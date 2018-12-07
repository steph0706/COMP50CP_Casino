# all_in
### Thu Cao, Long Tran, Stephanie Wong

# Project

This casino, implemented in python, sets out to deliver three games for clients interested in playing virtual casino games: baccarat, blackjack and roulette. Clients will receive the same experience playing in this casino as if they were there in reality. 

Clients will join the the casino, which is a server that runs each game server. The game servers starts a new thread each time a new room is created. Clients will be able to switch from game to game, however, they cannot be in multiple games at once.

# Instructions to run Program
Server side (IP-address needs to be your personal IP):
```
python server.py [IP-address] [Port number]
```

in a different terminals (after running the main server):
```
python game_server.py [IP-address] [Port number] blackjack
python game_server.py [IP-address] [Port number] roulette
python game_server.py [IP-address] [Port number] baccarat
```

Client side (after all servers have started running):

```
python client.py [IP-address] [Port number]
```


# Files
`server.py`
Creates the casino server and listens for connections from game_server and client. Facilitates message passing between client and game_server.

`client.py`
Implements all client-facing functions and interacts with the client and passes and receives messages from the server

`game_server.py`
Creates an instance of the game_manager object for each type of game

`game_manager.py`
is a generic game manager that facilitates all message passing between the server and the individual games (via rooms)

`room.py`
Room class represents a room playing a game. Each room contains users and keeps track of how much money they have. Messages from games will be added to a message queue that the game manager reads from

`deck.py`
Represents a deck of  of  52 playing cards and takes care of card drawing functions.

`roulette.py`
Contains the actual game play for roulette.

`baccarat.py`
Contains the actual game play for baccarat

`blackjack.py`
Contains the actual game play for blackjack


