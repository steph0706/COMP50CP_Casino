"""
    Author: all_in

    deck class contains a deck of the 52 playing cards and takes care of drawing functions.
"""

import random, time

class deck:
    def __init__(self):
        """ Initializes a deck of 52 playing cards. """
        random.seed(time.time())
        self.deck = []
        self.reshuffle()

        self.face_value = {'A':11, 'J':10, 'Q':10, 'K':10}

    def draw_card(self):
        """ Draws a random card from the deck and reshuffle if deck is empty. """
        if len(self.deck) == 0:
            self.reshuffle()
            draw_card()
        card = self.deck[random.randint(0, len(self.deck) - 1)]
        self.deck.remove(card)
        return card

    def reshuffle(self):
        """ Creates a new deck of cards. """
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


    def get_face_value(self, card):
    """ Returns the numerical value of face cards and Ace. """
        if card[0] in self.face_value:
            return self.face_value[card[0]] 

