import socket
import sys
import select
import threading
import json
import room
import time
import generic_game
from Queue import *

class Game_manager:
    def __init__(self, game):
        print("Making game manager")
        self.SERVER    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users     = {}
        self.rooms     = []
        self.name      = game
        self.cap       = 5
        self.room_msgs = Queue()
        self.self_lock = threading.Lock()
        self.MESSAGES  = {
            'name'   : Game_manager.get_name,
            'join'   : Game_manager.join_room,
            'bet'    : Game_manager.handle_bet,
            'remove' : Game_manager.remove_user
        }

    def connect_to_casino(self, ip_addr, port):
        print("Connecting to casino")
        self.SERVER.connect((ip_addr, port))
        threading.Thread(target=self.listen_for_room).start()

        loop_counter = 0
        while True:
            self.self_lock.acquire()
            loop_counter += 1
            print("server loop " + str(loop_counter))
            read_sockets, _, _ = select.select([self.SERVER], [], [], 1)
            # read_sockets = []
            # select_read = threading.Thread(target=self.select_server,
            #                 args=(self.SERVER, read_sockets))
            # select_read.start()
            # select_read.join(2)
            # if len(read_sockets) == 0:
            #     print("connected to server in loop " + str(loop_counter))
            #     self.self_lock.release()
            #     print("release lock in server " + str(loop_counter))

            print("connected to server in loop " + str(loop_counter))

            if len(read_sockets) == 0:
                print("release lock in server " + str(loop_counter))
                self.self_lock.release()
                print("release lock in server " + str(loop_counter))
            #for socks in read_sockets[0]:
            for socks in read_sockets:
                print("enter reading in loop " + str(loop_counter))
                if socks == self.SERVER:
                    m_list = []
                    #t1 = time.time()
                    recv = threading.Thread(target=self.receive_message,
                        args=(socks, m_list))
                    recv.start()

                    # while (time.time() - t1 <= 0.2):
                    #     continue

                    recv.join(0.1)

                    message = ''
                    if len(m_list) == 0:
                        self.self_lock.release()
                        continue
                    else:
                        message = m_list[0]
                        print(message)
                    # message = socks.recv(4096)
                    # print(message)
                    try:
                        message = json.loads(message)
                        user     = message[1] if len(message) > 1 else None
                        money    = message[2] if len(message) > 2 else None
                        betsize  = message[3] if len(message) > 3 else None
                        beton    = message[4] if len(message) > 4 else None
                        fun_name = self.MESSAGES[message[0]]
                        self.self_lock.release()
                        print("release lock in server " + str(loop_counter))
                        fun_name(self, user, money, betsize, beton)
                    except:
                        print("Exception caught")
                        print(message)
                        print(type(message))
                        self.self_lock.release()
                        print("release lock in server " + str(loop_counter))

        self.SERVER.close()

    def select_server(self, server, read_sockets):
        read_socket, _, _ = select.select([server], [], [])
        read_sockets.append(read_socket)

    def receive_message(self, sock, message):
        print("trying to receive message from server")
        m = ''
        m = sock.recv(4096)
        if m != '':
            message.append(m)
        print("received message from server")

    def listen_for_room(self):
        loop_counter = 0
        while True:
            self.self_lock.acquire()
            loop_counter += 1
            print("room loop " + str(loop_counter))
            if not self.room_msgs.empty():
                message = self.room_msgs.get()
                print(message)
                if message[0] != 'betset':
                    self.SERVER.send(json.dumps(message + [self.name]))
            self.self_lock.release()
            print("release lock in room loop " + str(loop_counter))

    def get_name(self, user, money, betsize, beton):
        print("sending name to server")
        self.self_lock.acquire()
        self.SERVER.send(self.name)
        self.self_lock.release()

    def join_room(self, user, money, betsize, beton):
        print("adding user " + user + " to a room")
        self.self_lock.acquire()
        for idx, rm in enumerate(self.rooms):
            if rm.size() < self.cap:
                while rm.roomBusy:
                    pass
                rm.addToRoom([user, money])
                self.users[user] = idx
                break
        else:
            new_room = room.Room(generic_game.gen_game, self.room_msgs)
            new_room.addToRoom([user, money])
            self.rooms.append(new_room)
            self.users[user] = len(self.rooms) - 1

        for rm in self.rooms:
            rm.printRoom()

        self.self_lock.release()
        print("release lock in join")

    def handle_bet(self, user, money, betsize, beton):
        self.self_lock.acquire()
        self.rooms[self.users[user]].setBet([user, betsize, beton])
        self.self_lock.release()

    def remove_user(self, user, money, betsize, beton):
        print("removing user " + user + " from a room")
        self.self_lock.acquire()
        rm = self.rooms[users[user]]
        if rm.hasUser(user):
            while rm.roomBusy:
                pass
            rm.removeUser(user)

        self.users.pop(user)
        self.self_lock.release()
