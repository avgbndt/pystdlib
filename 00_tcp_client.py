import socket

target_host = "127.0.0.1"
target_port = 9999

#Instance socket object

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect the client

client.connect((target_host, target_port))

#Send over some data

client.send(b"ABC123")

#Receive data

response = client.recv(4096)

print(response)