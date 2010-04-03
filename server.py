#!/usr/bin/env python
import cPickle
import sys
import time
import traceback
import select
import time

sys.path.append("data/source/")

import network as Network
from gingerbreadMonster import GingerbreadMonster
from physics import Physics
from Global import Global
from gameObject import GameObject

#TODO: ? Keepalive packets ?
#TODO: Player buffer

objects = []
threads = []

def spawnMonsters():
	print "spawnMonsters()"
	print objdata
	gingerbreadMonster = GingerbreadMonster(
			"GingerbreadMonster", "Gingerbread 1",
			(0.0, 50.0, 40.0), (0.0, 0.0, 0.0),
			100.0, objects, True)
	objects.append(gingerbreadMonster)

	objdata.append(gingerbreadMonster.data)

	gingerbreadIntelligenceThread = \
		gingerbreadMonster.IntelligenceThread(gingerbreadMonster)
	gingerbreadIntelligenceThread.start()
	threads.append(gingerbreadIntelligenceThread)

if __name__ == '__main__':
	Network.Listen('0.0.0.0', 30000)

	startTime = time.time()

	objdata = []
	players = []

	physics = Physics(objects)

	spawnMonsters()

	physics.updateObjects(objects)

	try:
		while True:
			objects = physics.update()

			sendObjdata = False

			read_sockets, write_sockets, error_sockets = \
					select.select(
							Network.tcpConnections + [Network.uSock], [], [], 0.1)
			for sock in read_sockets:
				if sock == Network.tSock: #new connection on server socket
					addr = Network.Accept()
					print "Client connected:",addr

				elif sock == Network.uSock: #udp data
					try:
						type, recvd, addr = Network.URecv()
						print "len(recvd):",len(recvd)
						if type == None: pass
						else:
							if type == 0:
								print "Client connected UDP:", addr
								players.append(addr)
								Network.USend(addr, 0, cPickle.dumps(addr, 2))
							elif type == 1:
								print "Client disconnected UDP:", addr
								players.remove(addr)
								for i in objdata:
									if i.id == recvd:
										objdata.remove(i)
								for i in objects:
									if i.data.id == recvd:
										objects.remove(i)
							elif type == 2:
								sendObjdata = True
								obj = cPickle.loads(recvd)
								obj.addr = addr

								objectExists = False
								for i in xrange(len(objdata)):
									if objdata[i].id == obj.id:
										objectExists = True
										objdata[i] = obj
										break

								for i in xrange(len(objects)):
									if obj.id == objects[i].data.id:
										objects[i].data = obj

								if not objectExists:
									print "Object not in list"
									objdata.append(obj)
									g = GameObject(obj.type, obj.name,
											obj.position, obj.orientation,
											obj.mass, obj.velocity,
											obj.id)
									objects.append(g)

								for i in objdata:
									print "Name:",i.name
									print "Position:",i.position
					except Exception, e:
						traceback.print_exc()

				else: #data received from client
					data = Network.TRecv(sock, 256)
					if len(data) == 0:
						print "Connection reset by peer"
						sock.close()
						Network.tcpConnections.remove(sock)
						continue

					if data:
						#add to player buffer
						#process all complete commands in buffer
						print data

			for sock in Network.tcpConnections:
				if sock == Network.tSock:
					pass

				#tcp
				#we need association tcp-socket<->player<->udp-addr

			for addr in players:
				print "Sending data"
				if sendObjdata: #fix this
					print "Sending objdata"
					Network.USend(addr, 3, cPickle.dumps(objdata, 2))


	except:
		traceback.print_exc()

	Network.CloseConnections()

	Global.quit = True
	for i in threads:
		if i.isAlive(): i.join()
