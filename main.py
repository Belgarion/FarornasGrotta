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

import thread
from Global import *
from physics import Physics
from graphics import *
from menu import *

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

Global.Input = input()
Global.menu = Menu()
graphics = Graphics()
physics = 0
objects = []

g_nFrames = 0.0

class TestObject:
	def __init__(self, name, position):
		self.name = name
		self.position = position



class GameObject:
	def __init__(self, name, position, orientation, mass, velocity ):
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity

def init():
	global physics
	pygame.init()
	pygame.display.set_mode((640,480), pygame.DOUBLEBUF | pygame.OPENGL)

	pygame.mouse.set_visible(0)
	pygame.event.set_grab(1)

	rel = pygame.mouse.get_rel()

	monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0,), 100, (0.0,0.0,0.0))
	objects.append(monster)
	physics = Physics(objects)

	print "F1 for switch between Qwerty and Dvorak"
	print "F2 for switch debugLines"
	print "F6 for switch drawAxes"
	print "F7 for switch wireframe"
	print "+/- to increase/decrease number of debug-lines level"
	print "WASD to move. Mouse to look"



init()
graphics.initGL()
Global.menu.init_font()

graphics.addSurface(0, "Terrain.raw", "test.bmp")

if sys.platform != "win32":
	thread.start_new_thread(graphics.printFPS, ())

def editpos():
	Global.Input.xpos = -400
	Global.Input.ypos = 360
	Global.Input.zpos = -45
	Global.Input.xrot = -333
	Global.Input.yrot = -250


thread.start_new_thread(Global.Input.handle_input, ())

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

Global.menu.setBackground("IMG_1133.jpg")
Global.menu.addMenuEntry("Start", startGame)
Global.menu.addMenuEntry("Options", options)
Global.menu.addMenuEntry("Quit", quit)

while not Global.quit:
	if sys.platform == "win32":
		if time.time() - fpsTime >= 1.0:
			fpsTime = time.time()
			graphics.printFPS()
		Global.Input.handle_mouse()

	if Global.mainMenuOpen:
		Global.menu.draw()
	else:
		objects = physics.update()
		graphics.draw(objects)
