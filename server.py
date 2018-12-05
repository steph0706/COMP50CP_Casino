import socket
import sys
import threading
import json
from Queue import *
import game_server
###########################################################################
# globals defined

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
INIT_MONEY = 1000
NUM_GAMES = 3 # edit this to change number of games needed to connect before
              # users can start connecting
BUFF_SIZE = 4096

###########################################################################
# init loop functions
def init_game_servers(games, game_queue, users):
    print("Initializing games")
    game_set = set(['blackjack', 'roulette', 'baccarat'])

    # accept recognized games
    while len(games) < NUM_GAMES:
        conn, addr = SERVER.accept()

        # debug prints
        print(conn)
        print(addr)
        print("Accepted game")

        # request game name by sending it to game_manager
        conn.send(json.dumps(['name']))
        name = conn.recv(BUFF_SIZE)[:-1]

        # if game is recognized, add to the game dict
        if name not in game_set:
            sys.stderr.write("Unrecognized game")
        else:
            games[name] = [conn]

            # start game_listen thread for each game
            game_listen = threading.Thread(target=listen_for_game,
                          args=(games, name, conn, game_queue, users))
            game_listen.start()
            print(name) # debug print

def init_user_loop(games, users, users_lock, usr_queue):
    while True:
        name = ''
        game = ''
        conn, addr = SERVER.accept()

        print("got user") # debug print

        get_user = threading.Thread(target=get_one_user_info,
            args=(games, users, users_lock, usr_queue, conn, addr))
        get_user.start()

def get_one_user_info(games, users, users_lock, usr_queue, conn, addr):
        # loops until user enters a unique name
        conn.send(json.dumps(["name", "What is your name?"]))
        while True:
            try:
                name = conn.recv(BUFF_SIZE)[0:-1]
                if name not in users:
                    users_lock.acquire()
                    users[name] = [conn, INIT_MONEY]
                    users_lock.release()
                    print(name + " connected")
                    break
                else:
                    while True:
                        conn.send(json.dumps(["name", 
                        "Sorry, name is taken, try again."]))
                        try:
                            name = conn.recv(BUFF_SIZE)[0:-1]
                            if name not in users:
                                break
                        except:
                            print("Not able to receive name")
                            pass

                    users_lock.acquire()
                    users[name] = [conn, INIT_MONEY]
                    users_lock.release()
                    print(name + " connected")
                    break
            except:
                print("exception caught in user registration")
                pass

        # loops until user enters a recognized game
        print("sending game choice to user")
        conn.send(json.dumps(['game',
            "Which game do you want to join? Baccarat, Blackjack, " \
                  + "or Roulette?"]))
        while True:
            try:
                msg = conn.recv(BUFF_SIZE).lower().split("\0")
                print "game: " + str(msg[0])
                game = msg[0][:-1]
                if game == 'baccarat':
                    conn.send(json.dumps(['print', None, "Joined Baccarat!"]) \
                        + "\0")
                    break
                elif game == 'blackjack':
                    conn.send(json.dumps(['print', None, "Joined Blackjack!"]) \
                        + "\0")
                    break
                elif game == 'roulette':
                    conn.send(json.dumps(['print', None, "Joined Roulette!"]) \
                        + "\0")
                    break
                else:
                    conn.send(json.dumps(['game', 
                              "Invalid option. Please choose between " \
                              + "Baccarat, Blackjack, or Roulette."]))
            except Exception, e:
                print str(e)
                continue

        # send message to game_manager to let user join 

        msg_from_user_to_game(users, users_lock, games, game, \
                        ['join', name, users[name][1], None, None])

        # lock users dict and add the game name the user is in
        users_lock.acquire()
        users[name].append(game)
        users_lock.release()
        
        user_listen = threading.Thread(target=listen_for_user, 
                                       args=(users, users_lock, name, conn, 
                                             usr_queue))
        user_listen.start()

###########################################################################
# message sending functions
def msg_from_user_to_game(users, users_lock, games, game, message):
    proper_msg = set(['join', 'bet', 'continue', 'switch', 'quit', \
        'bjack-move', 'quit-game'])
    if message[0] not in proper_msg:
        print("Invalid message")
        return

    # a 'switch' command is converted to quitting the game the user
    # is in, and joining a different game
    if message[0] == 'switch':
        message_quit = ['quit-game'] + message[1:]
        message_join = ['join'] + message[1:]

        # send quit and join to appropriate game_managers
        msg_from_user_to_game(users, users_lock, games, 
                    users[message[1]][2], message_quit)
        msg_from_user_to_game(users, users_lock, games,
                    game, message_join)
        users_lock.acquire()
        users[message[1]][2] = game
        users_lock.release()
        return
    if message[0] == 'quit':
        users_lock.acquire()
        print message[1] + " quitting"
        users.pop(message[1])
        users_lock.release()
   
    print(message) # debug print
    print(type(message)) # debug print
    print("Sending message to " + str(games[game][0])) # debug print
    games[game][0].send(json.dumps(message) + "\0")

