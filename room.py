import threading
import time
from Queue import *

class Room:
    def __init__(self, game, msgs):
        self.roomLock = threading.Lock()

        """ a list of messages to be sent to the server to deal with """
        self.msgs   = msgs

        """ a queue of bets """
        self.bets   = Queue()

        """ a list representing the room containing users """
        self.room   = []

        """ the game function to be played """
        self.game   = game
        """ stores the current game object """
        self.curr_game = None
        self.game()

        """ 
            keeps track of how many users have updated their result from the
            game
        """
        self.update = 0

        start = threading.Thread(target=Room.waitForMinPlayers, args=(self,))
        start.start()

    def waitingMsg(self, user):
        """ sends a waiting message to the user """
        if len(self.room) < 2:
            self.msgs.put(['wait', user[0], 
                'Waiting for more users to join the room'])
    
    def addToRoom(self, user):
        """
            waits for the current game in the room to finish and 
            adds a user to the room
        """
        if self.roomLock.locked():
            self.msgs.put(['wait', user[0], 'Waiting for current game to '\
                                + "finish"])
        self.roomLock.acquire()
        self.msgs.put(['wait', user[0], 'Entering game room...'])
        self.room.append(user)
        self.roomLock.release()
        self.waitingMsg(user)

    def updateMoney(self, user, new_money): 
        """
            updates a user's money in the user dictionary
        """
        for u in self.room:
            if u[0] == user:
                u[1] = new_money
                break

    def removeUser(self, username):
        """
            removes the user given by the username from the room
        """
        user_to_remove = []
        for user in self.room:
            if user[0] == username:
                user_to_remove = user
                break
        self.room.remove(user_to_remove)

    def printRoom(self):
        """
            prints the users in the room - for debugging purposes
        """
        print("Room start")
        for user in self.room:
            print(user)
        print("Room end")

    def waitForMinPlayers(self):
        """
            waits for the number of players in the room exceeds 2 and then executes
            the actual game play
        """
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
                                + user[0] + " to bet"])

                    user_bet = self.getBet()
                    curr_game.bet(user_bet[0], user_bet[1], user_bet[2])

                result = curr_game.play(self.msgs)
                self.msgs.put(['result', result])
                self.getUpdate()
                self.roomLock.release()


    def setBet(self, bet):
        """ puts bet on bet queue """
        self.bets.put(bet)

   
    def getBet(self):
        """ 
            loops until something is on bet queue, then pop it off and return 
        """
        while self.bets.empty():
            pass
        return self.bets.get()

    def blackjackMove(self, user, move):
        """ 
            if a user decides to hit in a blackjack game, notifies the play thread
            in the blackjack room to start the hitting/standing interaction
        """
        if move == 'hit':
            self.curr_game.start_hit(user)
        else:
            self.curr_game.stop_hit(user)

    def setUpdate(self):
        """ increments update count """
        self.update += 1

    def getUpdate(self):
        """ 
            loops until all players have updated from the result of the game
        """
        while self.update < len(self.room):
            pass
        self.update = 0
