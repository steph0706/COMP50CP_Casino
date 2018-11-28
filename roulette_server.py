BET_MSG = "Place your bets! Before all your bets, please type 'bet' followed " \
            + "by a space and the following:"
            + "Bet on it landing on an even number by typing 'even'\n" \
            + "Bet on an odd number by typing 'odd'\n" \
            + "Bet on it landing on a number between 0 and 12 by typing " \
            + "'1-3'\n" \
            + "Bet on it landing on a number between 13 and 25 by typing " \
            + "'2-3'\n" \
            + "Bet on it landing on a number between 26 and 36 by typing " \
            + "'3-3'\n" \
            + "Bet on it landing on a specific number by typing the " \
            + "number\n" \
            +" Type 'low' to bet between 0 and 18, and type 'high' to bet " \
            + "higher than 18\n" \
            + "Place your what you're betting on followed by a space and how " \
            + "much you're betting: "

def isInt(num):
    try: 
        int(num)
        return True
    except ValueError:
        return False

def roll(users):
    landon = random.randint(0, 36)
    losers = []
    winners = []
    if landon % 2 == 0:
        for user in users:
            if user[4] == 'even':
                winners.append((user[0], user[3]*2))
            elif user[4] == 'odd':
                losers.append((user[0], user[3]))
    if landon % 2 != 0:
        for user in users:
            if user[4] == 'odd':
                winners.append((user[0], user[3]*2))
            elif user[4] == 'even':
                losers.append((user[0], user[3]))
    if landon > 0 and landon <= 12:
        for user in users:
            if user[4] == '1-3':
                winners.append((user[0], user[3]*3))
            elif user[4] == '2-3' or user[4] == '3-3':
                losers.append((user[0], user[3]))
    if landon > 13 and landon <= 25:
        for user in users:
            if user[4] == '2-3':
                winners.append((user[0], user[3]*3))
            elif user[4] == '3-3' or user[4] == '1-3':
                losers.append((user[0], user[3]))
    if landon > 25 and landon <= 36:
        for user in users:
            if user[4] == '3-3':
                winners.append((user[0], user[3]*3))
            elif user[4] == '1-3' or user[4] == '2-3':
                losers.append((user[0], user[3]))
    if landon < 19:
        for user in users:
            if user[4] == 'low':
                winners.append((user[0], user[3]*2))
            elif user[4] == 'high':
                losers.append((user[0], user[3]))
    else:
        for user in users:
            if user[4] == 'high':
                winners.append((user[0], user[3]*2))
            elif user[4] == 'low':
                losers.append((user[0], user[3]))
    for user in users:
        if isInt(user[4]):
            if int(user[4]) == landon:
                winners.append((user[0], user[3]*36))
            else:
                losers.append((user[0], user[3]))
    return winners, losers

def run(users):
    for user in users:
        user[1].send(BET_MSG)

    allBet = all(user[3] is not None for user in users)
    while not allBet:
        allBet = all(user[3] is not None for user in users)

    return roll(users)



