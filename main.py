#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
import sys
import time
import pygame
import math
import random
import threading
import thread
import OpenGL
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
	pygame.display.set_mode((640,480), pygame.DOUBLEBUF|pygame.OPENGL)

	global level, level2

	pygame.mouse.set_visible(0)
	pygame.event.set_grab(1)

	rel = pygame.mouse.get_rel()


	Global.level = load_level("Terrain.raw")

	monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0,), 100, (0.0,0.0,0.0))
	objects.append(monster)
	physics = Physics(objects)



init()
graphics.initGL()
Global.menu.init_font()

#graphics.addSurface(50, "level2", "grass.jpg")
#graphics.addSurface(0, "level", "test.bmp")
#graphics.addSurface(50, "Terrain.raw", "grass.jpg")
graphics.addSurface(0, "Terrain.raw", "grass.jpg")
#graphics.addSurface(0, "skydome.raw", "test.bmp")

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

def a():
	print "a"

def b():
	print "b"

Global.menu.setBackground("IMG_1133.jpg")
Global.menu.addMenuEntry("Start", startGame)
Global.menu.addMenuEntry(".qjk", a)
Global.menu.addMenuEntry("aoeu", b)

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

