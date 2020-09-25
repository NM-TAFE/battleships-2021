import time
from client import Battleship

battleship = Battleship()


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
def attack(vector):
    vector = vector[0]
    print(f'Shot received at {vector}')
    while True:
        print("""H)it, m)iss, or d)efeat?""")
        s = input('Enter status> ')
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
        else:
            continue


@battleship.on()
def win():
    print('Yay! You won!')
    exit(0)


@battleship.on()
def lose():
    print('Aww... You lost...')
    exit(0)


print('Waiting for the game to start.')
battleship.join()
while True:
    time.sleep(1.0)
