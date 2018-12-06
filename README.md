# all_in
# Python implementation of a casino running Blackjack, Baccarat and Roulette


# FILES
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

# Instructions to run Program
```python server.py [IP-address] [Port number]```

in a different terminals:
```
python game_server.py [IP-address] [Port number] blackjack
python game_server.py [IP-address] [Port number] roulette
python game_server.py [IP-address] [Port number] baccarat
```

client side:
```python client.py [IP-address] [Port number]```
