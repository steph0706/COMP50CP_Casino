import random
import time

class deck:
    def __init__(self):
        random.seed(time.time())
        self.deck = [(str(val), suit) for val in xrange(1, 14) \
               for suit in ['Hearts', 'Diamonds','Clubs', 'Spades']]

        for i in xrange(len(self.deck)):
            if self.deck[i][0] == '1':
                self.deck[i] = ('A', self.deck[i][1])
            elif self.deck[i][0] == '11':
                self.deck[i] = ('J', self.deck[i][1])
            elif self.deck[i][0] == '12':
                self.deck[i] = ('Q', self.deck[i][1])
            elif self.deck[i][0] == '13':
                self.deck[i] = ('K', self.deck[i][1])

    def draw_card(self):
        if len(self.deck) == 0:
            return (0, 0)
        card = self.deck[random.randint(0, len(self.deck) - 1)]
        self.deck.remove(card)
        return card