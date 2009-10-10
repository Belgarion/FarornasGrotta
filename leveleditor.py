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
from main import *
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

Global.Input = input()
graphics = Graphics()

g_nFrames = 0.0

level = []


width = 0
height = 0
texture = 0

NO_VBOS = True

g_fVBOSupported = False
g_pMesh = None
g_pMesh2 = None
g_flYRot = 0.0

g_prev_draw_time = 0.0

CVec = CVert


class Leveleditor:
	"""This class was made so we can integrated the leveleditor in the game"""

	def __init__ (self):
		thread.start_new_thread(Global.Input.handle_input, ())


	def draw (self):
		pass
	

thread.start_new_thread(graphics.printFPS, ())

pygame.init()
pygame.display.set_mode((640,480), pygame.DOUBLEBUF|pygame.OPENGL)

main.init()
graphics.initGL()

graphics.addSurface(0, "level2", "grass.jpg")
graphics.addSurface(50, "level", "test.bmp")


t = threading.Timer(2.0, main.editpos)
t.start()

thread.start_new_thread(Global.Input.handle_input, ())



while not Global.quit:		

	graphics.draw()
	
	#Print the position every 1000th frame
	if g_nFrames == 1:
		#print xpos, ypos, zpos, xrot, yrot 
		pass

