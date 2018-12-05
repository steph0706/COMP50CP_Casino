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

                    # give server 0.1 seconds to send over, after that
                    # terminate receive
                    m_list = []
                    recv = threading.Thread(target=self.receive_message,
                        args=(socks, m_list))
                    recv.start()
                    recv.join(0.1)

                    # if no message found loop back to beginning
                    message = ''
                    if len(m_list) == 0:
                        self.self_lock.release()
                        # continue
                    else:
                        for message in m_list:
                            print(message)
                            try:
                                message = json.loads(message)
                                user     = message[1] if len(message) > 1 else None
                                money    = message[2] if len(message) > 2 else None
                                betsize  = message[3] if len(message) > 3 else None
                                beton    = message[4] if len(message) > 4 else None
                                fun_name = self.MESSAGES[message[0]]
                                self.self_lock.release()
                                fun_name(self, user, money, betsize, beton)
                            except Exception, e:
                                print("Exception caught")
                                print str(e)
                                print(message)
                                print(type(message))
                                self.self_lock.release()

        self.SERVER.close()

    # receive message with time constraint
    def receive_message(self, sock, message):
        m = ''
        msgs = sock.recv(4096).split("\0")
        for m in msgs:
            if m != '':
                message.append(m)

    # check message queue from rooms continuously
    def listen_for_room(self):
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
        print("sending name to server")
        self.self_lock.acquire()
        self.SERVER.send(self.name + "\0")
        self.self_lock.release()

    def blackjack_move(self, user, move, betsize, beton):
        self.self_lock.acquire()
        self.rooms[self.users[user]][0].blackjackMove(user, move)
        self.self_lock.release()

    # when adding user to room, increment the size of the room in self.rooms
    # so we don't get locked by the roomLock, and check this size to see
    # whether room is actually full
    def join_room(self, user, money, betsize, beton):
        print("adding user " + user + " to a room")
        self.self_lock.acquire()
        for idx, rm in enumerate(self.rooms):
            if rm[1] < self.cap:
                rm[1] += 1
                t = threading.Thread(target=rm[0].addToRoom, 
                                     args=([user, money],))
                t.start()
                self.users[user] = idx
                break
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

    # each user sets the bet they made according to the specified game
    def handle_bet(self, user, money, betsize, beton):
        print "handle bet"
        self.self_lock.acquire()
        print "lock acquired"
        self.rooms[self.users[user]][0].setBet([user, betsize, beton])
        self.self_lock.release()


    # update money by changing money of user in room
    # and then increment the number of users updated using setUpdate()
    def update_money(self, user, money, betsize, beton):
        print("updating user " + user + " money")
        self.self_lock.acquire()
        self.rooms[self.users[user]][0].updateMoney(user, money)
        self.rooms[self.users[user]][0].setUpdate()
        self.self_lock.release()

    # remove by removing the user from room
    # and from the user list in self.users
    def remove_user(self, user, money, betsize, beton):
        print("removing user " + user + " from a room")
        self.self_lock.acquire()
        rm = self.rooms[self.users[user]]
        rm[0].removeUser(user)
        rm[1] -= 1

        self.users.pop(user)
        self.self_lock.release()
