import threading
from Queue import *

class Room:
    def __init__(self, game, msgs):
        self.roomBusy = False
        
        self.roomLock = threading.Lock()
        # self.roomAvailable = threading.Condition(self.roomLock)

        # self.roomReadyLock = threading.Lock()
        # self.roomReady = threading.Condition(self.roomReadyLock)

        self.msgs = msgs
        self.bets = Queue()
        self.room = []
        self.game = game
        self.game()

        start = threading.Thread(target=Room.waitForMinPlayers, args=(self,))
        start.start()

    def addToRoom(self, user):
        self.roomLock.acquire()
        self.room.append(user)
        self.roomLock.release()

    def hasUser(self, username):
        self.roomLock.acquire()
        for idx, user in enumerate(self.room):
            if username in user:
                self.roomLock.release()
                return idx
        self.roomLock.release()
        return ''

    def removeUser(self, username):
        idx = self.hasUser(username)
        if idx != '':
            self.roomLock.acquire()
            self.room.pop(idx)
            self.roomLock.release()

    def printRoom(self):
        print("Room start")
        for user in self.room:
            print(user)
        print("Room end")

    def waitForMinPlayers(self):
        while True:
            if len(self.room) < 2:
                continue
            else:
                self.roomLock.acquire()
                self.roomBusy = True

                curr_game = self.game()
                for user in self.room:
                    bet_msg, possible_bet = curr_game.bet_message()
                    self.msgs.put(['bet', user[0], user[1], bet_msg, possible_bet])
                    user_bet = self.getBet()
                    self.msgs.put(['betset', 'bet set by ' + str(user_bet[0])])
                    curr_game.bet(user_bet[0], user_bet[1], user_bet[2])

                result = curr_game.play()
                curr_game.reset()
                self.msgs.put(['result', result])
                self.roomLock.release()

    def setBet(self, bet):
        self.bets.put(bet)

    def getBet(self):
        while self.bets.empty():
            pass
        return self.bets.get()

    def size(self):
        self.roomLock.acquire()
        room_size = len(self.room)
        self.roomLock.release()
        return room_size