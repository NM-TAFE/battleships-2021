import os
import threading
import time
from battleship_client import BattleshipClient
import board
import ship

grpc_host = os.getenv('GRPC_HOST', 'localhost')
grpc_port = os.getenv('GRPC_PORT', '50051')

playing = threading.Event()
playing.set()

battleship = BattleshipClient(grpc_host=grpc_host, grpc_port=grpc_port)

player1 = board.player1_table()
player2 = board.player2_table()


def clear():
    print("\n" * 100)


@battleship.on()
def begin():
    print('Game started!')


@battleship.on()
def start_turn():
    print("\n")
    s = input('Your move> ')
    global my_attack
    my_attack = s
    battleship.attack(s)


@battleship.on()
def end_turn():
    print('End turn')


@battleship.on()
def hit():
    row = my_attack[0].upper()
    col = int(my_attack[1:]) - 1
    player2[row][col] = "Hit"
    clear()
    board.display_grid(player1, player2)
    print('\n\nYou hit the target!')


@battleship.on()
def miss():
    row = my_attack[0].upper()
    col = int(my_attack[1:]) - 1
    player2[row][col] = "Miss"
    clear()
    board.display_grid(player1, player2)
    print('\n\nAww.. You missed!')


@battleship.on()
def win():
    print('Yay! You won!')
    playing.clear()


@battleship.on()
def lose():
    print('Aww... You lost...')
    playing.clear()


@battleship.on()
def attack(vector):
    print(vector)
    position = vector[0].upper()
    row = position[0]
    col = int(position[1:]) - 1
    if row in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
        print(f"\n Shot received at {position}")
        if player1[row][col] in [" ", "Miss"]:
            player1[row][col] = "Miss"
            """Send Miss event"""
            battleship.miss()
        else:
            player1[row][col] = "Hit"
            """Send Hit Or Defeat Event"""
            board.display_grid(player1, player2)
            print("""\n\nAll Ships Sunk? Y/N""")
            answer = input("Enter Y or N: ")
            if answer[0].upper() == 'Y':
                battleship.defeat()
            else:
                battleship.hit()
        board.display_grid(player1, player2)
    else:
        board.display_grid(player1, player2)
        print(f"\nEnemy sending attack coordinate outside of grid value :::{vector[0]}")
        battleship.miss()


if __name__ == '__main__':
    board.display_grid(player1, player2)
    player_table = ship.placement(player1, player2)
    board.display_grid(player_table, player2)
    while True:
        s = input("\nReady to join? Y/N : ")
        if s[0].upper() == 'Y':
            break
        else:
            continue
    print('\nWaiting for the game to start...')
    battleship.join()
    while playing.is_set():
        time.sleep(1.0)
