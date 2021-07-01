import logging
import os
import random
import time
from breezypythongui import EasyFrame
from battlefield import Battlefield
from battlefield_ui import BattlefieldUI
from battleship_client import BattleshipClient

# Without this, nothing shows up...
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')


class Game(EasyFrame):
    SIZE = 10
    SHIPS = {
        'A': 5, 'B': 4, 'S': 3, 's': 3, '5': 3,
        'C': 3, 'D': 2, 'd': 2, 'P': 1, 'p': 1,
    }

    SHIP_NAMES = {
        'A': 'Aircraft Carrier',
        'B': 'Battleship',
        'S': 'Submarine', 's': 'Submarine', '5': 'Submarine',
        'C': 'Cruiser',
        'D': 'Destroyer', 'd': 'Destroyer',
        'P': 'Patrol Boat', 'p': 'Patrol Boat',
    }

    def __init__(self, timeout=1.0, mirrored=False, vertical=False, smart_ai=False):
        EasyFrame.__init__(self, 'Battleships')

        self.__smart_ai = smart_ai

        # Get a copy of the ships
        self.__ships = self.SHIPS.copy()

        self.__mine = Battlefield(colour=193)
        self.__opponent = Battlefield(colour=208)

        self.__mine_ui = BattlefieldUI(self, width=400, height=400, size=self.SIZE)
        self.__opponent_ui = BattlefieldUI(self, width=400, height=400, size=self.SIZE,
                                           colour='lightgreen')

        fields = []
        if not mirrored:
            fields.append(self.__opponent_ui)
            fields.append(self.__mine_ui)
        else:
            fields.append(self.__mine_ui)
            fields.append(self.__opponent_ui)

        for i in range(len(fields)):
            field = fields[i]
            if vertical:
                self.addCanvas(field, row=i, column=0)
            else:
                self.addCanvas(field, row=0, column=i)

        self.__timeout = abs(timeout)
        self.__attack_vector = None, None

        self.__client = self.__create_grpc_client()
        self.__client.join()

    def __create_grpc_client(self):
        """
        Create BattleshipClient that communicates with Game Server.
        """
        client = BattleshipClient(grpc_host=grpc_host, grpc_port=grpc_port)

        # Assign event handlers
        client.add_event_listener('begin', self.begin)
        client.add_event_listener('start_turn', self.start_my_turn)
        client.add_event_listener('end_turn', self.end_my_turn)
        client.add_event_listener('hit', self.hit)
        client.add_event_listener('miss', self.miss)
        client.add_event_listener('win', self.won)
        client.add_event_listener('lose', self.lost)
        client.add_event_listener('attack', self.attacked)
        return client

    def clear(self):
        """
        Clear all data related to the game so we can start a new game.
        """
        self.__mine.clear()
        self.__mine_ui.clear()

        self.__opponent.clear()
        self.__opponent_ui.clear()

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
                        ship_name = self.SHIP_NAMES[ship][0]
                        self.__mine_ui.update_at(x, y, ship_name)
                    break

    def start(self):
        self.mainloop()

    def begin(self):
        logger.info("The game has started!")

    def start_my_turn(self):
        logger.info("Okay, it's my turn now.")
        time.sleep(self.__timeout)
        while True:
            try:
                self.__attack_nearby_cell()
                return
            except ValueError:
                col = random.randint(0, 9)
                row = random.randint(0, 9)

                cell = self.__opponent.get_by_col_row(col, row)
                if cell is None:
                    self.__attack_cell(col, row)
                    return

    def __attack_cell(self, col, row):
        """
        Attack the opponent at location ({col}, {row}).
        """
        self.__attack_vector = col, row
        x, y = self.__mine.to_coords(col, row)
        vector = f'{x}{y}'
        logger.info(f'Attacking on {vector}.')
        self.__client.attack(vector)

    def __attack_nearby_cell(self):
        """
        This method attacks a nearby cell based on an earlier hit. The
        position of the hit is maintained in the instance variable
        {__attack_vector}. The AI will try to find an empty location
        close to the latest successful attack. If no empty locations
        exist, it will raise a ValueError.
        """
        col, row = self.__attack_vector
        if self.__smart_ai and not (col is None or row is None):
            relative_cells = [(-1, 0), (0, -1), (1, 0), (0, 1)]

            # Shuffling may not make much of a difference...
            random.shuffle(relative_cells)
            for dx, dy in relative_cells:
                dcol, drow = col + dx, row + dy
                if not (0 <= dcol < self.SIZE and 0 <= drow < self.SIZE):
                    # Off the grid, so move to the next one
                    continue

                cell = self.__opponent.get_by_col_row(dcol, drow)
                if cell is None:
                    logger.info(f'Nearby empty cell @ ({col},{row}) found.')
                    self.__attack_cell(dcol, drow)
                    return

        raise ValueError

    def end_my_turn(self):
        logger.info("Okay, my turn has ended.")

    def hit(self):
        logger.info("Success!")
        self.__opponent.set_by_col_row(*self.__attack_vector, 'X')
        self.__opponent_ui.update_at(*self.__attack_vector, '\u2716', colour='red')
        # Don't reset attack vector so AI will try to attack a nearby position

    def miss(self):
        logger.info("No luck.")
        dot = '\u25CB'
        self.__opponent.set_by_col_row(*self.__attack_vector, dot)
        self.__opponent_ui.update_at(*self.__attack_vector, dot, colour='blue')

        # Reset the attack vector so next attack will be at random position
        self.__attack_vector = None, None

    def won(self):
        logger.info("I won!!!")

    def lost(self):
        logger.info("Meh. I lost.")

    def attacked(self, vector):
        # Get rid of any whitespace
        vector = vector.strip()

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
            self.__mine_ui.update_at(col, row, '\u2716', colour='red')

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


def main():
    mirrored = os.getenv('MIRRORED', False)
    vertical = os.getenv('VERTICAL', False)
    smart_ai = os.getenv('SMART_AI', False)

    game = Game(timeout=0.25, mirrored=mirrored, vertical=vertical, smart_ai=smart_ai)
    game.setup()
    game.start()


if __name__ == '__main__':
    main()
