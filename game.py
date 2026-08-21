#game

from rich.table import Table
from rich import print

class Board:
    def __init__(self):
        self.grid = [["•" for _ in range(10)] for _ in range(10)]
        self.ships = {
            "carrier": 5,
            "battleship": 4,
            "cruiser": 3,
            "submarine": 3,
            "destroyer": 2
        }

    def parse_position(self, position):
        """Returns (row, col) on success, or None if invalid."""
        if not position or len(position) < 2:
            return None
        letter = position[0].upper()
        if letter not in "ABCDEFGHIJ":
            return None
        try:
            col = int(position[1:]) - 1
        except ValueError:
            return None
        row = ord(letter) - ord('A')
        if not (0 <= row < 10) or not (0 <= col < 10):
            return None
        return row, col

    def place_ship(self, ship_type, position, direction):
        parsed = self.parse_position(position)
        if parsed is None:
            return "ship placed out of bounds"
        row, col = parsed

        size = self.ships[ship_type]
        direction = direction.upper()

        if direction == "H":
            if (col + size) >= 10:
                return "ship placed out of bounds"
        elif direction == "V":
            if (row + size) >= 10:
                return "ship placed out of bounds"
        
        for coord in range(size):
            if direction == "H":
                if self.grid[row][col+coord] == "S":
                    return f"there is already a ship at {row}, {col}"
            elif direction == "V":
                if self.grid[row+coord][col] == "S":
                    return f"there is already a ship at {row}, {col}"

        

        if direction == "H":
            coords = [(row, col + i) for i in range(size)]
        else:
            coords = [(row + i, col) for i in range(size)]

        for r, c in coords:
            self.grid[r][c] = "S"
        return "ship placed successfully"
    
    def receive_shot(self, position):
        parsed = self.parse_position(position)
        if parsed is None:
            return "shot placed out of bounds"
        row, col = parsed

        if self.grid[row][col] == "S":
            self.grid[row][col] = "X"
            return "hit"
        elif self.grid[row][col] == "•":
            self.grid[row][col] = "O"
            return "miss"
        else:
            return "already shot"
        
    def is_game_over(self):
        for i in range(10):
            for j in range(10):
                if self.grid[i][j] == "S":
                    return False
        return True

    
    def display(self):
        table = Table()
        table.add_column(" ")  # for row letters
        for i in range(1, 11):
            table.add_column(str(i))
        
        letters = "ABCDEFGHIJ"
        for i in range(10):
            table.add_row(letters[i], *self.grid[i])
        
        print(table)

if __name__ == "__main__":
    b = Board()
    print(b.is_game_over())
    b.place_ship("destroyer","C3","H")
    print(b.is_game_over())

    b.display()


    #DIRECTION DEFAULT VERTICAL : FIX?