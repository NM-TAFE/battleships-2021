class BattleBoard:
    """
    This class holds information on a 10x10 battleship grid.
    It also contains function handling attacks, ship placement and game status.
    """
    # @D array for 10 by 10 grid to be played on
    board = [[".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
             [".", ".", ".", ".", ".", ".", ".", ".", ".", "."]]

    # array that represents to total rows in the 10 x 10 grid
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    def set_board(self):
        """
            This method allows the user to sets the boats into the grid.
        """
        # dictionary of ships with names and length
        ships = {
            "Carrier": 5,
            "Battleship": 4,
            "Submarine(1)": 3,
            "Submarine(2)": 3,
            "Submarine(3)": 3,
            "Cruiser": 3,
            "Destroyer(1)": 2,
            "Destroyer(2)": 2,
            "Patrol(1)": 1,
            "Patrol(2)": 1
        }
        # Iterates through the dictionary to place ship into user assigned location
        for ship in ships:
            placed = False
            while not placed:
                try:
                    placed, orientation, length, row, column = self.check_placement(ship, ships)
                except TypeError:
                    placed = False
                    view = input("Would you like to view your game board Y/N: \n").upper()
                    if view in ["Y", "YES"]:
                        self.view_board()
                    else:
                        continue
                if placed:
                    # Places the user ship in the chosen area
                    placed = self.place_ship(orientation, length, row, column)

        print("All Ships placed successfully")

    def view_board(self):
        """
        Prints the board
        """
        for i in self.board:
            print(i)

    def check_placement(self, ship, ships):
        """
            This method checks the users grid placement.
        """
        # Takes user inputs
        ship_placement = \
            input("Where would you like to place your " + ship + "\nIt is " + str(
                ships[ship]) + " grid long:\n").upper()
        ship_orientation = input("Horizontal or Vertical: \n").upper()

        # Checks if the user entered an appropriate orientation
        if ship_orientation[0] not in "HV":
            print("Invalid orientation entered, try again")
            return False

        # Checks the users coordinates are valid
        target_column, target_row = self.check_grid_choice(ship_placement)

        # Checks if the users choice is within the bounds of the grid
        if ship_orientation[0] == "H":
            if ships[ship] + target_column > 11:
                print("Not enough room on board, try again")
                return False
            else:
                return True, ship_orientation[0], ships[ship], target_row, target_column
        if ship_orientation[0] == "V":
            if ships[ship] + target_row > 11:
                print("Not enough room on board, try again")
                return False
            else:
                return True, ship_orientation[0], ships[ship], target_row, target_column

    def place_ship(self, orientation, length, target_row, target_column):
        """
            Places the ship on the board, at the user's selected grid location.
        """
        # Minus one as array index starts at 0
        row = target_row - 1
        column = target_column - 1

        grid_free = True
        # Checks the given orientation
        if orientation == "H":
            # Checks if the grids are already filled from a ship
            for i in range(length):
                if self.board[row][column + i] != ".":
                    print("Grid space already filled")
                    return False
            # Places the ship on the grid, ships assigned to 'B'
            if grid_free:
                for grid in range(length):
                    self.board[row][column + grid] = "B"
                print("Ship has been placed")
                return True
        else:
            # Checks if the grids are already filled from a ship
            for i in range(length):
                if self.board[row + i][column] != ".":
                    print("Grid space already filled")
                    return False
            # Places the ship on the grid, ships assigned to 'B'
            if grid_free:
                for grid in range(length):
                    self.board[row + grid][column] = "B"
                print("Ship has been placed")
                return True

    def check_grid_choice(self, target):
        """
            Checks the user given coordinates. See's if they have been previously filled.
            Previously attacked or ship placed at the coordinates.
        """
        # Checks the coordinates are within acceptable parameters
        if len(target) not in [2, 3, 4] or target[0] not in self.rows:
            print("Chosen coordinates are out of range or invalid. Try again.")
            return False

        try:
            # Converts coordinates string into integers
            target_column = int(target[1:])
            target_row = ord(target[0]) - 64  # 64 is (ord("A") + 1) creating our 1 row point in the grid

        # Catch exception when values cant be converted to integers
        except ValueError:
            print("Invalid Coordinate entered, try again")
            return False

        # Checks that the converted values are within the bounds of the board
        if target_column not in range(1, 11) or target_row not in range(1, 11):
            print("Coordinates given out of range")
            return False
        else:
            return target_column, target_row

    def send_attack(self):
        """
            Validate user's attack.
            returns the user entered string and converted integer values as a tuple.
        """
        successful_attack = False
        while not successful_attack:
            attack = input("Enter your attack: \n").upper()
            try:
                # Converts user input into integers
                target_column, target_row = self.check_grid_choice(attack)
            # Catches invalid input
            except TypeError:
                print("Invalid attack entered, try again.")
                continue
            else:
                # Checks the entered grid has not been previously attacked
                if self.board[target_row - 1][target_column - 1] == ".":
                    print("Sending attack to opponent.")
                    return attack, (target_column, target_row)
                else:
                    print("You've already attacked that grid. Try again.")
                    continue

    def record_attack(self, target, hit):
        """
            Records the attack on the grid.
        """
        if hit:
            print("Successful attack, enemy hit")
            self.board[target[1] - 1][target[0] - 1] = "X"
        else:
            print("Your attack missed")
            self.board[target[1] - 1][target[0] - 1] = "O"

    def receive_attack(self, target):
        """
            Checks the user's grid with the received attack from enemy.
        """
        print(f"Enemy attack at {target}")
        # Checks the first value is uppercase and converts if not
        if not target[0].isupper():
            _target = target[0].upper() + target[1:]
        else:
            _target = target
        # Converts enemy coordinates to integer
        try:
            target_column, target_row = self.check_grid_choice(_target)
        except ValueError:
            print("Enemy attack invalid. Missed")
            return False
        else:
            # Minus one as array index starts at 0
            target_row = target_row - 1
            target_column = target_column - 1
            # Checks the user's board for a ship
            if self.board[target_row][target_column] == "B":
                print("Enemy attack successful.")
                self.board[target_row][target_column] = "X"
                return True
            else:
                self.board[target_row][target_column] = "O"
                print("Enemy attack missed.")
                return False

    def check_defeat(self):
        """
            Checks whether the user has been defeated. All ships have been destroyed.
        """
        for i in self.board:
            for j in i:
                if j == "B":
                    print("Not defeated, continue")
                    return True
        print("Defeated")
        return False

