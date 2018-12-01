import socket
import select
import sys
import json

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main(args):
    if len(args) != 3:
        sys.exit("Usage: script, IP address, port number")
    ip_addr = str(args[1])
    port    = int(args[2])

    SERVER.connect((ip_addr, port))
    actions = {
        'name'        : insert_preference,
        'game'        : insert_preference,
        'bet'         : handle_bet,
        'print'       : print_a_message,
        'result'      : handle_result,
        'bjack-cards' : handle_bjack,
        'bjack-hit'   : handle_hit,
    }

    print("connected to server")

    loop = 0
    while True:
        loop += 1
        # print("start loop " + str(loop))
        read_sockets, _, _ = select.select([SERVER], [], [], 0.01)
        for socks in read_sockets:
            # print("got server in loop " + str(loop))
            if socks == SERVER:
                message = socks.recv(4096)
                # print("message from server loop " + str(loop) \
                #                + ": " + str(message)) # debug print
                try:
                    message = json.loads(message)
                    action = message[0]
                    details = message[1:]
                    actions[action](details, SERVER)
                except:
                    message = message
                    # print("message from server loop exception " \
                    #           + ": " + str(message)) # debug print
    SERVER.close()

# try until an input is given from stdin
def try_to_get_input(message):
    if message == 'blackjack\n':
        return "blackjack"
    user_input = ''
    while user_input == '':
        try:
            user_input = raw_input(message)
        except:
            user_input = ''
            pass

    return user_input.lower()

def insert_preference(details, server):
    print(details[0])
    reply = sys.stdin.readline()
    server.send(reply)
    sys.stdout.flush()

def handle_bjack(details, server):
    cards = details[0]
    msg = "Here are your cards: " + cards[0][0] + " of " + cards[0][1] \
        + " and " + cards[1][0] + " of " + cards[1][1] + "\n" \
        + "Hit or Stand?\n"
    
    move = try_to_get_input(msg)
    server.send(json.dumps(['bjack-move', details[1], move, 'blackjack']))

def handle_hit(details, server):
    card = details[0]
    msg = "Here's your next card: " + card[0] + " of " + card[1] + "\n" \
        + "Hit or Stand?\n"
    move = try_to_get_input(msg)
    server.send(json.dumps(['bjack-move', details[1], move, 'blackjack']))

def handle_bet(details, server):
    betsize = try_to_get_input("How much do you want to bet? Note: " \
                            + "your total money is " + str(details[1]) + '\n')

    # check whether input is a proper number
    while True:
        try:
            betsize = int(betsize)
        except:
            betsize = try_to_get_input("Not a number. Please insert a number.\n")
            continue

        if int(betsize) > int(details[1]) or int(betsize) <= 0:
            betsize = try_to_get_input("Your bet exceeds your total money " \
                        + "or is 0 or less. Please insert a positive bet " \
                        + "less than your total.\n")
        else:
            break

    beton = try_to_get_input(details[2] + '\n')

    # check whether input (have not converted .lower() yet) matches anything
    # in the set of proper bets
    while str(beton) not in set(details[3]):
        beton = try_to_get_input("Not a valid side to bet on\n" \
                            + "Options are: " + json.dumps(details[3]) + '\n')

    message = ['bet', details[0], details[1], betsize, beton, details[-1]]
    server.send(json.dumps(message))

def print_a_message(details, server):
    print(details[1])

def handle_result(details, server):

    # checks whether input is yes/no
    print(details[1])
    ans = try_to_get_input("Continue game? Please type yes or no\n")
    while str(ans).lower() not in set(['yes', 'no']):
        ans = try_to_get_input("Please enter 'yes' or 'no'.\n")

    # assign the correct command for associated input
    if str(ans) == 'yes':
        command = 'continue'
        ans = details[-1]
    elif str(ans) == 'no':
        ans = try_to_get_input("Which game do you want to play now? Please" \
                + " enter blackjack, roulette, or baccarat. If you want to" \
                + " quit, please enter 'quit'.\n")
        while str(ans).lower() not in set(['blackjack', 'roulette', \
                                            'baccarat', 'quit']):
            ans = try_to_get_input("Invalid input. Please enter one of the" \
                + " following:\nblackjack, roulette, baccarat, quit")
        
        if ans == 'quit':
            command = ans
            ans = details[-1]
        else:
            command = 'switch'


    message = [command, details[0], details[2], ans]
    server.send(json.dumps(message))

if __name__ == '__main__':
    main(sys.argv)