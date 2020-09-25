import time
from client import Battleship

battleship = Battleship()


@battleship.on()
def begin():
    print('Game started!')


@battleship.on()
def start_turn():
    print('Start turn received!')


@battleship.on()
def end_turn():
    print('End turn received!')


battleship.join()
time.sleep(120)
