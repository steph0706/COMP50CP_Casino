<<<<<<< HEAD
import socket
import select
import sys

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main(args):
	if len(args) != 3:
		sys.exit("Usage: script, IP address, port number")
	ip_addr = str(args[1])
	port    = int(args[2])

	SERVER.connect((ip_addr, port))

	print("connected to server")
	while True:
		sockets_list = [sys.stdin, SERVER]

		read_sockets, _, _ = select.select(sockets_list, [], [])

		for socks in read_sockets:
			if socks == SERVER:
				message = socks.recv(2048)
				print(message)
			else:
				message = sys.stdin.readline()
				SERVER.send(message)
				sys.stdout.flush()
	SERVER.close()

if __name__ == '__main__':
=======
import socket
import select
import sys

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main(args):
	if len(args) != 3:
		sys.exit("Usage: script, IP address, port number")
	ip_addr = str(args[1])
	port    = int(args[2])

	SERVER.connect((ip_addr, port))

	print("connected to server")
	while True:
		sockets_list = [sys.stdin, SERVER]

		read_sockets, _, _ = select.select(sockets_list, [], [])

		for socks in read_sockets:
			if socks == SERVER:
				message = socks.recv(2048)
				print(message)
			else:
				message = sys.stdin.readline()
				SERVER.send(message)
				sys.stdout.flush()
	SERVER.close()

if __name__ == '__main__':
>>>>>>> 89ac322dd2748d90eb953a882712383fc2270123
	main(sys.argv)