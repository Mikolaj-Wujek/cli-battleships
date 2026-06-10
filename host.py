from socket import *
import game
import threading
import json

players_ready = [0]
current_turn = [1]

server_socket = socket(AF_INET, SOCK_STREAM)
port = 6789
hostname = gethostname()
serverName = gethostbyname(hostname)

server_address = (serverName, port)
print('*** Server is starting up on %s port %s ***' % server_address)
server_socket.bind(('', port))

server_socket.listen(2)

print("waiting for player 1...")
conn1, addr1 = server_socket.accept()
print("player 1 connected:", addr1)

print("waiting for player 2...")
conn2, addr2 = server_socket.accept()
print("player 2 connected:", addr2)

p1_board = game.Board()
p2_board = game.Board()

grid = p1_board.grid

start_msg = {"type": "start_placing", "grid": grid}
conn1.send(json.dumps(start_msg).encode())
conn2.send(json.dumps(start_msg).encode())


def handle_client(conn, other_conn, my_board, other_board, player):
    while True:
        global players_ready
        data = conn.recv(4096)
        if not data:
            print("a player disconnected")
            break
        msg = json.loads(data.decode())

        if msg["type"] == "place":
            result = my_board.place_ship(msg["ship_type"],msg["position"],msg["direction"])
            grid = my_board.grid
            new_msg = {"type": "place_result", "content": result, "grid": grid}
            conn.send(json.dumps(new_msg).encode())
        elif msg["type"] == "done_placing":
            players_ready[0] += 1
            if players_ready[0] != 2:
                new_msg = {"type": "onedone", "content": "waiting on other player to place ships"}
                conn.send(json.dumps(new_msg).encode())
            else:
                new_msg = {"type": "game_starting", "content": "starting game, good luck!"}
                conn.send(json.dumps(new_msg).encode())
                other_conn.send(json.dumps(new_msg).encode())
                new_msg = {"type": "your_turn"}
                conn1.send(json.dumps(new_msg).encode())
                new_msg = {"type": "message", "content": "other players turn..."}
                conn2.send(json.dumps(new_msg).encode())

        elif msg["type"] == "shot":
            if current_turn[0] != player:
                continue
            result = other_board.receive_shot(msg["position"])
            if result not in ["hit", "miss"]:
                new_msg = {"type": "shot_result", "content": "invalid", "message": result}
                conn.send(json.dumps(new_msg).encode())
                continue
            new_msg = {"type": "shot_result", "content": "valid", "message": result}
            conn.send(json.dumps(new_msg).encode())
            current_turn[0] = 2 if player == 1 else 1
            grid = other_board.grid
            new_msg = {"type": "your_turn", "grid": grid}
            other_conn.send(json.dumps(new_msg).encode())




t1 = threading.Thread(target=handle_client, args=(conn1, conn2, p1_board, p2_board, 1))
t2 = threading.Thread(target=handle_client, args=(conn2, conn1, p2_board, p1_board, 2))
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

t1.join()
t2.join()