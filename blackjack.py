import deck
import threading

class blackjack:
    def __init__(self):
        self.users = {}
        self.deck = deck.deck()
        self.hitLock = threading.Lock()
        self.waitForHit = threading.Condition(self.hitLock)
        self.hitting = True

    def bet(self, user, betsize, beton):
        self.users[user] = [betsize, None]

    def bet_message(self):
        return "blackjack", ["blackjack"]

    def allDoneHitting(self):
        done = True
        for user, bet in self.users.iteritems():
            done = done and (bet[1] == 'stand')
        return done

    def play(self, msgs):
        winners = []
        losers = []

        for user, bet in self.users.iteritems():
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            self.users[user] = self.users[user] + [card1, card2]
            msgs.put(['bjack-deal', user, None, None, [card1, card2]])
        
        dealer = [self.deck.draw_card(), self.deck.draw_card()]
        
        with self.hitLock:
            self.waitForHit.wait()
        doneHitting = self.allDoneHitting()
        while not doneHitting:
            for user, bet in self.users.iteritems():
                if bet[1] == 'hit':
                    card3 = self.deck.draw_card()
                    entry = self.users[user] + [card3]
                    entry[1] = None
                    self.users[user] = entry
                    msgs.put(['bjack-hit', user, None, None, card3])
            doneHitting = self.allDoneHitting()

        dealerScore, dealerMsg = self.get_dealer(dealer)

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

            
            for card in cards:
                value = card[0]
                if total > 21 and value == 'A':
                    total -= 10

            if total > 21:
                losers.append((user, -bet[0]))
            elif self.checkForNatural(cards):
                winners.append(user, bet[0] * 1.5)
            elif total == 21:
                winners.append((user, bet[0]))
            else:
                if dealerScore < total:
                    winners.append((user, bet[0]))
                else:
                    losers.append((user, -bet[0]))
 
        return [winners, losers, dealerMsg]
    
    def checkForNatural(self, cards):
        if len(cards) == 2:
            card1 = cards[0]
            card2 = cards[1]
            if card1[0] == 'A' and (card2[0] == 10 or card2[0] == 'K' \
                or card2[0] == 'Q' or card2 == 'J'):
                return True
            elif card2[0] == 'A' and (card1[0] == 10 or card1[0] == 'K' \
                or card1[0] == 'Q' or card1 == 'J'):
                return True
        return False


    def get_dealer(self, dealer):
        msg = "Dealer's hand was "
        total = 0
        for card in dealer:
            msg += str(card[0]) + " of " + str(card[1]) + ", "
            value = card[0]
            if value == 'J' or value == 'Q' or value == 'K':
                value = 10
            if value == 'A':
                value = 11
            total += int(value)

        while total < 16:
            card3 = self.deck.draw_card()
            msg += str(card3[0]) + " of " + str(card3[1]) + ", "
            value = card3[0]
            if value == 'J' or value == 'Q' or value == 'K':
                value = 10
            if value == 'A':
                value = 11
            total += int(value)

        if total > 21:
            return -1, msg[:-2] + "\n"
        return total, msg[:-2] + "\n"

    def stop_hit(self, user):
        self.users[user][1] = 'stand'
        with self.hitLock:
            self.waitForHit.notify()

    def start_hit(self, user):
        self.users[user][1] = 'hit'
        with self.hitLock:
            self.waitForHit.notify()

    def reset(self):
        self.users = {}
