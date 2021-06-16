import os
import random
import threading
import time
from battlefield import Battlefield
from battleship_client import BattleshipClient

grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')


class Game:
    SHIPS = {
        'A': 5,
        'B': 4,
        'S': 3,
        's': 3,
        '5': 3,
        'C': 3,
        'D': 2,
        'd': 2,
        'P': 1,
        'p': 1,
    }

    def __init__(self):
        # Get a copy of the ships
        self.__ships = self.SHIPS.copy()

        self.__mine = Battlefield(colour=193)
        self.__opponent = Battlefield(colour=208)

        playing = threading.Event()
        playing.set()
        self.__playing = playing

        # Create Battleship Client
        client = BattleshipClient(grpc_host=grpc_host, grpc_port=grpc_port)

        # Assign event handlers
        client.add_event_listener('begin', self.begin)
        client.add_event_listener('start_turn', self.start_turn)
        client.add_event_listener('end_turn', self.end_turn)
        client.add_event_listener('hit', self.hit)
        client.add_event_listener('miss', self.miss)
        client.add_event_listener('win', self.won)
        client.add_event_listener('lose', self.lost)
        client.add_event_listener('attack', self.attacked)

        self.__client = client

    def setup(self):
        """
        Randomly place ships on the grid.
        """
        for ship in self.__ships:
            size = self.__ships[ship]
            while True:
                x = random.choice('ABCDEFGHIJ')
                y = random.randint(1, 10)
                o = random.choice([False, True])
                if self.__mine.place_ship(ship, x, y, size, horizontal=o) is True:
                    break

        print(self.__mine)
        print(self.__opponent)

    def start(self):
        print('Waiting for the game to start...')
        self.__client.join()
        while self.__playing.is_set():
            time.sleep(1.0)

    def begin(self):
        pass

    def start_turn(self):
        pass

    def end_turn(self):
        pass

    def hit(self):
        pass

    def miss(self):
        pass

    def won(self):
        pass

    def lost(self):
        pass

    def attacked(self, vector):
        pass


def main():
    game = Game()
    game.setup()
    game.start()


if __name__ == '__main__':
    main()
