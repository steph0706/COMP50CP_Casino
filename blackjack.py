import deck

class blackjack:
    def __init__(self):
        self.users = {}
        self.deck = deck.deck()

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, None]

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
            self.users[user] + [card1, card2]
            print card1
            print card2
            msgs.put(['bjack-deal', user, None, None, [card1, card2]])
        
        dealer = [self.deck.draw_card(), self.deck.draw_card()]
        
        for user, bet in self.users.iteritems():
            while bet[1] is None:
                continue
            if bet[1] == 'hit':
                card3 = self.deck.draw_card()
                self.users[user].append(card3)
                msgs.put(['bjack-hit', user, None, None, card3])
            else:
                continue
         
        dealerScore = self.get_dealer(dealer)

        for user, bet in self.users.iteritems():
            cards = bet[2:]
            total = 0
            for card in cards:
                value = card[0]
                if value == 'J' or value == 'Q' or value == 'K':
                    value = 10
                if value == 'A':
                    value = 11
                total += int(value)
            if total > 21:
                losers.append((user, -bet[0]))
            elif total == 21:
                winners.append((user, bet[0]))
            else:
                if dealerScore < total:
                    winners.append((user, bet[0]))
                else:
                    losers.append((user, -bet[0]))

        return [winners, losers]
    
    def get_dealer(self, dealer):
        total = 0
        for card in dealer:
            value = card[0]
            if value == 'J' or value == 'Q' or value == 'K':
                value = 10
            if value == 'A':
                value = 11
            total += int(value)

        while total < 16:
            card3 = self.deck.draw_card()
            value = card3[0]
            if value == 'J' or value == 'Q' or value == 'K':
                value = 10
            if value == 'A':
                value = 11
            total += int(value)

        if total > 21:
            return -1
        return total

    def stop_hit(self, user):
        print "stopping hitting"
        self.users[user][1] = 'stand'

    def start_hit(self, user):
        self.users[user][1] = 'hit'

    def reset(self):
        self.users = {}