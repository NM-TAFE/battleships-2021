import queue
import threading
import time
import unittest
from datetime import datetime
from app.battleships_pb2 import Attack, Request, Response, Status
from app.server import Battleship

REDIS_HOST = '192.168.20.50'


def stream(q):
    while True:
        s = q.get()
        if s is not None:
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


def test_simple_game_play():
    alice = queue.Queue()
    bob = queue.Queue()
    game_server_1 = Battleship(REDIS_HOST)
    game_server_2 = Battleship(REDIS_HOST)

    input_stream_1 = game_server_1.Game(stream(alice), {})
    input_stream_2 = game_server_2.Game(stream(bob), {})

    t1 = threading.Thread(
        target=lambda: read_incoming(input_stream_1, 'Alice'))
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(
        target=lambda: read_incoming(input_stream_2, 'Bob'))
    t2.daemon = True
    t2.start()

    # Both players join
    alice.put(Request(join=Request.Player(id='Alice')))
    time.sleep(1.5)
    bob.put(Request(join=Request.Player(id='Bob')))
    time.sleep(1.5)

    # Player 1 gets to start
    alice.put(Request(move=Attack(vector="a1")))
    time.sleep(1.5)
    bob.put(Response(report=Status(state=Status.State.HIT)))
    time.sleep(1.5)

    # Now it is Player 2's turn
    bob.put(Request(move=Attack(vector="j10")))
    time.sleep(1.5)
    alice.put(Response(report=Status(state=Status.State.MISS)))
    time.sleep(1.5)

    # Now it is Player 1's turn
    alice.put(Request(move=Attack(vector="c5")))
    time.sleep(1.5)
    bob.put(Response(report=Status(state=Status.State.HIT)))
    time.sleep(1.5)

    # Now it is Player 2's turn
    bob.put(Request(move=Attack(vector="e3")))
    time.sleep(1.5)
    alice.put(Response(report=Status(state=Status.State.DEFEAT)))
    time.sleep(1.5)

    alice.put(None)
    bob.put(None)
    time.sleep(1)


class TestGamePlay(unittest.TestCase):
    def test_simple_game_play(self):
        test_simple_game_play()


if __name__ == '__main__':
    test_simple_game_play()
