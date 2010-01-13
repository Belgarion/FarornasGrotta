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
from player import Player

import StringIO

class InputThread(threading.Thread):
	def __init__(self, input):
		self.input = input
		threading.Thread.__init__(self)
	def run(self):
		self.input.handle_input()

class Main:
	def __init__(self):
		args = {'disableWater': False}
		if len(sys.argv) > 1:
			for arg in sys.argv:
				if arg == "--nowater":
					args['disableWater'] = True

		config = self.init_config()
	
		self.mainMenuOpen = True

		pygame.init()
		pygame.display.set_mode(
				(config.getint('Resolution','Width'),
					config.getint('Resolution', 'Height')),
				pygame.DOUBLEBUF | pygame.OPENGL)

		objects = []

		self.octree = COctree()

		self.graphics = Graphics(self.octree, self, config, args)
		self.graphics.initGL()

		self.menu = Menu(self.graphics, config)
		self.menu.init_font()

		self.player = Player()
		objects.append(self.player)

		monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0), 100, (0.0,0.0,0.0))
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

		self.menu.setBackground("img2.png")
		self.menu.addMenuEntry("Start", self.startGame)
		self.menu.addMenuEntry("Options", self.options)
		self.menu.addMenuEntry("Quit", self.quit)

		self.Input = input(self.octree, self.graphics, self.menu, self.player,
				config, self)
		self.inputThread = InputThread(self.Input)
		self.inputThread.start()

	def run(self):
		fpsTime = 0
		while not Global.quit:
			if time.time() - fpsTime >= 1.0:
				fpsTime = time.time()
				self.graphics.printFPS()

			if sys.platform == "win32":
				self.Input.handle_mouse()

			if self.mainMenuOpen:
				self.menu.draw()
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

	def options(self):
		print "Not implemented (yet)"
		# TODO: Implement submenus

	def quit(self):
		Global.quit = 1

	def init_config(self):
		
		# Just add new values
		defaultConfig = StringIO.StringIO("""\
[Resolution]
Width: 640
Height: 480

[Input]
KeyboardLayout: qwerty
				""")

		config = ConfigParser.SafeConfigParser()
		config.readfp(defaultConfig)
		config.read('config')

		return config

if __name__ == '__main__':
	main = Main()
	main.run()
	main.inputThread.join()
