from socket import *
import sys
import json
import threading

client_socket = socket(AF_INET, SOCK_STREAM)
server_name = input("input the IP address to be used: ")
server_port = int(input("enter the port number to be used: "))

server_address = (server_name, server_port)
print('connecting to server at %s port %s' % server_address)
client_socket.connect(server_address)

def listen():
    while True:
        data = client_socket.recv(1024)
        msg = json.loads(data.decode())
        print(msg["content"])

listener = threading.Thread(target=listen)
listener.daemon = True
listener.start()

while True:
    message = input()
    msg = {"type": "message", "content": message}
    client_socket.send(json.dumps(msg).encode())