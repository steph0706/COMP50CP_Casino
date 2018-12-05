"""

    game_server.py

    This is a main function that creates a game_manager object; open
    this file to connect to casino server

"""
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

if __name__ == '__main__':
    main(sys.argv)