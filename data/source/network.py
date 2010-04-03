# -*- coding: utf-8 -*-
import threading
import socket
import traceback
import struct
import select
import cPickle

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
		6:"Start sound",
		7:"Stop sound"
		}

import sys
import time

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
		packet = (
				chr(udpSeq) \
				+ chr(type) \
				+ struct.pack("I", (len(msg))) + str(msg)
				)
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

class NetworkThread(threading.Thread):
	def __init__(self, main):
		self.main = main
		self.physics = main.physics
		self.player = main.player
		threading.Thread.__init__(self)
		self.addr = ('', 0)
		self.running = True
		self.objdataToAdd = []
	def run(self):
		self.handleNetwork()
	def handleNetwork(self):
		lastSend = 0
		myAddr = ('', 0)

		USend(self.addr, 0, "Nick")
		while self.running:
			read_sockets, write_sockets, error_sockets = \
					select.select([uSock, tSock], [], [], 0.05)
			for sock in read_sockets:
				print sock,"is ready for reading"
				if sock == uSock:
					type, recvd, addr = URecv()
					print "len(recvd) =", len(recvd)
					if len(recvd) == 0: continue

					if type == 0:
						print "Connected"
						myAddr = cPickle.loads(recvd)

					elif type == 3:
						print "Object data received"

						objects = self.physics.objects
						objdata = cPickle.loads(recvd)
						added = []

						for od in objdata:
							if od.id == self.player.data.id:
								continue

							for obj in objects:
								if od.id == obj.data.id:
									obj.data = od
									added.append(od)

						for obj in objects:
							exists = False
							if obj in self.objdataToAdd:
								exists = True
								continue

							for od in objdata:
								if obj.data.id == od.id:
									exists = True
									break

							if not exists and \
									obj.data.id != self.main.player.data.id:
								objects.remove(obj)

						for i in objdata:
							if i.id == self.player.data.id:
								continue

							alreadyAdded = False
							for j in self.objdataToAdd:
								if i.id == j.id:
									alreadyAdded = True
									break

							if i not in added and not alreadyAdded:
								self.objdataToAdd.append(i)

						self.physics.updateObjects(objects)
						for i in objects:
							print i.data.position
					elif type == 6: # start sound
						data = cPickle.loads(recvd)

						self.main.sound.Add_Sound(data[0], data[1], data[2], data[3])

					elif type == 7: # stop sound
						self.main.sound.Del_Sound(cPickle.loads(recvd))

				else:
					#tcp
					pass

			if time.time() - lastSend > 0.05:
				lastSend = time.time()
				USend(self.addr, 2, cPickle.dumps(self.player.data, 2))

		USend(self.addr, 1, self.player.data.id)
