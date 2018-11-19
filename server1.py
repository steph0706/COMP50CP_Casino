import socket
import select
import sys
import threading
from thread import *
  
if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
BLACKJACK_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
POKER_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ROULETTE_SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])
BLACKJACK_PORT = 8081
POKER_PORT = 8082
ROULETTE_PORT = 8083
INIT_CASH = 500

SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind((IP_ADDRESS, PORT))
SERVER.listen(100)

# BLACKJACK_SERVER.connect((IP_ADDRESS, BLACKJACK_PORT))
# POKER_SERVER.connect((IP_ADDRESS, POKER_PORT))
ROULETTE_SERVER.connect((IP_ADDRESS, ROULETTE_PORT))

# TODO: delete later
list_of_clients = []
list_of_users = {}
list_of_users_lock = threading.Lock()

def client_init(conn, addr):
    conn.send("What is your name? Maximum 10 characters, no spaces.")
    name = ""
    while True:
        try:
            name = conn.recv(2048)
            list_of_users_lock.acquire()
            if name not in list_of_users and len(name) < 11:
                """
                    every person is kept as a tuple of its socket, the game they
                    are in and the amount of cash they have
                """
                list_of_users[name] = (conn, None, INIT_CASH)
                list_of_users_lock.release()
                break
            else:
                conn.send(
                    "Sorry, name is already taken or too long, try again.")
                list_of_users_lock.release()
        except:
            list_of_users.release()
            continue
    
    conn.send("Which game do you want to join? Poker, Blackjack, or Roulette")
    game_server = ask_user_for_game(conn, list_of_users, name)

def ask_user_for_game(conn, list_of_users, name):
    while True:
        try:
            game = conn.recv(2048).lower()[0:-1]
            if game == 'poker':
                list_of_users_lock.acquire()
                list_of_users[name] = (conn, POKER_SERVER, INIT_CASH)
                list_of_users_lock.release()
                game_server = POKER_SERVER
                msg = 'JOIN' + " " +  name + " " + `INIT_CASH`
                # POKER_SERVER.send(msg)
                conn.send('Joined Poker!')
                return game_server
            elif game == 'blackjack':
                list_of_users_lock.acquire()
                list_of_users[name] = (conn, BLACKJACK_SERVER, INIT_CASH)
                list_of_users_lock.release()
                game_server = BLACKJACK_SERVER
                msg = 'JOIN' + " " +  name + " " + `INIT_CASH`
                # BLACKJACK_SERVER.send(msg)
                conn.send('Joined Blackjack!')
                return game_server
            elif game == 'roulette':
                list_of_users_lock.acquire()
                list_of_users[name] = (conn, ROULETTE_SERVER, INIT_CASH)
                list_of_users_lock.release()
                game_server = ROULETTE_SERVER
                msg = 'JOIN' + " " +  name + " " + `INIT_CASH`
                ROULETTE_SERVER.send(msg)
                conn.send('Joined Roulette!')
                return game_server
            elif game == 'quit' or game == '--q':
                return None
            else:
                conn.send(
                    "Error, you must pick either Poker, Blackjack or Roulette")
        except:
            continue


def broadcast(message, clients): 
    for name in clients: 
        try: 
            list_of_users_lock.acquire()
            client = list_of_users[name]
            list_of_users_lock.release()
            client.send(message) 
        except: 
            clients.close() 
            remove(clients) 

def listen():
    game_servers = [BLACKJACK_SERVER, POKER_SERVER, ROULETTE_SERVER]

    while True:
        try:
            list_of_users_lock.acquire()
            user_sockets_list = [val[0] for user, val in list_of_users.items()]
            list_of_users_lock.release()
            socket_list = user_sockets_list #+ game_servers
            print socket_list
            read_sockets ,write_socket, error_socket = select.select(
                socket_list,[],[])
            print "socket"
            print user_sockets_list
            
            for socks in read_sockets:
                print socks
                if socks in game_servers:
                    message = socks.recv(8192).split("###")
                    msg_text = message[0]
                    clients = message[1:]
                    broadcast(msg_text, clients)
                elif socks in user_sockets_list:
                    # client sent messsage
                    message = socks.recv(2048)

                    # find name of user who sent it by socket
                    name = [user for user,val in list_of_users.items() 
                        if val[0] == socks]
                    game_server = list_of_users[name][1]

                    game_server.send(name + " " + message)
                    print message
                elif socks != sys.stdin: 
                    remove(conn)
                else:
                    continue
            print "end of forloop"
        except KeyboardInterrupt: 
            sys.exit(0)
        except:
            print "execpting"
            continue

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = SERVER.accept()
    list_of_clients.append(conn)
    print addr[0] + " connected"

    start_new_thread(client_init,(conn,addr))
    listen_thread = threading.Thread(target = listen, args = [])
    listen_thread.start()
    listen_thread.join()


conn.close()
# BLACKJACK_SERVER.close()
# POKER_SERVER.close()
ROULETTE_SERVER.close()
SERVER.close()