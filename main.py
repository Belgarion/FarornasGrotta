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
from graphics import Graphics
from physics import Physics
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

Global.Input = input()
graphics = Graphics()
physics = 0
objects = []

g_nFrames = 0.0

level = []

width = 0
height = 0
texture = 0

NO_VBOS = True

g_fVBOSupported = False
g_pMesh = None
g_pMesh2 = None

class GameObject:
	def __init__(self, name, position, orientation, mass, velocity ):
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity	

def load_level(name):
	f = open(name, "r")
	lines = f.readlines()
	f.close()
	level = []
	x = 0
	y = 0
	for line in lines:
		line2 = []
		for i in line.rsplit(" "):
			line2.append(float(i.replace("\n", "")))
			y+=1
		level.append(line2)
		x+=1
	return level

def init():
	global physics
	pygame.init()
	pygame.display.set_mode((640,480), pygame.DOUBLEBUF|pygame.OPENGL)

	pygame.mouse.set_visible(0)
	pygame.event.set_grab(1)

	rel = pygame.mouse.get_rel()

	Global.level = load_level("level")

	monster = GameObject("monster1", (0.0, 100.0, 0.0), (0.0, 0.0, 0.0,), 100, (0.0,0.0,0.0))
	objects.append(monster)
	physics = Physics(objects)


init()
graphics.initGL()

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

