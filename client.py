import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()
IP_ADDRESS = str(sys.argv[1])
PORT = int(sys.argv[2])
server.connect((IP_ADDRESS, PORT))

while True:

    # possible input streams
    sockets_list = [sys.stdin, server]

    # find sockets that are ready to be read from
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print message
        else:
            message = sys.stdin.readline()
            server.send(message)
            sys.stdout.flush()
server.close()
