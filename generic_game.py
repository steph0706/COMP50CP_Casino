class gen_game:
    def __init__(self):
        self.users = {}
        # do nothing

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, beton]

    def bet_message(self):
        return 'What do you want to bet on? True or False?', \
               ['True', 'False']

    def play(self):
        winners = []
        losers  = []
        for user, bet in self.users.iteritems():
            #print(user + " bet " + str(bet[0]) + " on " + str(bet[1]))
            if bet[1] == 'True':
                winners.append([user, bet[0]])
            else:
                losers.append([user, -bet[0]])
        return [winners, losers]

    def reset(self):
        self.users = {}