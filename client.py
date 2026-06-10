from socket import *
import sys
import json
import threading
from rich.table import Table
from rich import print
from rich.columns import Columns

placement_phase = threading.Event()
ships = ["carrier","battleship","cruiser","submarine","destroyer"]
shot_board = [["•" for _ in range(10)] for _ in range(10)]

placement_response = threading.Event()
last_result = [None]         #RETURN TO THIS

game_start = threading.Event()

my_turn = threading.Event()
shot_response = threading.Event()
last_shot_result = [None]

last_message = " "
my_grid = [None]

client_socket = socket(AF_INET, SOCK_STREAM)
server_name = input("input the IP address to be used: ")
server_port = int(input("enter the port number to be used: "))

server_address = (server_name, server_port)
print('connecting to server at %s port %s' % server_address)
client_socket.connect(server_address)

def display(grid, second_grid = None):
    table1 = Table(title="My Board")
    table1.add_column(" ")  # for row letters
    for i in range(1, 11):
        table1.add_column(str(i))
    
    letters = "ABCDEFGHIJ"
    for i in range(10):
        table1.add_row(letters[i], *grid[i])

    if second_grid:
        table2 = Table(title="Shot Tracker")
        table2.add_column(" ")
        for i in range(1, 11):
            table2.add_column(str(i))
        for i in range(10):
            table2.add_row(letters[i], *second_grid[i])
        print(Columns([table1, table2]))
    else:
        print(table1)

def listen():
    global last_message
    global my_grid
    while True:
        try:
            data = client_socket.recv(4096)
            msg = json.loads(data.decode())
            if msg["type"] == "message":
                print(msg["content"])
            elif msg["type"] == "start_placing":
                display(msg["grid"])
                my_grid = msg["grid"]
                placement_phase.set()
            elif msg["type"] == "place_result":
                last_result[0] = msg["content"]
                display(msg["grid"])  
                my_grid = msg["grid"]
                placement_response.set()
            elif msg["type"] == "onedone":
                print(msg["content"])
            elif msg["type"] == "game_starting":
                print(msg["content"])
                game_start.set()
            elif msg["type"] == "your_turn":
                print("Your turn")
                if "grid" in msg:
                    display(msg["grid"])
                    my_grid = msg["grid"]
                my_turn.set()
            elif msg["type"] == "shot_result":
                last_shot_result[0] = msg["content"]
                print(msg["message"])
                last_message = msg["message"]
                shot_response.set()


        except Exception as e:
            print("listener error:", e)
            break
        

listener = threading.Thread(target=listen)
listener.daemon = True
listener.start()


placement_phase.wait()
print("please begin placing your ships\nPlease enter the starting coordinate aswell as direction\nEXAMPLE: \nC4\nH")
for ship in ships:
    last_result[0] = None
    while last_result[0] != "ship placed successfully":
        print(ship,":")
        coord = str(input("Coordinate:"))
        direction = str(input("Direction:"))
        msg = {"type": "place", "ship_type": ship, "position": coord, "direction":direction}
        client_socket.send(json.dumps(msg).encode())
        placement_response.wait()
        placement_response.clear()
        print(last_result[0])
msg = {"type": "done_placing"}
client_socket.send(json.dumps(msg).encode())
game_start.wait()

while True:
    my_turn.wait()
    last_shot_result[0] = None
    while last_shot_result[0] != "valid":
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



