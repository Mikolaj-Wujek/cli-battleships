from socket import *
import sys
import json
import threading
from rich.table import Table
from rich import print

placement_phase = threading.Event()
ships = ["carrier","battleship","cruiser","submarine","destroyer"]

placement_response = threading.Event()
last_result = [None]         #RETURN TO THIS

game_start = threading.Event()

client_socket = socket(AF_INET, SOCK_STREAM)
server_name = input("input the IP address to be used: ")
server_port = int(input("enter the port number to be used: "))

server_address = (server_name, server_port)
print('connecting to server at %s port %s' % server_address)
client_socket.connect(server_address)

def display(grid):
    table = Table()
    table.add_column(" ")  # for row letters
    for i in range(1, 11):
        table.add_column(str(i))
    
    letters = "ABCDEFGHIJ"
    for i in range(10):
        table.add_row(letters[i], *grid[i])
    
    print(table)

def listen():
    while True:
        try:
            data = client_socket.recv(4096)
            msg = json.loads(data.decode())
            if msg["type"] == "message":
                print(msg["content"])
            elif msg["type"] == "start_placing":
                display(msg["grid"])
                placement_phase.set()
            elif msg["type"] == "place_result":
                last_result[0] = msg["content"]
                display(msg["grid"])
                placement_response.set()
            elif msg["type"] == "onedone":
                print(msg["content"])
            elif msg["type"] == "game_starting":
                print(msg["content"])
                game_start.set()
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




