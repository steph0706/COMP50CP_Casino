import threading

class RouletteRoom():
    def __init__(self):
        self.roomBusy = False
        self.roomLock = threading.Lock()
        self.roomAvailable = threading.Condition(self.roomLock)

        self.roomReadyLock = threading.Lock()
        self.roomReady = threading.Condition(self.roomReadyLock)

        self.room = []
        self.max = 5

    def addToRoom(self, user):
        with self.roomLock:
            while self.roomBusy:
                self.roomAvailable.wait()
            self.roomBusy = True
            room.append(user)
            if len(room) >= 2:
                self.roomReady.notify()

    def waitForMinPlayers(self, game_fun):
        with self.roomLock:
            while len(self.room) < 2:
                self.roomReady.wait()

            return game_fun(self.room)


    def roomBusy(self):
        return self.roomBusy

    def roomSize(self):
        with self.roomLock:
            return len(self.room)