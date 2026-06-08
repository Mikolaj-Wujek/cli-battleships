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

    def place_ship(self, ship_type, position, direction):
        row = ord(position[0].upper()) - ord('A')
        if row > 9:
            return "ship placed out of bounds"
        col = int(position[1:]) - 1
        if col > 9:
            return "ship placed out of bounds"
        size = self.ships[ship_type]
        direction = direction.upper()

        if direction == "H":
            if (col + size) > 9:
                return "ship placed out of bounds"
        elif direction == "V":
            if (row + size) > 9:
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
    
    def receive_shot(self, row, col):
        if self.grid[row][col] == "S":
            self.grid[row][col] = "X"
            return True
        elif self.grid[row][col] == "•":
            self.grid[row][col] = "O"
            return False
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