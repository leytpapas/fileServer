import socket
import sys
from thread import *
clist=[]
alist=[]
flist=[]

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'

#Start listening on socket
s.listen(10)
print 'Socket now listening'


#Function for handling connections. This will be used to create threads
def clientthread(conn,addr):
	#Sending message to connected client
	conn.send('Welcome to the server.\n') #send only takes string
	conn.send('|')
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		
		#Receiving from client
		choice=""
		data=""
		while data!='|':
			data=conn.recv(1)
			if data=='|':
				break
			choice=choice+data
		reply = addr[0] + ':' + str(addr[1]) + ' sent: ' + choice + '\n'
		print reply
		
		if choice == 'exit':
			s=0
			for a in clist:
				if a == conn:
					reply = addr[0] + ':' + str(addr[1]) + ' disconnected from server.\n|'
					for i in clist:
						if i == conn:
							#flist[s]=[]
							continue
						i.sendall(reply)
					clist.remove(a)
					flist[s]=[]
					flist.remove([])
					break
					
				s=s+1
			print reply
			break
		
		#uploading list of files for each client
		elif choice == 'up':
			s=0
			for i in clist:
				if i == conn:
					
					flist[s]=[]
					word=""
					#print 'Ok'
					while word!='|':
						data=""
						word=""
						while word!='>':
							#print 'OK3'
							word=conn.recv(1)
							if word=='|':
								break
							elif word=='>':
								flist[s].append(data)
								break
							data=data+word
					print 'File list has been updated:\n'
					print  flist
					break
				s=s+1
			continue
		#downloading list of files
		elif choice == 'down':
			reply= '\nFiles list:'
			s=0
			for i in clist:
				reply=reply + '\nClient' + str(s+1) + ': '
				for a in range(len(flist[s])):
					reply=reply + flist[s][a] + ' '
				s=s+1
			conn.sendall(reply)
			conn.sendall('|')
			continue
		elif choice == 'ask':
			choice=""
			data=""
			while data!='|':
				data=conn.recv(1)
				if data=='|':
					break
				choice=choice+data
			print 'Searching for file ' + choice 
			found=0
			s=0
			for i in clist:
				if i == conn:
					s=s+1
					continue
				for a in range(len(flist[s])):
					if choice==flist[s][a]:
						reply='OK'
						conn.sendall(reply)
						conn.sendall('|')
						data=""
						port=""
						while data!='|':
							data=conn.recv(1)
							if data=='|':
								break
							port=port+data
						reply='send'
						i.sendall(reply)
						i.sendall('|')
						reply=addr[0]
						i.sendall(reply)
						i.sendall('|')
						reply=port
						i.sendall(reply)
						i.sendall('|')
						
						reply=choice
						i.sendall(reply)
						i.sendall('|')
						
						found=1
						break
				s=s+1
				if found==1:
					reply= 'Found desired file'
					data=""
					while data!='|':
						data=conn.recv(1)
						if data=='|':
							break
						choice=choice+data
					if choice=='OK':
						i.sendall('OK')
						i.sendall('|')
					else:
						print 'Communication between clients failed'
						i.sendall('fail')
						i.sendall('|')
					#print reply
					break
				reply='Did not found desired file'
			conn.sendall(reply)
			conn.sendall('|')
			print reply
			continue
		
	#came out of loop
	conn.close()

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    clist.append(conn)
    flist.append([])
    alist.append(addr)
    
    #print clist
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,addr))
 
s.close()