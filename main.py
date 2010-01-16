#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
import sys
import os
import time
try:
	import pygame
except:
	print "ERROR: pygame is not installed"
	sys.exit()
import math
import random
import threading
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
import ConfigParser
from OpenGL.GL.ARB.vertex_buffer_object import *
import traceback
from octree import *
from gameObject import GameObject

import Network
import cPickle

import select

from player import Player

import StringIO

class InputThread(threading.Thread):
	def __init__(self, input):
		self.input = input
		threading.Thread.__init__(self)
	def run(self):
		self.input.handle_input()

class NetworkThread(threading.Thread):
	def __init__(self, physics, player):
		self.physics = physics
		self.player = player
		threading.Thread.__init__(self)
		self.addr = ('', 0)
	def run(self):
		self.handleNetwork()
	def handleNetwork(self):
		myAddr = ('', 0)

		Network.USend(self.addr, 0, "Nick")
		while not Global.quit:
			read_sockets, write_sockets, error_sockets = \
					select.select([Network.uSock, Network.tSock], [], [], 1)
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
								objects[i] = self.player
								break

						self.physics.updateObjects(objects)
						for i in objects:
							print i.position

				else:
					#tcp
					pass

			Network.USend(self.addr, 2, cPickle.dumps(self.player, 2))
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

		Network.USend(self.addr, 1, "")

class Main:
	def __init__(self):
		self.args = {'disableWater': False,
				'host': None,
				'port': 30000}
		if len(sys.argv) > 1:
			for index, arg in enumerate(sys.argv):
				if arg == "--help" or arg == "-h":
					print "Arguments: \n"\
							"	--nowater		Disable water\n"\
							"	--host			Connect to host\n"\
							"	--port			Port (Default: 30000)\n"
					sys.exit(0)
				elif arg == "--nowater":
					self.args['disableWater'] = True
				elif arg == "--host":
					if not len(sys.argv) > index + 1:
						print "No host specified for --host"
						continue
					self.args['host'] = sys.argv[index + 1]
				elif arg == "--port":
					if not len(sys.argv) > index + 1:
						print "No port specified for --port"
						continue
					self.args['port'] = sys.argv[index + 1]

		config = self.init_config()
		self.config = config

		self.mainMenuOpen = True

		pygame.init()
		pygame.display.set_mode(
				(config.getint('Resolution','Width'),
					config.getint('Resolution', 'Height')),
				pygame.DOUBLEBUF | pygame.OPENGL)

		objects = []

		self.octree = COctree()

		self.graphics = Graphics(self.octree, self, config, self.args)
		self.graphics.initGL()


		self.player = Player()
		objects.append(self.player)

		monster = GameObject("monster1", (0.0, 100.0, 0.0),
				(0.0, 0.0, 0.0), 100, (0.0,0.0,0.0))
		objects.append(monster)

		self.physics = Physics(objects)

		pygame.mouse.set_visible(0)
		pygame.event.set_grab(1)

		rel = pygame.mouse.get_rel()

		print "Edit config for settings"
		print "F2 for toggle debugLines"
		print "F6 for toggle drawAxes"
		print "F7 for toggle wireframe"
		print "+/- to increase/decrease number of debug-lines level"
		print "WASD to move. Mouse to look"

		self.graphics.addSurface(0, "Terrain.raw", "grass.jpg")

		self.initMenus()

		self.Input = input(self.octree, self.graphics, self.menu, self.player,
				config, self)
		self.inputThread = InputThread(self.Input)
		self.inputThread.start()

		self.networkThread = NetworkThread(self.physics, self.player)

	def initMenus(self):
		self.font = Font()

		self.menu = Menu(self.graphics, self.config, self.font)

		self.menu.setBackground("img2.png")
		self.menu.addMenuEntry("Start", self.startGame)

		def MOptions():
			self.menu.current = self.optionsMenu
		self.menu.addMenuEntry("Options", MOptions)

		def MQuit():
			Global.quit = 1
		self.menu.addMenuEntry("Quit", MQuit)

		self.optionsMenu = Menu(self.graphics, self.config, self.font)

		self.optionsMenu.setBackground("img2.png")

		resolutions = [(640, 480),
				(800, 600),
				(1024, 768),
				(1280, 960),
				(1400, 1050),
				(1600, 1200),
				(1680, 1260),
				(1920, 1440),
				(2048, 1536)]

		def OMResolution():
			om = self.optionsMenu
			wstr, hstr = om.menuEntries[om.row][0].split(":")[1] \
					.lstrip().split("x")
			w, h = int(wstr), int(hstr)
			for i, r in enumerate(resolutions):
				if r[0] == w or \
						(len(resolutions) > i + 1 and resolutions[i+1][0] > w):
					index = (i + 1) % (len(resolutions))
					nw, nh = resolutions[index]
					self.config.set("Resolution", "Width", str(nw))
					self.config.set("Resolution", "Height", str(nh))
					om.menuEntries[om.row] = ("Resolution: " + \
							str(nw) + "x" + str(nh),
							om.menuEntries[om.row][1])
					break

		self.optionsMenu.addMenuEntry(
				"Resolution: " + self.config.get("Resolution","Width") \
						+ "x" + \
						self.config.get("Resolution","Height"),
				OMResolution)

		keyboardLayouts = ["qwerty", "dvorak"]
		def OMKeyboardLayout():
			om = self.optionsMenu
			layout = om.menuEntries[om.row][0].split(":")[1].lstrip()
			for i, l in enumerate(keyboardLayouts):
				if layout == l:
					index = (i + 1) % (len(keyboardLayouts))
					nl = keyboardLayouts[index]
					self.config.set("Input", "KeyboardLayout", nl)
					om.menuEntries[om.row] = \
							("Keyboard Layout: " + nl,
									om.menuEntries[om.row][1])

		self.optionsMenu.addMenuEntry(
			"Keyboard Layout: " + self.config.get("Input", "KeyboardLayout"),
			OMKeyboardLayout)

		def OMBack():
			with open("config", "wb") as configfile:
				main.config.write(configfile)
			self.menu.current = self.menu

		self.optionsMenu.addMenuEntry("Back", OMBack)

	def run(self):
		if self.args['host'] != None:
			self.networkThread.addr = (self.args['host'], self.args['port'])
			Network.Connect(self.args['host'], self.args['port'])
			self.networkThread.start()

		fpsTime = 0
		while not Global.quit:
			if time.time() - fpsTime >= 1.0:
				fpsTime = time.time()
				self.graphics.printFPS()

			if sys.platform == "win32":
				self.Input.handle_mouse()

			if self.mainMenuOpen:
				self.menu.current.draw()
			else:
				objects = self.physics.update()
				self.graphics.draw(objects)

	def editpos(self):
		self.Input.xpos = -400
		self.Input.ypos = 360
		self.Input.zpos = -45

	def startGame(self):
		self.mainMenuOpen = False
		self.editpos()
		self.physics.lastTime = time.time()

	def init_config(self):
		defaultConfig = StringIO.StringIO(\
				"[Resolution]\n"\
				"Width: 640\n"\
				"Height: 480\n"\
				"\n"\
				"[Input]\n"\
				"KeyboardLayout: qwerty\n"\
				)

		config = ConfigParser.SafeConfigParser()
		config.readfp(defaultConfig)
		config.read('config')

		return config

if __name__ == '__main__':
	main = Main()
	main.run()
	main.inputThread.join()
	if main.networkThread.isAlive(): main.networkThread.join()
