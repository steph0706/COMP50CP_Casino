import deck
import threading

class blackjack:
    def __init__(self):
        """ 
            dictionary mapping users --> [bet, card1, card2...card-n] 
        """
        self.users = {}
        self.deck = deck.deck()

        """ 
            locks the play thread if none of the players have decided
            their next move, whether that be stand or hit
        """
        self.hitLock = threading.Lock()

        """
            the condition so that the play thread will wait until a player
            has decided what to do as their move
        """
        self.waitForHit = threading.Condition(self.hitLock)
        self.hitting = True

    def bet(self, user, betsize, beton):
        """ sets the users bet in the dictionary """
        self.users[user] = [betsize, None]

    def bet_message(self):
        """ 
            returns the correct bet message to send to the client, in this case
            there is no bet message
        """
        return "blackjack", ["blackjack"]


    def allDoneHitting(self):
        """ 
            return trues if all the users have decided to stand, false otherwise
        """
        done = True
        for user, bet in self.users.iteritems():
            done = done and (bet[1] == 'stand')
        return done

    def busted(self, cards):
        """
            returns true if the user's cards add up to more than 21
        """
        total = 0
        for card in cards:
            value = self.deck.get_value(card)
            total += int(value)

        """ A defaults to 11, but can be used as 1 if the value is > 21 """
        for card in cards:
            value = card[0]
            if total > 21 and value == 'A':
                total -= 10
        return total > 21

    def play(self, msgs):     
        """ 
            contains the actual game play, and returns the result of the game.
            the result of the game consists of a list of winners and losers and the
            amount they won/lost respectively and the result of the game
            to print to the client
        """
        winners = []
        losers = []

        """ deals 2 cards to every user consecutively """
        for user, bet in self.users.iteritems():
            card1 = self.deck.draw_card()
            card2 = self.deck.draw_card()
            self.users[user] = self.users[user] + [card1, card2]
            msgs.put(['bjack-deal', user, None, None, [card1, card2]])
        
        """ deals two cards to dealer """
        dealer = [self.deck.draw_card(), self.deck.draw_card()]
        
        """ wait for users to start hitting """
        with self.hitLock:
            self.waitForHit.wait()

        """ check if all players have chosen to stand """
        doneHitting = self.allDoneHitting()
        while not doneHitting:
            for user, bet in self.users.iteritems():
                if bet[1] == 'hit':
                    if self.busted(bet[2:]):
                        msgs.put(['wait', user, 'Oops, you have already ' + \
                            'busted'])
                        msgs.put(['wait', user, 'Waiting for other users to' \
                            + 'finish betting'])
                        self.users[user][1] = 'stand'
                        break
                    card3 = self.deck.draw_card()
                    self.users[user] += [card3]

                    """ 
                        reset to None to wait for user to decide whether to
                        stand or hit
                    """
                    self.users[user][1] = None
                    msgs.put(['bjack-hit', user, None, None, card3])
            
            doneHitting = self.allDoneHitting()

        dealerScore, dealerMsg = self.get_dealer(dealer)

        """ get users scores """
        for user, bet in self.users.iteritems():
            cards = bet[2:]
            total = 0
            for card in cards:
                value = self.deck.get_value(card)
                print value
                total += int(self.deck.get_value(card))

            for card in cards:
                value = card[0]
                if total > 21 and value == 'A':
                    total -= 10

            if total > 21:
                losers.append((user, -bet[0]))
            elif self.checkForNatural(cards):
                winners.append((user, bet[0] * 1.5))
            elif total == 21:
                winners.append((user, bet[0]))
            else:
                if dealerScore < total:
                    winners.append((user, bet[0]))
                else:
                    losers.append((user, -bet[0]))
 
        return [winners, losers, dealerMsg]
    
    
    def checkForNatural(self, cards):
        """ checks if the user got a natural (i.e. original deal == 21) """
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
        """ gets the dealers score """
        msg = "Dealer's hand was "
        total = 0
        for card in dealer:
            msg += str(card[0]) + " of " + str(card[1]) + ", "
            value = self.deck.get_value(card)
            total += int(value)

        while total < 16:
            card3 = self.deck.draw_card()
            msg += str(card3[0]) + " of " + str(card3[1]) + ", "
            value = self.deck.get_value(card3)
            total += int(value)

        if total > 21:
            return -1, msg[:-2] + "\n"
        return total, msg[:-2] + "\n"


    def stop_hit(self, user):
         """ 
            sets the user's move in the dictionary to stand 
            and notifies the waiting thread that they've
            started moves/hitting
        """
        self.users[user][1] = 'stand'
        with self.hitLock:
            self.waitForHit.notify()

    def start_hit(self, user):
        """ 
            sets the user's move in the dictionary to hit
            and notifies the waiting thread that they've
            started moves/hitting
        """
        self.users[user][1] = 'hit'
        with self.hitLock:
            self.waitForHit.notify()

    def reset(self):
        """ resets the game """
        self.users = {}
