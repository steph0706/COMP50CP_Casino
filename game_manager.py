"""

    game_manager.py

    This is a generic manager class for a specified game module
    to manage the rooms and users playing the game

"""
import socket
import sys
import select
import threading
import json
import room
import time
import generic_game
import blackjack
import roulette
import baccarat
from Queue import *

class Game_manager:
    def __init__(self, game):
        """
        function initializes room list and user set and socket
        also initializes self_lock, which locks self because it's both
        listening to the room and the server

        game - the name of the game callback module that game_manager
               will use when creating a room
        """
        print("Making game manager")
        self.SERVER    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users     = {} # dict: user -> idx of room they're in
        self.rooms     = [] # each room is a 'tuple' in list form:
                            # ie: [room, size] where first idx  == room
                            #                        second idx == curr_size
        self.name      = game # name of game
        self.cap       = 5
        self.room_msgs = Queue()
        self.self_lock = threading.Lock()
        self.MESSAGES  = {
            'name'          : Game_manager.get_name,
            'join'          : Game_manager.join_room,
            'bet'           : Game_manager.handle_bet,
            'continue'      : Game_manager.update_money,
            'quit'          : Game_manager.remove_user,
            'quit-game'     : Game_manager.remove_user,
            'bjack-move'    : Game_manager.blackjack_move,
        }

        # edit this mapping once the games are implemented
        self.game_map = {
            'blackjack' : blackjack.blackjack,
            'roulette'  : roulette.roulette,
            'baccarat'  : baccarat.baccarat
        }

    def connect_to_casino(self, ip_addr, port):
        """
        function connects game_manager to casino and continuously listens
        to messages from casino; also spawns thread that listens for
        messages from rooms
        """
        print("Connecting to casino")
        self.SERVER.connect((ip_addr, port))
        threading.Thread(target=self.listen_for_room).start()

        while True:
            self.self_lock.acquire()
            read_sockets, _, _ = select.select([self.SERVER], [], [], 0.01)

            # if no socket is found, release lock and loop again
            if len(read_sockets) == 0:
                if self.self_lock.locked():
                    self.self_lock.release()

            # only enter here if some socket is found
            for socks in read_sockets:
                if socks == self.SERVER:

                    # give server 0.1 seconds to send message, else
                    # terminate receive
                    m_list = []
                    recv = threading.Thread(target=self.receive_message,
                        args=(socks, m_list))
                    recv.start()
                    recv.join(0.1)

                    # loop through message and lock self only when needed
                    message = ''
                    self.self_lock.release()
                    for message in m_list:
                        self.self_lock.acquire()
                        print(message)
                        try:
                            message = json.loads(message)
                            user = message[1] if len(message) > 1 else None
                            money = message[2] if len(message) > 2 else None
                            betsize = message[3] if len(message) > 3 else None
                            beton = message[4] if len(message) > 4 else None
                            fun_name = self.MESSAGES[message[0]]
                            self.self_lock.release()
                            fun_name(self, user, money, betsize, beton)
                        except Exception, e:
                            print("Exception caught in listening to casino")
                            print str(e)
                            print(message)
                            print(type(message))
                            self.self_lock.release()

        self.SERVER.close()

    # receive message with time constraint
    def receive_message(self, sock, message):
        """
        receives messages from socket (most likely server) and appends
        them to the message list

        since every message is separated by the '\0' character, we need
        to split by '\0' or we might accidentally concatenate 2+ messages
        """
        m = ''
        msgs = sock.recv(4096).split("\0")
        for m in msgs:
            if m != '' and m != "\0":
                message.append(m)

    # check message queue from rooms continuously
    def listen_for_room(self):
        """
        listen for messages from room by checking a message queue
        and send any message from room back to server
        """
        while True:
            self.self_lock.acquire()

            # print message then send to server
            # with game name appended to the end
            if not self.room_msgs.empty():
                message = self.room_msgs.get()
                print(message) # debugging print to see message
                self.SERVER.send(json.dumps(message + [self.name]) + "\0")
            self.self_lock.release()

    def get_name(self, user, money, betsize, beton):
        """
        get game name and send it to server. Only games with recognized
        name will be allowed to connect to server (in our case, the names
        are blackjack, roulette, baccarat)
        """
        print("sending name to server")
        self.self_lock.acquire()
        self.SERVER.send(self.name + "\0")
        self.self_lock.release()

    def blackjack_move(self, user, move, betsize, beton):
        """
        function to handle blackjack turn, as it's more complex than the
        other 2 games
        """
        self.self_lock.acquire()
        self.rooms[self.users[user]][0].blackjackMove(user, move)
        self.self_lock.release()

    def join_room(self, user, money, betsize, beton):
        """
        adds user to the room with the minimum number of people to prevent
        starvation

        increments the room size when we add a user such that we only have
        maximum self.cap (5 in this case) users in a room
        """
        print("adding user " + user + " to a room")
        self.self_lock.acquire()

        idx = self.get_min_room()
        if idx != -1:
            rm = self.rooms[idx]
            rm[1] += 1
            t = threading.Thread(target=rm[0].addToRoom, 
                                 args=([user, money],))
            t.start()
            self.users[user] = idx
        else:
            new_room = room.Room(self.game_map[self.name], self.room_msgs)

            t = threading.Thread(target=new_room.addToRoom, 
                                     args=([user, money],))
            t.start()
            self.rooms.append([new_room, 1])
            self.users[user] = len(self.rooms) - 1

        for rm in self.rooms:
            rm[0].printRoom()

        self.self_lock.release()
        print("release lock in join")

    def get_min_room(self):
        """
        returns index of room with minimum number of people
        if every room is filled, return -1
        """
        curr_min = self.cap
        min_idx = -1
        for idx, rm in enumerate(self.rooms):
            if rm[1] < curr_min:
                curr_min = rm[1]
                min_idx = idx
        return min_idx

    def handle_bet(self, user, money, betsize, beton):
        """
        set the bet placed by a user and send it to the room they're in
        """
        self.self_lock.acquire()
        self.rooms[self.users[user]][0].setBet([user, betsize, beton])
        self.self_lock.release()

    def update_money(self, user, money, betsize, beton):
        """
        update money of user and send it to room
        then notify room that the number of users that have finished
        updating has increated by 1
        """
        print("updating user " + user + " money")
        self.self_lock.acquire()
        self.rooms[self.users[user]][0].updateMoney(user, money)
        self.rooms[self.users[user]][0].setUpdate()
        self.self_lock.release()

    def remove_user(self, user, money, betsize, beton):
        """
        removes a user from room and from the list of users in
        game_manager
        """
        print("removing user " + user + " from a room")
        self.self_lock.acquire()
        rm = self.rooms[self.users[user]]
        rm[0].removeUser(user)
        rm[1] -= 1

        self.users.pop(user)
        self.self_lock.release()
