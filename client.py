import socket   #for sockets
import sys  #for exit
import os
import time
from thread import *
flist=[]

def get_open_port():
	w = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	w.bind(("",0))
	w.listen(1)
	port = w.getsockname()[1]
	w.close()
	return port

def rcvFile(name,port,s):
	
	HOST = ''   # Symbolic name meaning all available interfaces
	PORT = port # Arbitrary non-privileged port
	
	z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#print 'Socket created'
	
	#Bind socket to local host and port
	try:
		z.bind((HOST, PORT))
	except socket.error , msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	s.sendall('OK')
	s.sendall('|')
	#print 'Socket bind complete'

	#Start listening on socket
	z.listen(1)
	#print 'Socket now listening'

	sc, address = z.accept()
	print 'Receiving file: ' + name + ' from ' + address[0] + ':' + str(address[1])
	
	f = open(name,'wb') #open in binary

	l = sc.recv(1024)
	while (l):
		f.write(l)
		l = sc.recv(1024)
	f.close()
	sc.close()
	
	z.close()
	
	print 'File received'

def listenThread(s):
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		choice=""
		data=""
		while data!='|':
			data=s.recv(1)
			if data=='|':
				break
			choice=choice+data
			
		#data = s.recv(1024)
		if choice=='OK':
			port=get_open_port()
			start_new_thread(rcvFile,(message,port,s))
			s.sendall(str(port))
			s.sendall('|')
		elif choice=='send':
			host=""
			data=""
			port=""
			name=""
			while data!='|':
				data=s.recv(1)
				if data=='|':
					break
				host=host+data
			data=""
			while data!='|':
				data=s.recv(1)
				if data=='|':
					break
				port=port+data
			port=int(port)
			data=""
			while data!='|':
				data=s.recv(1)
				if data=='|':
					break
				name=name+data
			
			data=""
			while data!='|':
				data=s.recv(1)
				if data=='|':
					break
				binding=binding+data
			if binding=='OK':
				z = socket.socket()
				z.connect((host,port))
				f=open (name, "rb") 
				l = f.read(1024)
				while (l):
					z.send(l)
					l = f.read(1024)
				z.close()
				print 'Sending completed'
		else:
			print choice


def sendMessage(socket,message):
	try:
		#Set the whole string
		s.sendall(message)
	except socket.error:
		#Send failed
		print 'Send failed'
		sys.exit()
	#print 'Message send successfully'

try:
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();
 
print 'Socket Created'
 
host = raw_input('Enter host to connect: ') #'192.168.1.9'
port = int(raw_input('Enter port: ')) #8888

try:
    remote_ip = socket.gethostbyname( host )
    
except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()
    
#print 'Ip address of ' + host + ' is ' + remote_ip

#Connect to remote server
s.connect((remote_ip , port))
start_new_thread(listenThread ,(s,))

print 'Client Connected to ' + host #+ ' on ip ' + remote_ip

while True:
	time.sleep(1)
	message = raw_input("Enter:\n\t'up' for uploading files\n\t'down' for downloading the file list\n\t'ask' for getting the desired file\n\t'exit' for exit\n")
	
	sendMessage(s,message)
	sendMessage(s,'|')
	
	if message=='exit':
		s.close()
		break
	elif message=='up':
		files = [f for f in os.listdir('.') if (os.path.isfile(f) and f!=sys.argv[0])]
		for i in files:
			#print "Sending ",i
			sendMessage(s,i)
			sendMessage(s,'>')
		sendMessage(s,'|')
	elif message=='ask':
		message = raw_input("Enter name of file:")
		print "Asking for file: ",message
		sendMessage(s,message)
		sendMessage(s,'|')
	elif message=='list':
		print 'This Client has the following files: \n'
		for i in files:
			print i + ' '