#!/usr/bin/env python
import os
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
from gameObject import GameObject

#TODO: ? Keepalive packets ?
#TODO: Player buffer

objects = []
threads = []

def load_level(name):
	f = open("data/level/" + name + ".lvl")
	creatures = []
	for line in f:
		if not line: continue
		if line[0] is "#": continue
		split = line.split(" ")
		if split[0] == "spawn":
			pos = split[3].split(",")
			pos = (float(pos[0]), float(pos[1]), float(pos[2]))
			orientation = split[4].split(",")
			orientation = (float(orientation[0]), float(orientation[1]), float(orientation[2]))

			object = [split[1], split[2], (pos[0], pos[1], pos[2]), \
					(orientation[0], orientation[1], orientation[2]), float(split[5])]
			creatures.append(object)
	return creatures


def spawnMonsters():
	print "spawnMonsters()"

	objects_loaded = load_level("level1")

	for object in objects_loaded:
		if object[0] == "GingerbreadMonster":
			gingerbreadMonster = GingerbreadMonster(
				object[0], object[1],
				object[2], object[3],
				object[4],100.0, objects, True)

			#objdata.append(gingerbreadMonster.data)

			gingerbreadIntelligenceThread = \
				gingerbreadMonster.IntelligenceThread(gingerbreadMonster)
			gingerbreadIntelligenceThread.start()
			threads.append(gingerbreadIntelligenceThread)

			gingerbreadMonster.intelligenceThread = \
					gingerbreadIntelligenceThread

			objects.append(gingerbreadMonster)
		elif object[0] == "some other monster":
			pass


if __name__ == '__main__':
	Network.Listen('0.0.0.0', 30000)

	startTime = time.time()

	objdata = []
	players = []

	physics = Physics(objects)
	physics.isClient = False

	spawnMonsters()

	physics.updateObjects(objects)

	try:
		lastSend = 0
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
										obj.frags = objects[i].data.frags
										obj.deaths = objects[i].data.deaths
										obj.hp = objects[i].data.hp
										objects[i].data = obj

								if not objectExists:
									print "Object not in list"
									objdata.append(obj)
									g = GameObject(obj.type, obj.name,
											obj.position, obj.orientation,
											obj.scale, obj.mass, obj.velocity,
											obj.id, obj.owner)
									objects.append(g)

							elif type == 6: # start sound
								for ad in players:
									if ad != addr:
										Network.USend(ad, 6, recvd)
							elif type == 7: # stop sound
								for ad in players:
									if ad != addr:
										Network.USend(ad, 7, recvd)
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

			if time.time() - lastSend > 0.05:
				for addr in players:
					print "Sending data"
					lastSend = time.time()
					print "Sending objdata to", addr
					od = []
					for obj in objects:
						if obj.data.hp <= 0:
							if obj.data.type == "GingerbreadMonster" and \
									obj.intelligenceThread != None:
								obj.intelligenceThread.quit = True
								if obj.intelligenceThread.isAlive():
									obj.intelligenceThread.join()

								threads.remove(obj.intelligenceThread)

								#TODO: Spawn new monster
							physics.objectsToRemove.append(obj)
							objects.remove(obj)
						else:
							print obj.data.id, obj.data.name, obj.data.frags
							od.append(obj.data)
					Network.USend(addr, 3, cPickle.dumps(od, 2))

					for obj in physics.objectsToRemove:
						Network.USend(addr, 8, cPickle.dumps(obj.data))
						physics.objectsToRemove.remove(obj)


	except:
		traceback.print_exc()

	Network.CloseConnections()

	#Global.quit = True
	for i in threads:
		i.quit = True
		if i.isAlive(): i.join()
