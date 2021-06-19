import os
import random
import threading
import time
from battlefield import Battlefield
from battleship_client import BattleshipClient

grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')


class Game:
    SHIPS = {'A': 5, 'B': 4, 'S': 3, 's': 3, '5': 3,
             'C': 3, 'D': 2, 'd': 2, 'P': 1, 'p': 1,
             }

    SHIP_NAMES = {'A': 'Aircraft Carrier', 'B': 'Battleship',
                  'S': 'Submarine', 's': 'Submarine', '5': 'Submarine',
                  'C': 'Cruiser',
                  'D': 'Destroyer', 'd': 'Destroyer',
                  'P': 'Patrol Boat', 'p': 'Patrol Boat',
                  }

    def __init__(self, timeout=1.0):
        # Get a copy of the ships
        self.__ships = self.SHIPS.copy()

        self.__mine = Battlefield(colour=193)
        self.__opponent = Battlefield(colour=208)

        playing = threading.Event()
        playing.set()
        self.__playing = playing

        self.__timeout = abs(timeout)
        self.__attack_vector = None, None

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
        print("The game has started!")

    def start_turn(self):
        print("Okay, it's my turn now.")
        time.sleep(self.__timeout)
        while True:
            col = random.randint(0, 9)
            row = random.randint(0, 9)
            cell = self.__opponent.get_by_col_row(col, row)
            if cell is None:
                self.__attack_vector = col, row
                x, y = self.__mine.to_coords(col, row)
                vector = f'{x}{y}'
                print(f'Attacking on {vector}.')
                self.__client.attack(vector)
                break

    def end_turn(self):
        print("Okay, my turn has ended.")

    def hit(self):
        print("Success!")
        self.__opponent.set_by_col_row(*self.__attack_vector, 'X')
        print(self.__opponent)

    def miss(self):
        print("No luck.")
        self.__opponent.set_by_col_row(*self.__attack_vector, '.')
        print(self.__opponent)

    def won(self):
        print("I won!!!")
        self.__playing.clear()

    def lost(self):
        print("Meh. I lost.")
        self.__playing.clear()

    def attacked(self, vector):
        print(f"Oi! Getting attacked on {vector}")
        x, y = vector[0], int(vector[1:])
        cell = self.__mine.get(x, y)
        if cell is None:
            print(self.__mine)
            self.__client.miss()
        elif cell == '@':
            print('THIS SHOULD NOT HAPPEN!')  # Voiceover: "it happened."
            print(self.__mine)
            self.__client.miss()
        else:
            print("I'm hit!")
            self.__mine.set(x, y, 'X')

            self.__ships[cell] -= 1
            if self.__ships[cell] == 0:
                if cell in self.SHIP_NAMES:
                    sunk_ship = self.SHIP_NAMES[cell]
                    print(f'Sunk {sunk_ship}!')

                del self.__ships[cell]

            print(self.__ships)

            if not self.__ships:
                self.__client.defeat()
                self.__playing.clear()
            else:
                self.__client.hit()


def main():
    game = Game(timeout=0.15)
    game.setup()
    game.start()


if __name__ == '__main__':
    main()
