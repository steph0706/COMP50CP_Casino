import socket
import select
import sys
from thread import *
 

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()

IP_ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])

SERVER.bind((IP_ADDRESS, PORT))
SERVER.listen(100)

list_of_clients = []
list_of_usernames = []

def clientthread(conn, addr):
    conn.send("What is your name?")
    while True:
        try:
            name = conn.recv(2048)
            if name not in list_of_usernames:
                list_of_usernames.append(name)
                break
            else:
                conn.send("Sorry, name is already taken, try again.")
        except:
            continue

    conn.send("Which game do you want to join? Poker, Blackjack, or Roulette")

    while True:
        try:
            game = conn.recv(2048).lower()[0:-1]
            print game
            if game == 'poker':
                conn.send('Joined poker!')
                break
            elif game == 'blackjack':
                conn.send('Joined blackjack')
                break
            elif game == 'roulette':
                conn.send('joined roulette')
                break
            else:
                conn.send("Error, you must pick either Poker, Blackjack or Roulette")
        except:
            continue

    while True:
        try:
            message = conn.recv(2048)
            if message:
                print  message
                message_to_send = message
                broadcast(message_to_send, conn)
            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)
        except:
            continue

def broadcast(message, connection):
    for clients in list_of_clients:
        if clients!=connection:
            try:
                clients.send(message)
            except:
                clients.close()

                # if the link is broken, we remove the client
                remove(clients)


def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
  
    """Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected"""
    conn, addr = SERVER.accept()
  
    """Maintains a list of clients for ease of broadcasting
    a message to all available people in the chatroom"""
    list_of_clients.append(conn)
 
    # prints the address of the user that just connected
    print addr[0] + " connected"

    # creates and individual thread for every user 
    # that connects
    start_new_thread(clientthread,(conn,addr))

conn.close()
SERVER.close()