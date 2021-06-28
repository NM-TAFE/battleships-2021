def display_grid(player, enemy):
    """
    Display Grid to console
    """
    table_head = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print("\n\n\n" + " " * 25 + " Your Table" + " " * 100 + "Enemy Table")
    print(" " * 5, end="|")

    # Grid Header
    for i in table_head:
        print(f"{i:^5}", end="|")
    print(" " * 49, end="|")
    for i in table_head:
        print(f"{i:^5}", end="|")

    # Grid Table
    for key in player:
        print(f"\n\n{key:^5}", end="|")
        for item in player[key]:
            print(f"{item:^5}", end="|")

        print(" " * 45, end="")
        print(key, end="   |")

        for item in enemy[key]:
            print(f"{item:^5}", end="|")


def player1_table():
    """
    Dictionary for table grid
    """
    return {"A": [" "] * 10, "B": [" "] * 10, "C": [" "] * 10, "D": [" "] * 10, "E": [" "] * 10,
            "F": [" "] * 10, "G": [" "] * 10, "H": [" "] * 10, "I": [" "] * 10, "J": [" "] * 10, }


def player2_table():
    return {"A": [" "] * 10, "B": [" "] * 10, "C": [" "] * 10, "D": [" "] * 10, "E": [" "] * 10,
            "F": [" "] * 10, "G": [" "] * 10, "H": [" "] * 10, "I": [" "] * 10, "J": [" "] * 10, }
