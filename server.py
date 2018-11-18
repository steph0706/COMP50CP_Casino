import socket
import sys
import threading
import json
from Queue import *

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def init_user_loop(users, msg_queue):
    # adds user -> address to users dict
    while True:
        print("listening for user")
        name = ''
        game = ''
        conn, addr = SERVER.accept()

        print("got user")
        conn.send("What is your name?")
        while True:
            try:
                name = conn.recv(2048)[0:-1]
                if name not in users:
                    users[name] = conn
                    print(name + " connected")
                    break
                else:
                    conn.send("Sorry, name is taken, try again.")
            except:
                continue

        # add game to dict
        conn.send("Which game do you want to join? Baccarat, Blackjack, " \
                  + "or Roulette?")
        while True:
            try:
                game = conn.recv(2048).lower()[0:-1]
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
                    conn.send("Invalid option. Please choose between " \
                              + "Baccarat, Blackjack, or Roulette.")
            except:
                continue
        users[name] = (conn, game)
        user_listen = threading.Thread(target=listen_for_user, 
                                       args=(users, name, conn, msg_queue))
        user_listen.start()

def listen_for_user(users, name, conn, msg_queue):
    while True:
        try:
            message = conn.recv(2048)
            if message:
                msg_queue.put((name, message))
            else:
                users.pop(name)
        except:
            continue

def broadcast(message, users, sender):
    for user, data in users.iteritems():
        if user != sender:
            try:
                data[0].send(sender + ": " + message)
            except:
                data[0].close()
                users.pop(user)

def server_loop():
    users = {}
    msg_queue = Queue()
    user_loop = threading.Thread(target=init_user_loop, 
                                 args=(users, msg_queue))
    user_loop.start()
    while True:
        if msg_queue.empty():
            continue
        else:
            sender, msg = msg_queue.get()
            broadcast(msg, users, sender)

def main(args):
    if len(args) != 3:
        sys.exit("Usage: script, IP address, port number")

    ip_addr = str(args[1])
    port    = int(args[2])

    SERVER.bind((ip_addr, port))
    SERVER.listen(100)

    server_loop()

if __name__ == '__main__':
    main(sys.argv)