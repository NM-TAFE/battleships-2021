# Battleships client

This is a simple reference implementation showing how to use the client to play Battleships against the gRPC
powered game server. (Well, you're actually playing against another player.)

### Using the Battleship client in an actual implementation

Let's have a look at the client code to see how it can be used.

First, we import a few python libraries and the Battleship client.

```python
import os
import threading
import time
from client import Battleship
```

We need to connect to the game server, for which we use a couple of environment variables: `GRPC_HOST` and `GRPC_PORT`:

```python
grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')
```

We create a flag which indicates that we are playing and instantiate the Battleship client using the gRPC host and port
we retrieved from the environment variables:

```python
playing = threading.Event()
playing.set()

battleship = Battleship(grpc_host=grpc_host, grpc_port=grpc_port)
```

We register a number of event handlers that will be called when certain events happen during the game. The comments
describe what each of them is about. You can register callbacks using the `.on()` decorator. You should either use the
name as shown below (the function names) or provide it in the decorator call: `.on('begin')`. See the comments in the
source code for a more detailed explanation.

```python
@battleship.on()
def begin():
    """This callback is called when the game server indicates that a
    game starts. This happens when two players are available to play.
    If you're the first to register, you may have to wait for someone
    else to join.
    """
    print('Game started!')


@battleship.on()
def start_turn():
    """This callback indicates that it is this client's turn to do a
    move (attack a square). 
    """
    s = input('Your move> ')
    battleship.attack(s)



@battleship.on()
def end_turn():
    """This callback indicates this client's turn is over. It is not
    used in this example implementation but is added for the sake of
    completeness.
    """
    pass


@battleship.on()
def hit():
    """This callback indicates that the other player has marked your
    attack as a hit.
    """
    print('You hit the target!')


@battleship.on()
def miss():
    """This callback indicates that the other player has marked your
    attack as a miss.
    """
    print('Aww.. You missed!')


@battleship.on()
def win():
    """This callback indicates that the other player was defeated.
    """
    print('Yay! You won!')
    playing.clear()


@battleship.on()
def lose():
    """This callback indicates that you are defeated. This callback is
    called when you call the :meth:`defeat` method on the Battleship
    client, so this will never come as a surprise.
    """
    print('Aww... You lost...')
    playing.clear()


@battleship.on()
def attack(vector):
    """This callback indicates an attack by the other player. It takes
    a single argument, which is the square that was attacked. Please
    note that the game server does not perform any validation on the
    vector, so it is up to the clients to agree on a certain format (it
    must be a string, though).

    Just like in the example below, you should respond to an attack with
    either a hit, miss, or a defeat. The latter means that this client's
    ships all have been sunk and the game is over.

    :param vector: a string indicating the square that was attacked
    """
    vector = vector[0]
    print(f'Shot received at {vector}')
    while True:
        print("""H)it, m)iss, or d)efeat? """)
        s = input('Enter status> ')
        if len(s):
            _s = s[0].upper()
            if _s == 'H':
                battleship.hit()
                break
            elif _s == 'M':
                battleship.miss()
                break
            elif _s == 'D':
                battleship.defeat()
                break
```

In order to play the game, the client must first "join" a game (or start a new game if no open game is available).
The game has really started when the `begin` event is raised, after which either `start_turn` or `end_turn` will
indicate whether or not it's this client's turn. 

Finally, the game should be played as long as the flag `playing` is still set (as an example). The event handlers
are called from a different thread than the main thread.

```python
print('Waiting for the game to start...')
battleship.join()
while playing.is_set():
    # Be nice to the processor
    time.sleep(1.0)
```

The other functions that are available are:

- `battleship.attack(vector)`: to attack the other player's board (with `vector` indicating a square on the board),
- `battleship.hit()`: to indicate the other player hit a ship in the square that was attacked,
- `battleship.miss()`: to indicate the other player's attack was a miss, and
- `battleship.defeat()`: to indicate this player is defeated (just like in the real board game when the last ship is sunk).

With these functions and the callback functions, you can implement a client of your own, for instance, one that
keeps track of the moves in a graphical UI, that plays appropriate sounds upon hits and misses, etc.

Please note that the game server does not keep track of the moves and has no knowledge of who wins the game. This
is up to the clients. 
