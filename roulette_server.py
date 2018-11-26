import socket
import sys
import select
import threading
import json
from room import Room

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ROOM_CAP = 5

BET_MSG = "Bet on it landing on an even number by typing 'even'\n" \
            + "Bet on an odd number by typing 'odd'\n" \
            + "Bet on it landing on a number between 0 and 12 by typing " \
            + "'1-3'\n" \
            + "Bet on it landing on a number between 13 and 25 by typing " \
            + "'2-3'\n" \
            + "Bet on it landing on a number between 26 and 36 by typing " \
            + "'3-3'\n" \
            + "Bet on it landing on a specific number by typing the " \
            + "'betnum'\n" \
            +" Type 'low' to bet between 0 and 18, and type 'high' to bet " \
            + "higher than 18\n" \
            + "Place your what you're betting on followed by a space and how " \
            + "much you're betting: "

def connect_to_casino(ip_addr, port):
    users = set()
    rooms = []
    SERVER.connect((ip_addr, port))

    while True:
        read_sockets, _, _ = select.select([SERVER], [], [])

        for socks in read_sockets:
            if socks == SERVER:
                message = json.loads(socks.recv(2048))
                print 'msg: ' + message[0]
                user    = message[1]
                money   = message[2]
                betsize = message[3]
                MESSAGES[message[0]](users, user, rooms, money, betsize)
                SERVER.send(json.dumps(['users'] + list(users)))
    SERVER.close()

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

def join_room(users, user, rooms, money, betsize=None):
    users.add(user)
    # print "hello"
    # for room in rooms:
    #     if room.size() < ROOM_CAP:
    #         SERVER.send(json.dumps(['send_to_user', BET_MSG, user]))
    #         room.addToRoom((user, money))
    #     return True

    # new_room = Room(roll)
    # new_room.addToRoom((user, money))
    # rooms.append(new_room)
    # winners, losers = new_room.waitForMinPlayers()
    return True

def remove_user(users, user, rooms, money, betsize=None):
    users.remove(user)
    for room in rooms:
        # add code after rooms have been implemented
        # if room.has(user) == True:
        #   room.remove(user)
        #   return True
        x = 1
MESSAGES = {
    'join'   : join_room,
    'remove' : remove_user
    # add more msg later
}