# listen for messages from game and take appropriate action
def listen_for_game(games, name, conn, game_queue, users):
    actions = {
        'users'      : print_users,
        'bet'        : ask_for_bet,
        'wait'       : print_a_message,
        'result'     : broadcast_result,
        'bjack-deal' : blackjack_deal,
        'bjack-hit'  : blackjack_hit,
    }

    # continuously receives messages from game
    while True:
        try:
            messages = conn.recv(BUFF_SIZE).split("\0")
            print "game messages: " + str(messages)
            for m in messages:
                if m == "":
                    continue
                message = json.loads(m)
                if message:
                    print("Message from game: " + json.dumps(message))
                    actions[message[0]](message[1:], users)
        except Exception, e :
            print str(e)
            print 'didnt get message'
            continue

# listen for messages from user and adds to usr_queue
def listen_for_user(users, users_lock, name, conn, usr_queue):
    while True:
        try:
            messages = conn.recv(BUFF_SIZE).split("\0")
            for m in messages:
                if m == "":
                    continue
                message = json.loads(m)
                print "message from user:" + str(message)
                if message:
                    # adds message to the queue
                    usr_queue.put(message)
                else:
                    users_lock.acquire()
                    users.pop(name)
                    users_lock.release()
        except:
            continue

###########################################################################
# message handling functions

# debug print function
def print_users(users_list, users):
    print(users_list, users)

def ask_for_bet(details, users):
    print("sending bet instructions to " + str(users[details[0]][0]))
    try:
        users[details[0]][0].send(json.dumps(['bet'] + details) + "\0")
    except:
        users[details[0]][0].close()
        users.pop(details[0])

def blackjack_deal(details, users):
    user = details[0]
    cards = details[3]
    users[user][0].send(json.dumps(['bjack-cards', cards, user]) + "\0")

def blackjack_hit(details, users):
    user = details[0]
    card = details[3]
    users[user][0].send(json.dumps(['bjack-hit', card, user]) + "\0")

def print_a_message(details, users):
    print("sending printed message to " + str(users[details[0]][0]))
    try:
        users[details[0]][0].send(json.dumps(['print'] + details) + "\0")
    except:
        print("can't send printed instruction")
        users[details[0]][0].close()
        users.pop(details[0])

def broadcast_result(details, users):
    participants = details[0][0] + details[0][1]
    print("participants: " + json.dumps(participants))
    print "PRINTING RESULTS"
    msg = details[0][2]
    print msg
    for p in participants:
        users[p[0]][1] += int(p[1])
        message = " won " if p[1] >= 0 else " lost "
        msg_on_screen = msg + "You" + str(message) + str(abs(p[1])) \
                    + ". Your total is now " + str(users[p[0]][1])

        try:
            print "sending result"
            print(json.dumps(['result', p[0], msg_on_screen, 
                            users[p[0]][1], details[-1]])) # debug print
            users[p[0]][0].send(json.dumps(['result', p[0], msg_on_screen,
                            users[p[0]][1], details[-1]]) + "\0")
        except:
            print("send result to user exception") # debug print
            users[p[0]][0].close()
            users.pop(p[0])

###########################################################################
# main server loop
def server_loop(ip_addr, port):
    games = {}
    users = {}
    users_lock = threading.Lock()

    game_queue = Queue()
    usr_queue = Queue()

    game_loop = threading.Thread(target=init_game_servers,
                                 args=(games, game_queue, users))
    game_loop.start()
    
    # only start user_loop once all games are initialized
    while game_loop.is_alive():
        continue
    
    user_loop = threading.Thread(target=init_user_loop, 
                                 args=(games, users, users_lock,
                                       usr_queue))
    user_loop.start()

    # this loop continuously checks usr_queue and pop off messages
    # in order they were entered
    while True:
        if usr_queue.empty():
            continue
        else:
            message = usr_queue.get()
            game_name = message[-1]
            msg_from_user_to_game(users, users_lock,games, 
                                    game_name, message)


def main(args):
    if len(args) != 3:
        sys.exit("Usage: script, IP address, port number")

    ip_addr = str(args[1])
    port    = int(args[2])

    SERVER.bind((ip_addr, port))
    SERVER.listen(100)

    server_loop(ip_addr, port)

if __name__ == '__main__':
    main(sys.argv)