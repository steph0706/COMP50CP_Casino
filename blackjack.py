import deck

class blackjack:
    def __init__(self):
        self.users = {}
        self.deck = deck.deck()

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, beton]

    def bet_message(self):
        return "blackjack", \
            ["blackjack"]

    def play(self, msgs):
        winners = []
        losers = []
        # msgs.put()
        for user, bet in self.users.iteritems():
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            print card1
            print card2
            msgs.put(['bjack-deal', user, None, None, [card1, card2]])

        return [winners, losers]
    
    def hit(self, msgs):
        x=1

    def reset(self):
        self.users = {}