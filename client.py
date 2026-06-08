from socket import *
import sys

client_socket = socket(AF_INET, SOCK_STREAM)
server_name = input("input the IP address to be used: ")
server_port = int(input("enter the port number to be used: "))

server_address = (server_name, server_port)
print('connecting to server at %s port %s' % server_address)
client_socket.connect(server_address)

while True:
    message = input("enter message:")
    client_socket.send(message.encode())

    response = client_socket.recv(1024)
    print(f"recieved: {response.decode()}")