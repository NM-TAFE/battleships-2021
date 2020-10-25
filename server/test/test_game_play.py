import queue
import threading
import time
import unittest
from datetime import datetime
from battleships_pb2 import Attack, Request, Status
from server import Battleship

REDIS_HOST = '192.168.20.50'


def stream(q, p):
    while True:
        s = q.get()
        if s is not None:
            print(f'{datetime.now()} - {p} - Sending -', s, flush=True)
            yield s
        else:
            return


def read_incoming(input_stream, s):
    while True:
        try:
            response = next(input_stream)
            print(f'{datetime.now()} - {s} - Received -', response, flush=True)
        except StopIteration:
            return


def attack(vector):
    return Request(move=Attack(vector=vector))


def report(state):
    return Request(report=Status(state=state))


def start_thread(_stream, name):
    t = threading.Thread(target=lambda: read_incoming(_stream, name))
    t.daemon = True
    t.start()


def test_simple_game_play():
    delay = 0.5

    player_1 = 'Alice'
    player_2 = 'Bob'

    alice = queue.Queue()
    bob = queue.Queue()
    game_server_1 = Battleship(REDIS_HOST)
    game_server_2 = Battleship(REDIS_HOST)

    input_stream_1 = game_server_1.Game(stream(alice, player_1), {})
    input_stream_2 = game_server_2.Game(stream(bob, player_2), {})

    start_thread(input_stream_1, player_1)
    start_thread(input_stream_2, player_2)

    # Both players join
    alice.put(Request(join=Request.Player(id=player_1)))
    time.sleep(delay)
    bob.put(Request(join=Request.Player(id=player_2)))
    time.sleep(delay)

    # Player 1 gets to start
    alice.put(attack("a1"))
    bob.put(report(Status.State.MISS))
    time.sleep(delay)

    # Now it is Player 2's turn
    bob.put(attack("j10"))
    alice.put(report(Status.State.HIT))
    time.sleep(delay)

    # Now it is Player 1's turn
    alice.put(attack("c5"))
    bob.put(report(Status.State.MISS))
    time.sleep(delay)

    # Now it is Player 2's turn
    bob.put(attack("e3"))
    alice.put(report(Status.State.DEFEAT))
    time.sleep(delay)

    alice.put(None)
    bob.put(None)
    time.sleep(1)


# class TestGamePlay(unittest.TestCase):
#     def test_simple_game_play(self):
#         test_simple_game_play()


if __name__ == '__main__':
    test_simple_game_play()
