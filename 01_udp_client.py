import socket

target_host = "www.google.com"
target_port = 80

#Instance socket object

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Send data over

client.sendto("AAABBBCCC", (target_host, target_port))

#Receive data

data, addr = client.recvfrom(4096)

print(data)