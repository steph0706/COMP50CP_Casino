import random

class roulette:
    def __init__(self):
        self.users = {}
        # do nothing
        # return True

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, beton]

    def bet_message(self):
        return "Place your bets! Before all your bets, please type " \
                    + "Bet on it landing on an even number by typing 'even'\n" \
                    + "Bet on an odd number by typing 'odd'\n" \
                    + "Bet on it landing on a number between 0 and 12 by " \
                    + "typing '1-3'\n" \
                    + "Bet on it landing on a number between 13 and 25 by " \
                    + "typing '2-3'\n" \
                    + "Bet on it landing on a number between 26 and 36 by " \
                    + "typing '3-3'\n" \
                    + "Bet on it landing on a specific number by typing the " \
                    + "number\n" \
                    +"Type 'low' to bet between 0 and 18, and type 'high' " \
                    + "to bet higher than 18\n", \
               ['even', 'odd', '1-3', '2-3', '3-3', 'high', 'low'] \
                + [str(i) for i in range(37)]

    def isInt(self, num):
        try:
            if int(num):
                return True
        except:
            return False

    def play(self, msgs):
        winners = []
        losers  = []
        landon = random.randint(0, 36)

        if landon % 2 == 0:
            for user, bet in self.users.iteritems():
                if bet[1] == 'even':
                    winners.append((user, bet[0]))
                elif bet[1] == 'odd':
                    losers.append((user, -bet[0]))
        if landon % 2 != 0:
            for user, bet in self.users.iteritems():
                if bet[1] == 'odd':
                    winners.append((user, bet[0]))
                elif bet[1] == 'even':
                    losers.append((user, -bet[0]))
        if landon > 0 and landon <= 12:
            for user, bet in self.users.iteritems():
                if bet[1] == '1-3':
                    winners.append((user, bet[0]*2))
                elif bet[1] == '2-3' or bet[1] == '3-3':
                    losers.append((user, -bet[0]))
        if landon > 13 and landon <= 25:
            for user, bet in self.users.iteritems():
                if bet[1] == '2-3':
                    winners.append((user, bet[0]*2))
                elif bet[1] == '3-3' or bet[1] == '1-3':
                    losers.append((user, -bet[0]))
        if landon > 25 and landon <= 36:
            for user, bet in self.users.iteritems():
                if bet[1] == '3-3':
                    winners.append((user, bet[0]*2))
                elif bet[1] == '1-3' or bet[1] == '2-3':
                    losers.append((user, -bet[0]))
        if landon < 19:
            for user, bet in self.users.iteritems():
                if bet[1] == 'low':
                    winners.append((user, bet[0]))
                elif bet[1] == 'high':
                    losers.append((user, -bet[0]))
        else:
            for user, bet in self.users.iteritems():
                if bet[1] == 'high':
                    winners.append((user, bet[0]))
                elif bet[1] == 'low':
                    losers.append((user, -bet[0]))
        for user, bet in self.users.iteritems():
            if self.isInt(bet[1]):
                if int(bet[1]) == landon:
                    winners.append((user, bet[0]*35))
                else:
                    losers.append((user, -bet[0]))

        return [winners, losers, "The result was " + str(landon) + "\n"]

    def reset(self):
        self.users = {}