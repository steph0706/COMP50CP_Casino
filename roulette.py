import socket
import select
import sys
from thread import *
import threading
from RouletteRoom import RouletteRoom

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_ADDRESS = str(sys.argv[1])
ROULETTE_PORT = 8083

SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind((IP_ADDRESS, ROULETTE_PORT))
SERVER.listen(100)

CASINO_SERVER = None

list_of_users = {}
users_to_bets = {}
rooms = []
list_of_users_lock = threading.Lock()

# def ask_for_bet():
bet_msg = "Bet on it landing on an even number by typing 'even'\n" \
            + "Bet on an odd number by typing 'odd'\n" \
            + "Bet on it landing on a number between 0 and 12 by typing " \
            + "'1-3'\n" \
            + "Bet on it landing on a number between 13 and 25 by typing " \
            + "'2-3'\n" \
            + "Bet on it landing on a number between 26 and 36 by typing "
            + "'3-3'\n" \
            + "Bet on it landing on a specific number by typing the " \
            + "'betnum'\n" \
            +" Type 'low' to bet between 0 and 18, and type 'high' to bet " \
            + "higher than 18\n" \
            + "Place your what you're betting on followed by a space and how " \
            + "much you're betting: "
    # names = [user for user, val in list_of_users.items()]
    # CASINO_SERVER.send(bet_msg, names)

def roll(users):
    landon = random.randint(0, 36)
    losers = []
    winners = []
    if landon % 2 == 0:
        for user in users:
            if user[1] == 'even':
                winners.append(user[0])
            elif user[1] == 'odd':
                losers.append(user[0])
    if landon % 2 != 0:
        for user in users:
            if user[1] == 'odd':
                winners.append(user[0])
            elif user[1] == 'even':
                losers.append(user[0])
    if landon > 0 and landon <= 12:
        for user in users:
            if user[1] == '1-3':
                winners.append(user[0])
            elif user[1] == '2-3' or user[1] == '3-3':
                losers.append(user[0])
    if landon > 13 and landon <= 25:
        for user in users:
            if user[1] == '2-3':
                winners.append(user[0])
            elif user[1] == '3-3' or user[1] == '1-3':
                losers.append(user[0])
    if landon > 25 and landon <= 36:
        for user in users:
            if user[1] == '3-3':
                winners.append(user[0])
            elif user[1] == '1-3' or user[1] == '2-3':
                losers.append(user[0])
    if landon < 19:
        for user in users:
            if user[1] == 'low':
                winners.append(user[0])
            elif user[1] == 'high':
                losers.append(user[0])
    else:
        for user in users:
            if user[1] == 'high':
                winners.append(user[0])
            elif user[1] == 'low':
                losers.append(user[0])
    for user in users:
        if user[1] == 'betnum':
            if user[3] == landon:
                winners.append(user[0])
            else:
                losers.append(user[0])
    return winners, losers

def listen_thread(conn, addr):
    # conn.send("Welcome to roulette!")
    sockets_list = [sys.stdin, CASINO_SERVER]
    while True: 
        read_sockets,write_socket, error_socket = select.select(
            sockets_list,[],[])

        for socks in read_sockets:
            if socks == CASINO_SERVER:
                # msg from server, adding user
                message = socks.recv(4096).split()
                if message[0] == 'JOIN':
                    list_of_users_lock.acquire()
                    list_of_users[message[1]] = message[2]
                    print message
                    list_of_users_lock.release()
                    CASINO_SERVER.send(bet_msg + "###" + message[1])
                else:
                    name = message[0]
                    bet_on = message[1]
                    bet_size = int(message[2])
                    
                    list_of_users_lock.acquire()
                    if list_of_users[name] < bet_size:
                    list_of_users_lock.release()  
                        CASINO_SERVER.send(
                            "Bet amount is more than the amount of money " \
                            + "you have right now, try again" + "###" + name)
                        break

                    bet_num = None
                    if len(message) > 3:
                        bet_num = int(message[3])
                    
                    added = False
                    for i in range(0, len(rooms)):
                        if rooms[i].roomSize() < 5:
                            rooms[i].addToRoom(
                                (name, bet_on, bet_size, bet_num))
                            added = True
                    if not added:
                        newRoom = RouletteRoom()
                        newRoom.addToRoom((name, bet_on, bet_size, bet_num))
                        rooms.append(newRoom)
                        newRoom.waitForMinPlayers(roll)
            else:
                message = socks.recv(2048)

def game_thread():
    while True:
        for room in rooms:
            print "waiting for room"
            winners, losers = room.waitForMinPlayers(roll)

while True:
    conn, addr = SERVER.accept()
    print addr[0] + " connected"
    CASINO_SERVER = conn

    game_thread = threading.Thread(target = game_thread, args = [])
    game_thread.start()
    start_new_thread(listen_thread,(conn,addr))
    

conn.close()
SERVER.close()
CASINO_SERVER.close()