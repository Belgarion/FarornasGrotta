#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
import sys
import time
try:
	import pygame
except:
	print "ERROR: pygame is not installed"
	sys.exit()
import math
import random
import threading
import thread
try:
	import OpenGL
except:
	print "ERROR: pyopengl is not installed"
	sys.exit()
import logging

from Global import *
from physics import Physics
from graphics import *
from menu import *
from player import Player

#OpenGL.FULL_LOGGING = True

logging.basicConfig()
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
from input import *
try:
	import numpy as Numeric
except:
	import Numeric
from OpenGL.GL.ARB.vertex_buffer_object import *
import traceback
from octree import *

from gameObject import GameObject
import Network
import cPickle

import select

Global.Input = input()
Global.menu = Menu()
graphics = Graphics()
physics = 0

objects = []

g_nFrames = 0.0

Input = input()
inputThread = None

class TestObject:
	def __init__(self, name, position):
		self.name = name
		self.position = position

class InputThread(threading.Thread):
	def run(self):
		Global.Input.handle_input()

def init():
	global physics, inputThread

	if len(sys.argv) > 1:
		for arg in sys.argv:
			if arg == "--nowater":
				Global.disableWater = True

	pygame.init()
	pygame.display.set_mode((640,480), pygame.DOUBLEBUF | pygame.OPENGL)

	graphics.initGL()
	Global.menu.init_font()

	pygame.mouse.set_visible(0)
	pygame.event.set_grab(1)

	rel = pygame.mouse.get_rel()

	objects = []
	monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0), 100, (0.0,0.0,0.0))
	objects.append(monster)
	Global.player = Player()
	objects.append(Global.player)
	physics = Physics(objects)

	print "F1 for switch between Qwerty and Dvorak"
	print "F2 for switch debugLines"
	print "F6 for switch drawAxes"
	print "F7 for switch wireframe"
	print "+/- to increase/decrease number of debug-lines level"
	print "WASD to move. Mouse to look"

	graphics.addSurface(0, "Terrain.raw", "grass.jpg")

	Global.menu.setBackground("img2.png")
	Global.menu.addMenuEntry("Start", startGame)
	Global.menu.addMenuEntry("Options", options)
	Global.menu.addMenuEntry("Quit", quit)

	inputThread = InputThread()
	inputThread.start()


def editpos():
	Global.Input.xpos = -400
	Global.Input.ypos = 360
	Global.Input.zpos = -45
	#Global.Input.xrot = -333
	#Global.Input.yrot = -250

fpsTime = 0

def startGame():
	Global.mainMenuOpen = False
	editpos()
	physics.lastTime = time.time()

def options():
	print "Not implemented (yet)"
	# TODO: Implement submenus

def quit():
	Global.quit = 1

def handleNetwork():
	global objects

	addr = ('localhost', 30000)
	myAddr = ('', 0)

	Network.USend(addr, 0, "Nick")
	while not Global.quit:
		read_sockets, write_sockets, error_sockets = select.select([Network.uSock, Network.tSock], [], [], 1)
		for sock in read_sockets:
			print sock,"is ready for reading"
			if sock == Network.uSock:
				type, recvd, addr = Network.URecv()
				print "len(recvd) =", len(recvd)
				if len(recvd) == 0: continue
				
				if type == 0:
					print "Connected"
					myAddr = cPickle.loads(recvd)

				elif type == 3:
					print "Objects received"
					objects = cPickle.loads(recvd)
					for i in xrange(len(objects)):
						if objects[i].addr == myAddr:
							objects[i] = Global.player
							break

					physics.updateObjects(objects)
					for i in objects:
						print i.position

			else:
				#tcp
				pass

		Network.USend(addr, 2, cPickle.dumps(Global.player, 2))
		#print cPickle.dumps(objects, 2)
	
		#try:
		#	recvd, addr = Network.URecv()
		#	if len(revcd) == 0: pass
		#	else: print recvd
		#except:
		#	pass
	
		#Använd select för att kolla om det finns något att ta emot
		#recvd = Network.TRecv(None, 256)
		#while recvd:
		#	print recvd
		#	recvd = Nework.TRecv(None, 256)
	
	Network.USend(addr, 1, "")


init()
Network.Connect('localhost', 30000)
thread.start_new_thread(handleNetwork, ())

while not Global.quit:
	if time.time() - fpsTime >= 1.0:
		fpsTime = time.time()
		graphics.printFPS()

	if sys.platform == "win32":
		Global.Input.handle_mouse()

	if Global.mainMenuOpen:
		Global.menu.draw()
	else:
		objects = physics.update()
		graphics.draw(objects)

Network.CloseConnections()

inputThread.join()
