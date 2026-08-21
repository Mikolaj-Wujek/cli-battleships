#client

from socket import *
import sys
import json
import threading
from collections import deque
from rich.table import Table
from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel

placement_phase = threading.Event()
ships = ["carrier","battleship","cruiser","submarine","destroyer"]
shot_board = [["•" for _ in range(10)] for _ in range(10)]

placement_response = threading.Event()
last_result = [None]         #RETURN TO THIS

game_start = threading.Event()

my_turn = threading.Event()
shot_response = threading.Event()
last_shot_result = [None]

connection_lost = threading.Event()

last_message = " "
my_grid = [["•" for _ in range(10)] for _ in range(10)]  # placeholder until real grid arrives

console = Console()

client_socket = socket(AF_INET, SOCK_STREAM)
server_name = console.input("input the IP address to be used: ")
server_port = int(console.input("enter the port number to be used: "))

server_address = (server_name, server_port)
console.print('connecting to server at %s port %s' % server_address)
client_socket.connect(server_address)

messages = deque(maxlen=6)  # persistent log, oldest lines drop off as new ones arrive

def build_boards(grid, second_grid):
    table1 = Table(title="My Board")
    table1.add_column(" ")  # for row letters
    for i in range(1, 11):
        table1.add_column(str(i))

    letters = "ABCDEFGHIJ"
    for i in range(10):
        table1.add_row(letters[i], *grid[i])

    table2 = Table(title="Shot Tracker")
    table2.add_column(" ")
    for i in range(1, 11):
        table2.add_column(str(i))
    for i in range(10):
        table2.add_row(letters[i], *second_grid[i])

    log_panel = Panel("\n".join(messages) if messages else "", title="Game Log")

    return Group(Columns([table1, table2]), log_panel)

def redraw(grid, second_grid=None):
    """Clears the terminal and reprints the boards + log from scratch, so
    there's nothing stale left over from the previous frame."""
    if second_grid is None:
        second_grid = shot_board
    console.clear()
    console.print(build_boards(grid, second_grid))

def display(grid, second_grid=None):
    """Updates the board display."""
    redraw(grid, second_grid)

def log(text):
    """Adds a line to the persistent on-screen game log and redraws."""
    messages.append(text)
    redraw(my_grid, shot_board)

redraw(my_grid, shot_board)  # initial draw so boards are visible before any server messages

def listen():
    global last_message
    global my_grid
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                raise ConnectionError("server closed the connection")
            msg = json.loads(data.decode())
            if msg["type"] == "message":
                log(msg["content"])
            elif msg["type"] == "start_placing":
                my_grid = msg["grid"]
                display(my_grid)
                placement_phase.set()
            elif msg["type"] == "place_result":
                last_result[0] = msg["content"]
                my_grid = msg["grid"]
                display(my_grid)
                log(msg["content"])
                placement_response.set()
            elif msg["type"] == "onedone":
                log(msg["content"])
            elif msg["type"] == "game_starting":
                log(msg["content"])
                game_start.set()
            elif msg["type"] == "your_turn":
                log("Your turn")
                if "grid" in msg:
                    my_grid = msg["grid"]
                display(my_grid)
                my_turn.set()
            elif msg["type"] == "shot_result":
                last_shot_result[0] = msg["content"]
                log(msg["message"])
                last_message = msg["message"]
                shot_response.set()


        except Exception as e:
            log(f"listener error: {e}")
            log("connection to server lost. exiting.")
            connection_lost.set()
            placement_phase.set()
            placement_response.set()
            game_start.set()
            my_turn.set()
            shot_response.set()
            break
        

listener = threading.Thread(target=listen)
listener.daemon = True
listener.start()


def exit_client():
    sys.exit(1)

placement_phase.wait()
if connection_lost.is_set():
    exit_client()
log("please begin placing your ships. Enter the starting coordinate then direction, e.g. C4 then H")
for ship in ships:
    last_result[0] = None
    while last_result[0] != "ship placed successfully":
        if connection_lost.is_set():
            exit_client()
        coord = str(input(f"{ship} - Coordinate: "))
        direction = str(input(f"{ship} - Direction: "))
        msg = {"type": "place", "ship_type": ship, "position": coord, "direction":direction}
        client_socket.send(json.dumps(msg).encode())
        placement_response.wait()
        placement_response.clear()
        if connection_lost.is_set():
            exit_client()
msg = {"type": "done_placing"}
client_socket.send(json.dumps(msg).encode())
game_start.wait()
if connection_lost.is_set():
    exit_client()

while True:
    my_turn.wait()
    if connection_lost.is_set():
        exit_client()
    last_shot_result[0] = None
    while last_shot_result[0] != "valid":
        if connection_lost.is_set():
            exit_client()
        shot = str(input("enter your shot coordinates:"))
        msg = {"type": "shot", "position": shot}
        client_socket.send(json.dumps(msg).encode())
        shot_response.wait()
        shot_response.clear()
    row = ord(shot[0].upper()) - ord('A')
    col = int(shot[1:]) - 1
    shot_board[row][col] = "X" if last_message == "hit" else "O"
    display(my_grid, shot_board)
    my_turn.clear()