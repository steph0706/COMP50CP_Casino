import json
import roulette_server
import socket
import select
import room
from Queue import *

class Game_manager:
    global get_name, join_room, remove_user, game_fun, update_bet

    def __init__(self, game):
        print("Making game manager")
        self.games = {
            'roulette'  : roulette_server,
            'blackjack' : None,
            'baccarat'  : None
        }
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users  = set()
        self.rooms  = []
        self.name   = game
        self.r_cap  = 5
        self.msgQueue = Queue()
        self.MESSAGES = {
            'name'   : get_name,
            'join'   : join_room,
            'remove' : remove_user,
            'bet'    : update_bet
        }

    def get_name(self, user, money, betsize, beton):
        print("sending name to server")
        self.SERVER.send(self.name)


    def update_bet(self, user, money, betsize, beton):
        for room in rooms:
            if room.contains(user):
                # do something
                x=1

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
                    beton   = message[4] if len(message) > 4 else None
                    fun_name = self.MESSAGES[message[0]]
                    fun_name(self, user, money, betsize, beton)

        self.SERVER.close()


    def join_room(self, user, money, betsize, beton):
        print("adding user " + user + " to a room")
        self.users.add(user)
        for rm in self.rooms:
            if rm.size() < self.r_cap:
                rm.addToRoom([user, money, betsize])
                break
        else:
            new_room = room.Room(self.games[self.name], self.msgQueue)
            new_room.addToRoom([user, money, betsize])
            self.rooms.append(new_room)

        for rm in self.rooms:
            rm.printRoom()

    def remove_user(self, user, money, betsize, beton):
        print("removing user " + user + " from a room")
        self.users.remove(user)
        for rm in self.rooms:
            if rm.hasUser(user):
                rm.removeUser(user)
                break

    def game_fun():
        for room in self.rooms:
            room.waitForMinPlayers()
            while True:
                if self.msgQueue.empty():
                    continue
                else:
                    user, msg = self.msgQueue.get()
                    self.SERVER.send(json.dumps(['send', user, msg]))

        return True

