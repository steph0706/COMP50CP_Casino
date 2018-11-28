import threading

class Room:
    def __init__(self, game_fun):
        self.roomBusy = False
        
        self.roomLock = threading.Lock()
        self.roomAvailable = threading.Condition(self.roomLock)

        self.roomReadyLock = threading.Lock()
        self.roomReady = threading.Condition(self.roomReadyLock)

        self.room = []
        self.max = 5

        self.game_fun = game_fun

    def addToRoom(self, user):
        with self.roomLock:
            while self.roomBusy:
                self.roomAvailable.wait()
            self.room.append(user)
            with self.roomReadyLock:
                if len(self.room) >= 2:
                    self.roomReady.notify()


    def waitForMinPlayers(self):
        with self.roomLock and self.roomReadyLock:
            while len(self.room) < 2:
                self.roomReady.wait()
            self.roomBusy = True
            return self.game_fun(self.room)

    def doneWithRoom(self):
        with self.roomLock:
            self.roomBusy = False
            self.roomAvailable.notify()

    def roomBusy(self):
        return self.roomBusy

    def size(self):
        with self.roomLock:
            return len(self.room)

    def hasUser(self, username):
        with self.roomLock:
            for idx, user in enumerate(self.room):
                if username in user:
                    return idx
        return ''

    def removeUser(self, username):
        idx = self.hasUser(username)
        if idx != '':
            with self.roomLock:
                self.room.pop(idx)

    def printRoom(self):
        print("Room start")
        for user in self.room:
            print(user)
        print("Room end")


