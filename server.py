import socket
import select
import sys
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
# ROULETTE_SERVER.connect((IP_ADDRESS, ROULETTE_PORT))

list_of_clients = []
list_of_users = []

def clientthread(conn, addr):
    conn.send("What is your name?")
    name = ""
    while True:
        try:
            name = conn.recv(2048)
            if name not in list_of_users:
                """
                    every person is kept as a tuple of its socket, the game they
                    are in and the amount of cash they have
                """
                list_of_users.append((conn, name, None, INIT_CASH))
                break
            else:
                conn.send("Sorry, name is already taken, try again.")
        except:
            continue

    conn.send("Which game do you want to join? Poker, Blackjack, or Roulette")
    game_server = None
    while True:
        try:
            game = conn.recv(2048).lower()[0:-1]
            if game == 'poker':
                idx = list_of_users.index((conn, name, None, INIT_CASH))
                list_of_users[idx] = (conn, name, 'poker', INIT_CASH)
                game_server = POKER_SERVER
                conn.send('Joined Poker!')
                break
            elif game == 'blackjack':
                idx = list_of_users.index((conn, name, None, INIT_CASH))
                list_of_users[idx] = (conn, name, 'blackjack', INIT_CASH)
                game_server = BLACKJACK_SERVER
                conn.send('Joined Blackjack!')
                break
            elif game == 'roulette':
                idx = list_of_users.index((conn, name, None, INIT_CASH))
                list_of_users[idx] = (conn, name, 'roulette', INIT_CASH)
                game_server = ROULETTE_SERVER
                conn.send('Joined Roulette!')
                break
            else:
                conn.send(
                    "Error, you must pick either Poker, Blackjack or Roulette")
        except:
            continue

    listen(conn, game_server, name)

def listen(conn, game_server, username):
    # possible input streams
    sockets_list = [conn, game_server]

    while True:
        try:
            # find sockets that are ready to be read from
            read_sockets ,write_socket, error_socket = select.select(
                sockets_list,[],[])

            for socks in read_sockets:
                if socks == game_server:
                    # received message from game to send to user
                    message = socks.recv(2048)
                    conn.send(message)
                elif socks == conn:
                    # user sent message, now send to game server
                    message = socks.recv(2048)
                    game_server.send((username, message))
                else:
                    remove(conn)
        except: continue

# def broadcast(message, connection):
#     for clients in list_of_clients:
#         if clients!=connection:
#             try:
#                 clients.send(message)
#             except:
#                 clients.close()
#                 remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = SERVER.accept()
    list_of_clients.append(conn)
    print addr[0] + " connected"

    start_new_thread(clientthread,(conn,addr))

conn.close()
# BLACKJACK_SERVER.close()
# POKER_SERVER.close()
# ROULETTE_SERVER.close()
SERVER.close()