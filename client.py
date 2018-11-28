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
        'name'   : insert_preference,
        'game'   : insert_preference,
        'bet'    : handle_bet,
        'result' : handle_result
    }

    print("connected to server")

    loop = 0
    while True:
        loop += 1
        #print("start loop " + str(loop))
        read_sockets, _, _ = select.select([SERVER], [], [], 0.01)
        for socks in read_sockets:
            #print("got server in loop " + str(loop))
            if socks == SERVER:
                message = socks.recv(4096)
                print("message from server loop " + str(loop) + ": " + str(message))
                try:
                    message = json.loads(message)
                    action = message[0]
                    details = message[1:]
                    actions[action](details, SERVER)
                except:
                    message = message
                    print("message from server loop exception " + ": " + str(message))
    SERVER.close()

def insert_preference(details, server):
    print(details[0])
    reply = sys.stdin.readline()
    server.send(reply)
    sys.stdout.flush()

def handle_bet(details, server):
    print("How much do you want to bet? Note: your total money is " \
          + str(details[1]))
    betsize = input()
    while True:
        try:
            int(betsize)
        except:
            betsize = input("Not a number. Please insert a number.\n")
            continue

        if betsize > details[1] or betsize <= 0:
            betsize = input("Your bet exceeds your total money or is 0 or less." \
                        + " Please insert a positive bet less than your total.\n")
        else:
            break

    print(details[2]) # print bet message
    beton = str(input())
    while beton not in set(details[3]):
        beton = str(input("Not a valid side to bet on\n"))
        print("Options are: " + json.dumps(details[3]))

    try:
        message = ['bet', details[0], details[1], betsize, beton, details[-1]]
        print("Message to be sent")
        print(message)
        server.send(json.dumps(message))
        print("Message sent to server")
    except:
        print("Error somewhere here")

def handle_result(details, server):
    print(details[0])
    c = input("Continue game?\n")

if __name__ == '__main__':
    main(sys.argv)