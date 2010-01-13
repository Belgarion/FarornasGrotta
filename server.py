#!/usr/bin/env python
import Network
import cPickle
import sys
import time
import traceback
import select
import time

#TODO: ? Keepalive packets ?
#TODO: Player buffer

if __name__ == '__main__':
	Network.Listen('0.0.0.0', 30000)

	startTime = time.time()

	objects = []
	players = []
	try:
		while True:
			sendObjects = False

			read_sockets, write_sockets, error_sockets = select.select(Network.tcpConnections + [Network.uSock], [], [], 1)
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
								for i in objects:
									if i.addr == addr:
										objects.remove(i)
							elif type == 2:
								sendObjects = True
								obj = cPickle.loads(recvd)
								obj.addr = addr

								objectExists = False
								for i in xrange(len(objects)):
									if objects[i].addr == obj.addr:
										objectExists = True
										objects[i] = obj
										break

								if not objectExists:
									print "Object not in list"
									objects.append(obj)

								
								for i in objects:
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
				if sendObjects: #fix this
					print "Sending objects"
					Network.USend(addr, 3, cPickle.dumps(objects, 2))


	except:
		traceback.print_exc()

	Network.CloseConnections()
