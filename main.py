#!/usr/bin/env python
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
from Global import Global
from physics import Physics
from graphics import *

#OpenGL.FULL_LOGGING = True

logging.basicConfig()
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
from input import *
#from pyglew import *
import numpy as Numeric
from OpenGL.GL.ARB.vertex_buffer_object import *
import traceback
import Image
from octree import *

Global.Input = input()
graphics = Graphics()
physics = 0
objects = []

g_nFrames = 0.0

level = []
level2 = []


width = 0
height = 0
texture = 0

NO_VBOS = True

g_fVBOSupported = False
g_pMesh = None
g_pMesh2 = None

class TestObject:
	def __init__(self, name, position):
		self.name = name
		self.position = position

def RenderDebugLines
	glDisable(GL_LIGHTING)

	glBegin(GL_LINES)

	 

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


	Global.level = load_level("level")

	monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0,), 100, (0.0,0.0,0.0))
	objects.append(monster)
	physics = Physics(objects)

	print sys.getrecursionlimit()
	sys.setrecursionlimit(100000000)
	print sys.getrecursionlimit()
	myTree = Octree(15000.0)

	x = 0
	z = 0

	for line in Global.level:
		for point in line:
			name = "Node__"+ str(x)+ "x" + str(z)
			pos = ( x, Global.level[x][z], z )
			testOb = TestObject(name, pos)
			myTree.insertNode(myTree.root, 15000.0, myTree.root, testOb)
		

			x += 1

		z += 1
		x = 0

	print "WARNING: ", myTree.findPosition(myTree.root, (1300, 0, 1300))


init()
graphics.initGL()

graphics.addSurface(50, "level2", "grass.jpg")
graphics.addSurface(0, "level", "test.bmp")

thread.start_new_thread(graphics.printFPS, ())

def editpos():
	Global.Input.xpos = -400
	Global.Input.ypos = 360
	Global.Input.zpos = -45
	Global.Input.xrot = -333
	Global.Input.yrot = -250
	


t = threading.Timer(2.0, editpos)
t.start()

thread.start_new_thread(Global.Input.handle_input, ())

while not Global.quit:		
	
	#physics.updateObjects(objects)
	objects = physics.update()
	graphics.draw(objects)
	
	#Print the position every 1000th frame
	if g_nFrames == 1:
		#print xpos, ypos, zpos, xrot, yrot 
		pass

