import socket
import sys
import os
import time
import threading


class Client:
	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.files = [f for f in os.listdir('.') if (os.path.isfile(f) and f != sys.argv[0])]
		self.listen = threading.Thread(target=self.listenThread, args=(self.s,))
		self.end = False


	def get_open_port(self):
		w = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		w.bind(("", 0))
		w.listen(1)
		port = w.getsockname()[1]
		w.close()
		return port

	def rcvFile(self, port):


		z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# print 'Socket created'

		# Bind socket to local host and port
		try:
			z.bind(('', port))
		except socket.error as msg:
			print('Bind failed. Error : ' + str(msg))
			sys.exit()
		# self.s.sendall(('OK'+'|').encode('utf-8'))
		# print 'Socket bind complete'

		# Start listening on socket
		z.listen(1)
		# print 'Socket now listening'

		sc, address = z.accept()
		name = ""
		data = ""
		while data != '|' and not self.end:
			try:
				data = z.recv(1).decode('utf-8')
			except socket.timeout as e:
				err = e.args[0]
				# this next if/else is a bit redundant, but illustrates how the
				# timeout exception is setup
				if err == 'timed out':
					time.sleep(1)
					#print('recv timed out, retry later')
					continue
				else:
					print(e)
					sys.exit(1)
			except socket.error as e:
				# Something else happened, handle error, exit, etc.
				print(e)
				self.end = True
				sys.exit(1)
			else:
				if data == '|':
						break
				else:
					name += data
		print('Receiving file: ' + name + ' from ' + address[0] + ':' + str(address[1]))

		f = open(name, 'wb')  # open in binary

		l = sc.recv(1024).decode('utf-8')
		while l:
			f.write(l)
			l = sc.recv(1024).decode('utf-8')
		f.close()
		sc.close()

		z.close()
		self.s.sendall(('OK' + '|').encode('utf-8'))
		self.files.append(name)
		print('File received')


	def listenThread(self, s):
		while not self.end:
			choice = ""
			data = ""
			while data != '|':
				try:
					data = s.recv(1).decode('utf-8')
				except socket.timeout as e:
					err = e.args[0]
					# this next if/else is a bit redundant, but illustrates how the
					# timeout exception is setup
					if err == 'timed out':
						time.sleep(1)
						# print('recv timed out, retry later')
						continue
					else:
						print(e)
						sys.exit(1)
				except socket.error as e:
					# Something else happened, handle error, exit, etc.
					print(e)
					self.end = True
					sys.exit(1)
				else:
					if data == '|':
						break
					else:
						choice += data

			# data = s.recv(1024)

			if choice == 'OK':
				port = self.get_open_port()
				t = threading.Thread(target=self.rcvFile, args=port)
				t.start()
				s.sendall((str(port)+'|').encode('utf-8'))

			elif choice == 'send':
				host = ""
				data = ""
				port = ""
				name = ""
				while data != '|':
					data = s.recv(1).decode('utf-8')
					if data == '|':
						break
					host += data
				print('Host', host)
				data = ""
				while data != '|':
					data = s.recv(1).decode('utf-8')
					if data == '|':
						break
					port += data
				print('Port', port)
				port = int(port)
				data = ""
				while data != '|':
					data = s.recv(1).decode('utf-8')
					if data == '|':
						break
					name += data
				print('name',name)
				# data = ""
				# binding = ""
				# while data != '|':
				# 	data = s.recv(1).decode('utf-8')
				# 	if data == '|':
				# 		break
				# 	binding += data
				# print("binding", binding)

				# if binding == 'OK':
				z = socket.socket()
				z.connect((host, port))
				f = open(name, "rb")
				l = f.read(1024)
				z.sendall((name+'|').encode('utf-8'))
				while l:
					z.sendall(l.encode('utf-8'))
					l = f.read(1024)
				z.close()
				print('Sending completed')
			else:
				print(choice)

	def sendMessage(self, s, message):
		try:
			# Set the whole string
			s.sendall(message.encode('utf-8'))
		except s.error:
			# Send failed
			print('Send failed')
			sys.exit()
		# print 'Message send successfully'

	def run(self):
		host = 'localhost'  # input('Enter host to connect: ')  # '192.168.1.9'
		port = int(input('Enter port: '))  # 8888

		try:
			remote_ip = socket.gethostbyname(host)
		except socket.gaierror:
			# could not resolve
			print('Hostname could not be resolved. Exiting')
			self.s.close()
			sys.exit()

		# print 'Ip address of ' + host + ' is ' + remote_ip

		# Connect to remote server
		self.s.connect((remote_ip, port))
		self.s.settimeout(2)
		self.listen.start()

		print('Client Connected to ' + host) # + ' on ip ' + remote_ip)

		while True:
			time.sleep(1)
			message = input("Enter:\n\t'up' for uploading files\n\t'down' for downloading the file list\n\t'ask' for getting the desired file\n\t'list' for list of files\n\t'exit' for exit\n")

			self.sendMessage(self.s, message + '|')

			if message == 'exit':
				try:
					self.s.close()
				except Exception as err:
					pass
				break
			elif message == 'up':
				self.files = [f for f in os.listdir('.') if (os.path.isfile(f) and f != sys.argv[0])]
				for i in self.files:
					# print "Sending ",i
					self.sendMessage(self.s, i + '>')

				self.sendMessage(self.s, '|')
			elif message == 'ask':
				message = input("Enter name of file:")
				print("Asking for file: ", message)
				self.sendMessage(self.s, message + '|')
			elif message == 'list':
				print('This Client has the following files: \n')
				for i in self.files:
					print(i + ' ')

if __name__ == '__main__':
	client = Client()
	client.run()