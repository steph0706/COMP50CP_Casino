import socket
import sys
import select
import threading
import json

class Game_manager:
    global get_name, join_room, remove_user

    def get_name(self, user, money, betsize):
        print("sending name to server")
        self.SERVER.send(self.name)

    def join_room(self, user, money, betsize):
        print("adding user " + user + " to a room")
        self.users.add(user)
        #for room in rooms:
            # add code after rooms have been implemented
            #if room.cap() < ROOM_CAP:
            #   room.add(user, money)
            # return True
        #new_room = NEW ROOM OBJECT
        #new_room.add(user, money)
        #rooms.append(new_room)
        #return True

    def remove_user(self, user, money, betsize):
        print("removing user " + user + " from a room")
        self.users.remove(user)
        #for room in rooms:
            # add code after rooms have been implemented
            # if room.has(user) == True:
            #   room.remove(user)
            #   return True

    def __init__(self, game):
        print("Making game manager")
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users  = set()
        self.rooms  = []
        self.name   = game
        self.r_cap  = 5
        self.MESSAGES = {
            'name'   : get_name,
            'join'   : join_room,
            'remove' : remove_user
        }

    def connect_to_casino(self, ip_addr, port):
        print("Connecting to casino")
        self.SERVER.connect((ip_addr, port))
        
        while True:
            read_sockets, _, _ = select.select([self.SERVER], [], [])

            for socks in read_sockets:
                if socks == self.SERVER:
                    message = json.loads(socks.recv(2048))
                    print(message)
                    user    = message[1] if len(message) > 1 else None
                    money   = message[2] if len(message) > 2 else None
                    betsize = message[3] if len(message) > 3 else None
                    fun_name = self.MESSAGES[message[0]]
                    fun_name(self, user, money, betsize)

        self.SERVER.close()