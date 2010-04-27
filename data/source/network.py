# -*- coding: utf-8 -*-
import threading, socket, traceback, struct, select, cPickle

# TODO: This fits in here as much as it fits in main ^^, but going to fix this
from gingerbreadMonster import GingerbreadMonster
from player import Player
from fireball import Fireball

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
		7:"Stop sound",
		8:"Remove object",
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

	debug = 0

	data, addr = uSock.recvfrom(65500)

	if len(data) > 5:
		if debug: print "UDP packet received"
		udpSeq = ord(data[0])
		if debug: print "UDP Sequence:",udpSeq

		type = ord(data[1])
		if type in typeDict:
			if debug: print ("Type: (%i) %s" % (type, typeDict[type]))
		else:
			if debug: print "Unknown type:",type

		length = struct.unpack("I", data[2:6])[0]
		if debug: print "Length:", length
		if debug: print "len(data):", len(data)
		if length > 0:
			if length < (len(data) - 6):
				if debug: print "length < (len(data) - 6)"
				#if player.buf != "": msg = buf
				msg += data[6:6+length]
			else:
				# Save in players buffer
				# Should be appended to list?
				msg += data[6:6+length]
				if debug: print "Message:", data[6:6+length]
				while length > len(data) - 6:
					if debug: print "aoeu"
					data, addr = uSock.recvfrom(10)
					if debug: print "aa"
					if debug: print len(data)
					length -= len(data) - 6
					if debug: print "Message:", data[6:6+length]

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

		self.debug = 0

	def run(self):
		self.handleNetwork()

	def addNewObjects(self):
		# TODO: from gingerbreadMonster import GingerbreadMonster
		objects = self.physics.objects
		for i in self.objdataToAdd:
			if i.type == "player1":
				if self.debug: print "Append a player!"
				p = Player(i.name,
						i.position,
						i.orientation,
						i.scale, i.mass, i.id)

				# TODO: Do a function/class that add it to every list we need...
				objects.append(p)
				self.main.octree.insertNode(
					self.main.octree.root,
					self.main.octree.worldSize,
					self.main.octree.root,
					p.data
				)

			elif i.type == "GingerbreadMonster":
				if self.debug: print "Append a monster!"
				g = GingerbreadMonster(
						"GingerbreadMonster",
						i.name,
						i.position,
						i.orientation,
						i.scale,
						i.mass, self.main.objects, False, i.id)
				objects.append(g)
				self.main.octree.insertNode(
					self.main.octree.root,
					self.main.octree.worldSize,
					self.main.octree.root,
					g.data
				)
			elif i.type == "Fireball":
				f = Fireball(i.name, i.position,
						i.orientation, i.scale, i.mass,
						i.velocity, i.id)
				objects.append(f)
				#self.main.octree.insertNode(
				#	self.main.octree.root,
				#	self.main.octree.worldSize,
				#	self.main.octree.root,
				#	f.data
				#)
			self.objdataToAdd.remove(i)
		self.physics.updateObjects(objects)

	def handleNetwork(self):
		lastSend = 0
		myAddr = ('', 0)

		USend(self.addr, 0, "Nick")
		while self.running:
			read_sockets, write_sockets, error_sockets = \
					select.select([uSock, tSock], [], [], 0.05)
			for sock in read_sockets:
				if self.debug: print sock,"is ready for reading"
				if sock == uSock:
					type, recvd, addr = URecv()
					if self.debug: print "len(recvd) =", len(recvd)
					if len(recvd) == 0: continue

					if type == 0:
						if self.debug: print "Connected"
						myAddr = cPickle.loads(recvd)

					elif type == 3:
						if self.debug: print "Object data received"

						objects = self.physics.objects
						objdata = cPickle.loads(recvd)
						added = []

						for od in objdata:
							if od.id == self.player.data.id:
								continue

							for obj in objects:
								if od.id == obj.data.id:
									added.append(od.id)

						for obj in objects:
							exists = False
							if obj in self.objdataToAdd:
								exists = True
								continue

							for od in objdata:
								if od.id == self.player.data.id:
									continue
								if obj.data.id == od.id:
									if obj.data.type != "Fireball":
										self.main.octree.deletePosition(
												self.main.octree.root,
												obj.data.position,
												obj.data
												)
										self.main.octree.insertNode(
												self.main.octree.root,
												15000,
												self.main.octree.root,
												obj.data
												)
									obj.data = od
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

							if i.id not in added and not alreadyAdded:
								self.objdataToAdd.append(i)

						self.physics.updateObjects(objects)
						for i in objects:
							if self.debug: print i.data.position
					elif type == 8: # remove object
						data = cPickle.loads(recvd)

						self.main.octree.deletePosition(
								self.main.octree.root,
								data.position,
								data
								)
					elif type == 6: # start sound
						data = cPickle.loads(recvd)

						if self.main.sound != None:
							self.main.sound.Add_Sound(data[0], data[1], data[2], data[3])

					elif type == 7: # stop sound
						if self.main.sound != None:
							self.main.sound.Del_Sound(cPickle.loads(recvd))

				else:
					#tcp
					pass

			if time.time() - lastSend > 0.05:
				lastSend = time.time()
				USend(self.addr, 2, cPickle.dumps(self.player.data, 2))

		USend(self.addr, 1, self.player.data.id)
