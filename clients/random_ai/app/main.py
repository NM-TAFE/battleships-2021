from datetime import datetime
import logging
import os
import random
import time
from breezypythongui import EasyFrame
from battlefield import Battlefield
from battlefield_ui import BattlefieldUI
from battleship_client import BattleshipClient

logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

        self.__frame = EasyFrame('Battleships')

        self.__mine_ui = BattlefieldUI(self.__frame, width=400, height=400, size=10)
        self.__frame.addCanvas(self.__mine_ui, row=0, column=0)

        self.__opponent_ui = BattlefieldUI(self.__frame, width=400, height=400, size=10,
                                           colour='lightgreen')
        self.__frame.addCanvas(self.__opponent_ui, row=0, column=1)

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

        self.join()

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
                result = self.__mine.place_ship(ship, x, y, size, horizontal=o)
                if result is not None:
                    for x, y in result:
                        self.__mine_ui.update_at(x, y, ship)
                    break

        logger.info(self.__mine)
        logger.info(self.__opponent)

    def join(self):
        print('Waiting for the game to start...')
        self.__client.join()

    def start(self):
        self.__frame.mainloop()
        while True:
            time.sleep(1)

    def begin(self):
        logger.info("The game has started!")

    def start_turn(self):
        logger.info("Okay, it's my turn now.")
        time.sleep(self.__timeout)
        while True:
            col = random.randint(0, 9)
            row = random.randint(0, 9)
            cell = self.__opponent.get_by_col_row(col, row)
            if cell is None:
                self.__attack_vector = col, row
                x, y = self.__mine.to_coords(col, row)
                vector = f'{x}{y}'
                logger.info(f'Attacking on {vector}.')
                self.__client.attack(vector)
                break

    def end_turn(self):
        logger.info("Okay, my turn has ended.")

    def hit(self):
        logger.info("Success!")
        self.__opponent.set_by_col_row(*self.__attack_vector, 'X')
        self.__opponent_ui.update_at(*self.__attack_vector, 'X')
        print('Their board:')
        print(self.__opponent)

    def miss(self):
        logger.info("No luck.")
        self.__opponent.set_by_col_row(*self.__attack_vector, '.')
        self.__opponent_ui.update_at(*self.__attack_vector, '.')
        print('Their board:')
        print(self.__opponent)

    def won(self):
        logger.info("I won!!!")

    def lost(self):
        logger.info("Meh. I lost.")

    def attacked(self, vector):
        logger.info(f"Oi! Getting attacked on {vector}")
        x, y = vector[0], int(vector[1:])
        cell = self.__mine.get(x, y)
        if cell is None:
            self.__client.miss()
        elif cell == '@':
            logger.info('THIS SHOULD NOT HAPPEN!')  # Voiceover: "it happened."
            self.__client.miss()
        else:
            logger.info("I'm hit!")
            self.__mine.set(x, y, 'X')
            col, row = self.__mine.from_coords(x, y)
            self.__mine_ui.update_at(col, row, 'X')

            self.__ships[cell] -= 1
            if self.__ships[cell] == 0:
                if cell in self.SHIP_NAMES:
                    sunk_ship = self.SHIP_NAMES[cell]
                    logger.info(f'Sunk {sunk_ship}!')

                del self.__ships[cell]

            if not self.__ships:
                self.__client.defeat()
            else:
                self.__client.hit()

        logger.info('My board:')
        logger.info(self.__mine)


def main():
    start = datetime.now()
    game = Game(timeout=0.0)
    game.setup()
    game.start()
    elapsed = round((datetime.now() - start).total_seconds())
    logger.info(f'Time take for game: {elapsed} seconds.')


if __name__ == '__main__':
    main()
