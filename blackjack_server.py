import socket
import sys
import select
import threading
import json

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
MESSAGES = {
	'join'   : join_room,
	'remove' : remove_user
	# add more msg later
}
ROOM_CAP = 5

def connect_to_casino(ip_addr, port):
	users = set()
	rooms = []
	SERVER.connect((ip_addr, port))

	while True:
		read_sockets, _, _ = select.select([SERVER], [], [])

		for socks in read_sockets:
			if socks == SERVER:
				message = json.load(socks.recv(2048))
				user    = message[1]
				money   = message[2]
				betsize = message[3]
				MESSAGES[message[0]](users, user, rooms, money, betsize)
	SERVER.close()

def join_room(users, user, rooms, money, betsize=None):
	users.add(user)
	for room in rooms:
		# add code after rooms have been implemented
		#if room.cap() < ROOM_CAP:
		#	room.add(user, money)
		# return True
	# new_room = NEW BLACKJACK OBJECT
	# new_room.add(user, money)
	# rooms.append(new_room)
	# return True

def remove_user(users, user, rooms, money, betsize=None):
	users.remove(user)
	for room in rooms:
		# add code after rooms have been implemented
		# if room.has(user) == True:
		#	room.remove(user)
		#	return True