from socket import *
import game
import threading
import json

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

def handle_client(conn, other_conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print("a player disconnected")
            break
        msg = json.loads(data.decode())
        other_conn.send(json.dumps(msg).encode())

t1 = threading.Thread(target=handle_client, args=(conn1, conn2))
t2 = threading.Thread(target=handle_client, args=(conn2, conn1))
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

t1.join()
t2.join()