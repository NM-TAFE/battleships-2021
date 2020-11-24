import os
import threading
import time
from client import Battleship

grpc_host = os.getenv('GRPC_HOST', 'b.sndm.me')
grpc_port = os.getenv('GRPC_PORT', '50051')

playing = threading.Event()
playing.set()

battleship = Battleship(grpc_host=grpc_host, grpc_port=grpc_port)


@battleship.on()
def begin():
    print('Game started!')


@battleship.on()
def start_turn():
    s = input('Your move> ')
    battleship.attack(s)


@battleship.on()
def hit():
    print('You hit the target!')


@battleship.on()
def miss():
    print('Aww.. You missed!')


@battleship.on()
def win():
    print('Yay! You won!')
    playing.clear()


@battleship.on()
def lose():
    print('Aww... You lost...')
    playing.clear()


@battleship.on()
def attack(vector):
    vector = vector[0]
    print(f'Shot received at {vector}')
    while True:
        print("""H)it, m)iss, or d)efeat?""")
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


print('Waiting for the game to start...')
battleship.join()
while playing.is_set():
    time.sleep(1.0)
