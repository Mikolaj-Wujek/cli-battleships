from socket import *

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

while True:
    data = conn1.recv(1024)
    conn2.send(data)

    data = conn2.recv(1024)
    conn1.send(data)