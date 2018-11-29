import deck

class blackjack:
    def __init__(self):
        self.users = {}

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, beton]

    def bet_message(self):
        return "Place your bets! Minimum bet of 2, maximum 500.\n", \
            [str(i) for i in range(2, 501)]

    def play(self, msgs):
        winners = []
        losers = []
        # msgs.put()
        cards = deck.deck()
        for user, bet in users:
            card1 = cards.draw_card()
            card2 = cards.draw_card()
            msgs.put(['blackjack', user, None, None, [card1, card2]])

        return [winners, losers]

    def reset(self):
        self.users = {}