import socket
import select
import sys
from thread import *
import threading

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_ADDRESS = str(sys.argv[1])
ROULETTE_PORT = 8083

SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind((IP_ADDRESS, ROULETTE_PORT))
SERVER.listen(100)

list_of_users = {}
users_to_bets = {}
rooms = []
room_locks = []
queue = []
queue_lock = threading.Lock()
list_of_users_lock = threading.Lock()

def ask_for_bet():
    bet_msg = "Bet on it landing on an even number by typing 'even'\n\
Bet on an odd number by typing 'odd'\n\
Bet on it landing on a number between 0 and 12 by typing '1-3'\n\
Bet on it landing on a number between 13 and 25 by typing '2-3'\n\
Bet on it landing on a number between 26 and 36 by typing '3-3'\n\
Bet on it landing on a specific number by typing the 'betnum'\n\
Type 'low' to bet between 0 and 18, and type 'high' to bet higher than 18\n\
Place your what you're betting on followed by a space and how much you're \
betting: "
    names = [user for user, val in list_of_users.items()]
    SERVER.send(bet_msg, names)


def clientthread(conn, addr):
    # conn.send("Welcome to roulette!")
    sockets_list = [sys.stdin, SERVER]
    while True: 
        read_sockets,write_socket, error_socket = select.select(
            sockets_list,[],[])

        for socks in read_sockets:
            if socks == server:
                # msg from server, adding user
                message = socks.recv(4096).split()
                if message[0] == 'JOIN':
                    list_of_users_lock.acquire()
                    list_of_users[message[1]] = message[2]
                    list_of_users_lock.release()
                else:
                    name = message[0]
                    bet_on = message[1]
                    bet_size = int(message[2])
                    bet_num = None
                    if len(message) > 3:
                        bet_num = int(message[3])
                    
                    allLocked = all(room.locked() for room in room_locks)
                    if allLocked:
                        queue_lock.acquire()
                        queue.add((name, bet_on, bet_size, bet_num))
                        queue_lock.release()
                    else:
                        for i in range(0, len(rooms)):
                            if not room_locks[i].locked():
                                room_locks[i].acquire()
                                room[i].append(
                                    (name, bet_on, bet_size, bet_num))
                                room_locks[i].release()

                    users_to_bets[name] = (bet_on, bet_size, bet_num)      
            else:
                message = socks.recv(2048)

def roll(room_num):
    room_locks[room_num].acquire()

    landon = random.randint(0, 36)
    users = room[room_num]
    if landon % 2 == 0:
        for user in users():
            if user[1] == 'even':
                # send you win!
                print 'ha'
            elif user[1] == 'odd':
                # send you lose
                print 'ha'
    if landon % 2 != 0:
        for user in users():
            if user[1] == 'odd':
                # send you win!
                print 'ha'
            elif user[1] == 'even':
                # send you lose
                print 'ha'
    if landon > 0 and landon <= 12:
        for user in users():
            if user[1] == '1-3':
                # send you win!
                print 'ha'
            elif user[1] == '2-3' or user[1] == '3-3':
                # send you lose
                print 'ha'
    if landon > 13 and landon <= 25:
        for user in users():
            if user[1] == '2-3':
                # send you win!
                print 'ha'
            elif user[1] == '3-3' or user[1] == '1-3':
                # send you lose
                print 'ha'
    if landon > 25 and landon <= 36:
        for user in users():
            if user[1] == '3-3':
                # send you win!
                print 'ha'
            elif user[1] == '1-3' or user[1] == '2-3':
                # send you lose
                print 'ha'
    if landon < 19:
        for user in users():
            if user[1] == 'low':
                # send you win
                print 'ha'
            elif user[1] == 'high':
                # send you lose
                print 'ha'
    else:
        for user in users():
            if user[1] == 'high':
                # send you win
                print 'ha'
            elif user[1] == 'low':
                # send you lose
                print 'ha'
    for user in users():
        if user[1] == 'betnum':
            if user[3] == landon:
                # send you win
                print 'ha'
            else:
                # send you lose
                print 'ha'
    room_locks[room_num].release()


def room_thread(room_num):
    rooms[room_num].acquire()
    while len(rooms[room_num] < 2):
        rooms[room_num].release()

    rooms[room_num].release()
    roll(room_num)


while True:
    conn, addr = SERVER.accept()
    list_of_clients.append(conn)
    print addr[0] + " connected"

    start_new_thread(clientthread,(conn,addr))

conn.close()
SERVER.close()