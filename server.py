import socket
import sys
import threading


class Server:

	def __init__(self, host='', port=8888, max_clients=10):
		self.host = host
		self.port = port
		self.max_clients = max_clients
		self.client_list = []
		self.address_list = []
		self.files_list = []

	# Function for handling connections. This will be used to create threads
	def client_thread(self, conn, addr):
		stop_char = '|'
		separation_char = '>'
		try:
			# Sending message to connected client
			print("GG")

			conn.sendall(('Welcome to the server.\n' + stop_char).encode('utf-8'))
			print("G")
			while True:
				# Receiving from client
				choice = ""
				data = ""
				while data != stop_char:
					data = conn.recv(1).decode('utf-8')
					if data == stop_char:
						break
					choice += data
				# reply = addr[0] + ':' + str(addr[1]) + ' sent: ' + choice + '\n'
				print(addr[0], ':', str(addr[1]), 'sent:', choice, '\n')

				# client disconnected
				if choice == 'exit':
					i = 0
					reply = addr[0] + ':' + str(addr[1]) + ' disconnected from server.\n|'
					for e in self.client_list:
						if e == conn:
							self.files_list[i] = []
							self.files_list.remove([])
							continue
						e.sendall(reply.encode('utf-8'))
						i += 1
					self.client_list.remove(conn)
					print(reply)
					break
	
				# upload list of files
				elif choice == 'up':
					i = 0
					# TO CHECK
					for e in self.client_list:
						if e == conn:
							self.files_list[i] = []
							word = ""
							while word != stop_char:
								data = ""
								word = ""
								while word != separation_char:
									word = conn.recv(1).decode('utf-8')
									if word == stop_char:
										break
									elif word == separation_char:
										self.files_list[i].append(data)
										break
									data = data+word
							print('File list has been updated:\n')
							print(self.files_list)
							break
						i += 1
					continue
				# downloading list of files
				elif choice == 'down':
					reply = '\nFiles list:'
					i = 0
					for e in self.client_list:
						if e == conn:
							i += 1
							continue
						reply += '\nClient' + str(i+1) + ': '
						for a in range(len(self.files_list[i])):
							reply += self.files_list[i][a] + ' '
						i += 1
					conn.sendall((reply+stop_char).encode('utf-8'))
					continue
				elif choice == 'ask':
					filename = ""
					data = ""
					# Receive filename to be sent
					while data != stop_char:
						data = conn.recv(1).decode('utf-8')
						if data == stop_char:
							break
						filename += data
					print('Searching for file ' + filename)
					found = 0
					i = 0
					for e in self.client_list:
						if e == conn:
							i += 1
							continue
						for a in range(len(self.files_list[i])):
							if filename == self.files_list[i][a]:
								reply = 'OK'
								conn.sendall((reply + stop_char).encode('utf-8'))
								data = ""
								port = ""  # probably this is for port
								while data != stop_char:
									data = conn.recv(1).decode('utf-8')
									if data == stop_char:
										break
									port += data

								e.sendall(('send' + stop_char + addr[0] + stop_char + port + stop_char + filename + stop_char).encode('utf-8'))
								found = 1
								break
						i += 1
						if found == 1:
							reply = 'Found desired file'
							data = ""
							while data != stop_char:
								data = conn.recv(1).decode('utf-8')
								if data == stop_char:
									break
								choice += data
							if choice == 'OK':
								print("Transfer was successful")
								# conn.sendall(('OK' + stop_char).encode('utf-8'))
							else:
								print('Communication between clients failed')
								# conn.sendall(('fail' + stop_char).encode('utf-8'))
							break
						reply = 'Did not found desired file'
					conn.sendall((reply+stop_char).encode('utf-8'))
					print(reply)
					continue
	
			conn.close()
		except Exception as e:
			print("Server's client_thread crashed:", e)

	def run(self):

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('Socket created')

		# Bind socket to local host and port
		try:
			s.bind((self.host, self.port))
		except Exception as msg:
			print('Bind failed. Error: ', str(msg))
			sys.exit()
		print('Socket bind complete')
		# Start listening on socket
		s.listen(self.max_clients)
		print('Socket now listening')

		# now keep talking with the client
		while 1:
			# wait to accept a connection - blocking call
			conn, addr = s.accept()
			self.client_list.append(conn)
			self.files_list.append([])
			self.address_list.append(addr)

			# print client_list
			print('Connected with ' + addr[0] + ':' + str(addr[1]))

			# start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
			t = threading.Thread(target=self.client_thread, args=(conn, addr))
			t.start()

		s.close()


server = Server()
server.run()
