import socket
import sys
import select
import threading
import json
import game_manager

def main(args):
    if len(args) != 4:
        sys.exit("Usage: script, IP, port, game name")

    ip_addr = str(args[1])
    port    = int(args[2])
    game    = str(args[3])

    gm = game_manager.Game_manager(game)
    gm.connect_to_casino(ip_addr, port)
    gm.game_fun()

if __name__ == '__main__':
    main(sys.argv)