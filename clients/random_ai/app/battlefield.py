import logging
import random
from colored import fg, attr

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)


class Battlefield:
    STANDARD_X = 10
    STANDARD_Y = 10

    def __init__(self, columns=STANDARD_X, rows=STANDARD_Y, colour=193):
        self.__columns = columns
        self.__rows = rows

        # Colour that the grid will be printed in
        self.__colour = colour

        # Initialize grid
        self.grid = [[None] * columns for _ in range(rows)]

    def clear(self):
        """
        Clear the data of the battlefield.
        """
        for col in range(self.__columns):
            for row in range(self.__rows):
                self.grid[col][row] = None

    def get(self, x, y):
        """
        Get the contents of the grid element at ({x}, {y})
        """
        return self.get_by_col_row(*self.from_coords(x, y))

    def get_by_col_row(self, col, row):
        """
        Get element from grid using normal column/row indexes
        """
        return self.grid[col][row]

    def set(self, x, y, val):
        """
        Set the contents of the grid element at ({x}, {y})
        to the value {val}.
        """
        self.set_by_col_row(*self.from_coords(x, y), val)

    def set_by_col_row(self, col, row, val):
        """
        Set the contents of the grid element at (col, row)
        to the value {val}.
        """
        self.grid[col][row] = val

    @staticmethod
    def from_coords(x, y):
        column = ord(x.upper()) - ord('A')
        row = y - 1
        return column, row

    @staticmethod
    def to_coords(col, row):
        x = chr(ord('A') + col)
        y = row + 1
        return x, y

    def place_ship(self, ship_type, x, y, size, horizontal=True):
        """
        Place a ship on the provided coordinates. The X
        coordinate is a letter (A, B, C, ...) while the Y
        coordinate is a number (1, 2, 3, ...).
        This translates the coordinates into indexes into
        the grid array then calls the method {__place_ship}.

        :param ship_type: Type of ship
        :param x: X-coordinate to place ship
        :param y: Y-coordinate to place ship
        :param size: Size of ship
        :param horizontal: Orientation of the ship
        :return: True if ship placed succesfully, False otherwise
        """
        column, row = self.from_coords(x, y)
        return self.__place_ship(ship_type, column, row, size, horizontal)

    def __place_ship(self, ship_type, column, row, size, horizontal):
        """
        Place a ship on the grid. It will automatically adjust
        if the ship is placed in a position where it wouldn't
        technically fit. It prevents ship from being positioned
        on top of each other.

        :param ship_type: Type of ship
        :param row: Row to place ship
        :param column: Column to place ship
        :param size: Size of ship
        :param horizontal: Orientation of the ship
        :return: True if ship placed succesfully, False otherwise
        """
        # Determine max value for row/column and starting row/column
        rc_max = self.STANDARD_X if horizontal else self.STANDARD_Y
        rc, rc_start = (row, column) if horizontal else (column, row)

        # Make sure ship fits on board by tweaking starting position
        delta = rc_start + size - rc_max
        if delta > 0:
            rc_start -= delta

        # Place ships making sure no two ships occupy same cell
        cells = []
        for i in range(rc_start, rc_start + size):
            x, y = (i, rc) if horizontal else (rc, i)
            if self.grid[x][y] is not None:
                # Oops, there's already a ship here!
                break

            # Update grid
            self.grid[x][y] = ship_type
            cells.append((x, y))
        else:
            # No ship had been placed on any of the cells yet
            return cells

        # Ship already exists on one of the cells...
        for cell in cells:
            x_, y_ = cell
            self.grid[x_][y_] = None

        return None

    def __str__(self):
        s = '     '
        s += '   '.join(chr(x + ord('A')) for x in range(self.STANDARD_X))
        s += '\n   '
        s += '+---' * self.STANDARD_X + '+\n'
        for y in range(self.STANDARD_Y):
            s += f'{y + 1:2} |'
            s += '|'.join(['   '
                           if self.grid[x][y] is None
                           else f' {self.grid[x][y][0]} '
                           for x in range(self.STANDARD_X)])
            s += '|\n'
            s += '   '
            s += '+---' * self.STANDARD_X + '+\n'

        s = '%s' + s + '%s'
        return s % (fg(self.__colour), attr(0))


def main():
    ships = {
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

    bf = Battlefield()  # Assume 10x10 field
    for ship in ships:
        size = ships[ship]
        while True:
            x = random.choice('ABCDEFGHIJ')
            y = random.randint(1, 10)
            o = random.choice([False, True])
            if bf.place_ship(ship, x, y, size, horizontal=o) is not None:
                break

    print(bf)

    opp = Battlefield(colour=208)
    print(opp)


def test():
    bf = Battlefield(colour=208)

    assert bf.place_ship('A', 'C', 4, size=5, horizontal=True) is not None
    assert bf.place_ship('D', 'E', 3, size=4, horizontal=False) is None
    assert bf.place_ship('D', 'E', 5, size=4, horizontal=False) is not None
    assert bf.place_ship('d', 'I', 9, size=4, horizontal=True) is not None
    assert bf.place_ship('S', 'E', 6, size=3, horizontal=True) is None
    assert bf.place_ship('S', 'B', 6, size=3, horizontal=True) is not None
    assert bf.place_ship('s', 'I', 1, size=3, horizontal=True) is not None
    assert bf.place_ship('B', 'C', 7, size=4, horizontal=False) is not None

    print('Test grid: \n')
    print(bf)


if __name__ == '__main__':
    # test()
    main()
