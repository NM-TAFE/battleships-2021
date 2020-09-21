import queue
import threading
import time
import unittest
from app.battleships_pb2 import Request, Response
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
        response = next(input_stream)
        print(f'Received - {s} -', response, flush=True)


def test_simple_game_play():
    q1 = queue.Queue()
    q2 = queue.Queue()
    game_server_1 = Battleship(REDIS_HOST)
    game_server_2 = Battleship(REDIS_HOST)

    stream_1 = stream(q1)
    stream_2 = stream(q2)

    input_stream_1 = game_server_1.Game(stream_1, {})
    input_stream_2 = game_server_2.Game(stream_2, {})

    t1 = threading.Thread(
        target=lambda: read_incoming(input_stream_1, '12345'))
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(
        target=lambda: read_incoming(input_stream_2, '54321'))
    t2.daemon = True
    t2.start()

    q1.put(Request(join=Request.Player(id='12345')))
    time.sleep(0.1)
    q2.put(Request(join=Request.Player(id='54321')))

    time.sleep(1)


class TestGamePlay(unittest.TestCase):
    def test_simple_game_play(self):
        test_simple_game_play()


if __name__ == '__main__':
    test_simple_game_play()
