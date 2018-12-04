import threading
import time
from Queue import *

class Room:
    def __init__(self, game, msgs):
        self.roomLock = threading.Lock()
        self.msgs   = msgs
        self.bets   = Queue()
        self.room   = []
        self.game   = game
        self.update = 0
        self.curr_game = None
        self.game()

        start = threading.Thread(target=Room.waitForMinPlayers, args=(self,))
        start.start()


    def waitingMsg(self, user):
        if len(self.room) < 2:
            self.msgs.put(['wait', user[0], 
                'Waiting for more users to join the room\0'])
    
    def addToRoom(self, user):
        if self.roomLock.locked():
            self.msgs.put(['wait', user[0], 'Waiting for current game to '\
                                + "finish\0"])

        self.roomLock.acquire()
        self.msgs.put(['wait', user[0], 'Entering game room...\0'])
        self.room.append(user)
        self.roomLock.release()
        self.waitingMsg(user)

    def updateMoney(self, user, new_money):
        for u in self.room:
            if u[0] == user:
                u[1] = new_money
                break

    def removeUser(self, username):
        user_to_remove = []
        for user in self.room:
            if user[0] == username:
                user_to_remove = user
                break
        self.room.remove(user_to_remove)

    def printRoom(self):
        print("Room start")
        for user in self.room:
            print(user)
        print("Room end")

    # execute game once number of players >= 2
    def waitForMinPlayers(self):
        while True:
            time.sleep(0.01)
            if len(self.room) < 2:
                continue
            else:
                self.roomLock.acquire()
                self.printRoom() # debugging print to see who's in room

                curr_game = self.game()
                self.curr_game = curr_game

                # loops thru players so everyone can place bet
                for user in self.room:
                    bet_msg, possible_bet = curr_game.bet_message()

                    # put bet message in specified format on queue
                    self.msgs.put(['bet', user[0], user[1], 
                                    bet_msg, possible_bet])

                    for otherUser in self.room:
                        if otherUser != user:
                            self.msgs.put(['wait', otherUser[0], 'Waiting for '\
                                + user[0] + " to bet\0"])

                    user_bet = self.getBet()
                    curr_game.bet(user_bet[0], user_bet[1], user_bet[2])

                result = curr_game.play(self.msgs)
                self.msgs.put(['result', result])
                self.getUpdate()
                self.roomLock.release()

    # puts bet on bet queue
    def setBet(self, bet):
        self.bets.put(bet)

    # loops until something is on bet queue, then pop it off and return
    def getBet(self):
        while self.bets.empty():
            pass
        return self.bets.get()


    def blackjackMove(self, user, move):
        if move == 'hit':
            self.curr_game.start_hit(user)
        else:
            self.curr_game.stop_hit(user)


    # increment update count
    def setUpdate(self):
        self.update += 1

    # loops until all players in room has updated then return
    def getUpdate(self):
        while self.update < len(self.room):
            pass
        self.update = 0
        self.msgs.put(['debug', 'room done updating: len is', len(self.room)])