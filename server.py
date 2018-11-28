import socket
import sys
import threading
import json
from Queue import *
import game_server

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
INIT_MONEY = 1000

###########################################################################
# init loop functions
def init_game_servers(games, game_queue, users):
    print("Initializing games")
    game_set = set(['blackjack', 'roulette', 'baccarat'])
    while len(games) < 1:
        conn, addr = SERVER.accept()
        print(conn)
        print(addr)
        print("Accepted game")
        conn.send(json.dumps(['name']))
        name = conn.recv(4096)
        if name not in game_set:
            sys.stderr.write("Unrecognized game")
        else:
            games[name] = [conn]
            game_listen = threading.Thread(target=listen_for_game,
                          args=(games, name, conn, game_queue, users))
            game_listen.start()
            print(name)

def init_user_loop(games, users, users_lock, usr_queue):
    # adds user -> address to users dict
    while True:
        name = ''
        game = ''
        conn, addr = SERVER.accept()

        print("got user")
        conn.send(json.dumps(["name", "What is your name?"]))
        while True:
            try:
                name = conn.recv(4096)[0:-1]
                if name not in users:
                    users_lock.acquire()
                    users[name] = [conn, INIT_MONEY]
                    users_lock.release()
                    print(name + " connected")
                    break
                else:
                    # TODO fix this to force user to enter unique name
                    while True:
                        conn.send(json.dumps(["name", 
                        "Sorry, name is taken, try again."]))
                        try:
                            name = conn.recv(4096)[0:-1]
                            if name not in users:
                                break
                        except:
                            print("Not able to receive name")
                            pass

                    users_lock.acquire()
                    users[name] = [conn, INIT_MONEY]
                    users_lock.release()
                    print(name + " connected")
            except:
                print("exception caught in user registration")
                pass

        # add game to dict
        print("sending game choice to user")
        conn.send(json.dumps(['game',
            "Which game do you want to join? Baccarat, Blackjack, " \
                  + "or Roulette?"]))
        while True:
            try:
                game = conn.recv(4096).lower()[0:-1]
                if game == 'baccarat':
                    conn.send("Joined Baccarat!")
                    break
                elif game == 'blackjack':
                    conn.send("Joined Blackjack!")
                    break
                elif game == 'roulette':
                    conn.send("Joined Roulette!")
                    break
                else:
                    conn.send(json.dumps(['game', 
                              "Invalid option. Please choose between " \
                              + "Baccarat, Blackjack, or Roulette."]))
            except:
                continue

        msg_from_user_to_game(games, game, \
                        ['join', name, users[name][1], None, None])
        users_lock.acquire()
        users[name].append(game)
        users_lock.release()
        
        user_listen = threading.Thread(target=listen_for_user, 
                                       args=(users, users_lock, name, conn, 
                                             usr_queue))
        user_listen.start()

###########################################################################
# message sending functions
def msg_from_user_to_game(games, game, message):
    proper_msg = set(['join', 'quit', 'bet']) # add more msg later
    if message[0] not in proper_msg:
        print("Invalid message")
        return

    if game not in games:
        print("Invalid game")
        return
    
    print(message)
    print(type(message))
    print("Sending message to " + str(games[game][0]))
    games[game][0].send(json.dumps(message))

def listen_for_game(games, name, conn, game_queue, users):
    actions = {
        'users'  : print_users,
        'bet'    : ask_for_bet,
        'result' : broadcast_result
    }
    while True:
        try:
            message = json.loads(conn.recv(4096))
            if message:
                print("Message from game: " + json.dumps(message))
                actions[message[0]](message[1:], users)
        except:
            continue

def listen_for_user(users, users_lock, name, conn, usr_queue):
    while True:
        try:
            message = json.loads(conn.recv(4096))
            if message:
                usr_queue.put(message)
            else:
                users_lock.acquire()
                users.pop(name)
                users_lock.release()
        except:
            continue

###########################################################################
# message handling functions
def print_users(users_list, users):
    print(users_list, users)

def ask_for_bet(details, users):
    print("sending bet instructions to " + str(users[details[0]][0]))
    try:
        users[details[0]][0].send(json.dumps(['bet'] + details))
    except:
        users[details[0]][0].close()
        users.pop(details[0])

def broadcast_result(details, users):
    participants = details[0][0] + details[0][1]
    print("participants: " + json.dumps(participants))

    for p in participants:
        users[p[0]][1] += int(p[1])
        message = " won "
        if p[1] < 0:
            message = " lost "
        try:
            print(['result', "You" + str(message) \
                        + str(abs(p[1])) + ". Your total is now " \
                        + str(users[p[0]][1])])
            users[p[0]][0].send(json.dumps(['result', "You" + str(message) \
                        + str(abs(p[1])) + ". Your total is now " \
                        + str(users[p[0]][1])]))
        except:
            users[p[0]][0].close()
            users.pop(p[0])

# def broadcast(message, users_lock, users):
#     with users_lock:
#         for user, data in users.iteritems():
#             try:
#                 data[0].send(message)
#             except:
#                 data[0].close()
#                 users.pop(user)

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
    
    while game_loop.is_alive():
        continue
    
    user_loop = threading.Thread(target=init_user_loop, 
                                 args=(games, users, users_lock,
                                       usr_queue))
    user_loop.start()
    while True:
        if usr_queue.empty():
            continue
        else:
            message = usr_queue.get()
            game_name = message[-1]
            msg_from_user_to_game(games, game_name, message)


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