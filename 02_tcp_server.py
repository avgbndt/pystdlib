import socket
import threading

#Setup

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print(f"[*] Listening on {bind_ip} : {bind_port}")

#Client Handling Thread

def handle_client(client_socket):

	#Print out what the client sends
	request = client_socket.recv(1024)

	print(f"Received: {request}")

	#Send back a packet
	client_socket.send(b"ACK!")

	client_socket.close()

while True:
	
	client, addr = server.accept()
	
	print(f"[*] Accepted connection from: {addr[0], addr[1]}")

	#Spin up client handler
	client_handler = threading.Thread(target=handle_client, args=(client,))
	client_handler.start()
