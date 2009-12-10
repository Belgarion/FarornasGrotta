import socket
import traceback
import struct

uSock = 0
tSock = 0
tcpConnections = []

typeDict = {
		0:"Connect",
		1:"Disconnect",
		2:"Player object",
		3:"Object list",
		4:"Ping",
		5:"Pong",
		}

def Connect(host, port): 
	global uSock, tSock
	uSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	uSock.connect( (host, port) )
	tSock.connect( (host, port) )
	#uSock.setblocking(0)
	#tSock.setblocking(0)
def Listen(host, port):
	global uSock, tSock
	uSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	uSock.bind( (host, port) )
	tSock.bind( (host, port) )
	tSock.listen(5)
	#uSock.setblocking(0)
	#tSock.setblocking(0)

	tcpConnections.append(tSock)
def CloseConnections():
	global uSock, tSock, tcpConnections

	for sock in tcpConnections:
		sock.close()

	uSock.close()
def USend(addr, type, msg):
	if type > 255: print "wrong type"
	global uSock
	udpSeq = 255


	udpSeq = (udpSeq + 1) % 255

	try:
		packet = ( chr(udpSeq) + chr(type) + struct.pack("I", (len(msg))) + str(msg))
		while len(packet) > 0:
			uSock.sendto(packet[:65500], addr)
			packet = packet[65500:]
	except:
		traceback.print_exc()
	pass
def TSend(sock, type, msg):
	pass
def URecv():
	global uSock
	type = None
	msg = ""

	data, addr = uSock.recvfrom(65500)
	
	if len(data) > 5:
		print "UDP packet received"
		udpSeq = ord(data[0])
		print "UDP Sequence:",udpSeq

		type = ord(data[1])
		if type in typeDict:
			print ("Type: (%i) %s" % (type, typeDict[type]))
		else:
			print "Unknown type:",type

		length = struct.unpack("I", data[2:6])[0]
		print "Length:", length
		print "len(data):", len(data)
		if length > 0:
			if length < (len(data) - 6):
				print "length < (len(data) - 6)"
				#if player.buf != "": msg = buf
				msg += data[6:6+length]
			else:
				# Save in players buffer
				# Should be appended to list?
				msg += data[6:6+length]
				#print "Message:", data[6:6+length]
				while length > len(data) - 6:
					print "aoeu"
					data, addr = uSock.recvfrom(10)
					print "aa"
					print len(data)
					length -= len(data) - 6
					print "Message:", data[6:6+length]

	return (type, msg, addr)
def TRecv(sock, size):
	if sock == None:
		sock = tSock

	return sock.recv(size)
def Accept():
	global tSock, tcpConnections
	tSock2, addr = tSock.accept()
	#tSock2.setblocking(0)
	tcpConnections.append(tSock2)
	return addr

