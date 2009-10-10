#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import pygame
import math
import random
import threading
import thread
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
from OpenGL.extensions import *
from input import *

Input = input()

g_nFrames = 0.0

level = []

width = 0
height = 0
texture = 0


class Vert:
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0

class TexCoord:
	def __init__(self):
		self.u = 0.0
		self.v = 0.0

vertexCount = 0
vertices = Vert()
texcoords = TexCoord()

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
	print level
	return level


def init():
	global level
	pygame.mouse.set_visible(0)
	pygame.event.set_grab(1)

	rel = pygame.mouse.get_rel()

	level = load_level("level")


def initGL():
	global width, height, texture
	image = pygame.image.load("test.bmp")
	
	width = image.get_width()
	height = image.get_height()
	print width
	print height
	texture = glGenTextures(1)

	glBindTexture(GL_TEXTURE_2D, texture)
	
	
	GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
	GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.get_width(), image.get_height(), 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
	GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
	GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
	GL.glEnable(GL.GL_TEXTURE_2D)

	glEnable(GL_TEXTURE_2D)
	
	glClearColor( 0.0, 0.0, 0.0, 0.0)
	glClearDepth(1.0)
	glDepthFunc(GL_LESS)
	glEnable(GL_DEPTH_TEST)
	glShadeModel(GL_SMOOTH)

	glMatrixMode(GL_PROJECTION)
	
	#glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
	glViewport (0, 0, 640, 480)
	glLoadIdentity()
	gluPerspective( 60, 640/480, 0.1, 1000.0)
	glMatrixMode(GL_MODELVIEW)

def printFPS():
	global g_nFPS, g_nFrames, g_dwLastFPS, Input
	while True:
		pygame.display.set_caption("FarornasGrotta - %f FPS" % (g_nFrames))
		g_nFrames = 0
		time.sleep(1.0)
		print Input.xrot


thread.start_new_thread(printFPS, ())


def draw():
	global g_nFPS, g_nFrames, g_dwLastFPS
	
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT ) 
	glLoadIdentity()
	glRotatef(Input.xrot, 1.0, 0.0, 0.0)
	glRotatef(Input.yrot, 0.0, 1.0, 0.0)
	glTranslated(-Input.xpos, -Input.ypos,-Input.zpos)
	
	g_nFrames += 1
	
	key = 0
	x = 0
	y = 0 # y is actually z here
	errors = 0
	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, texture)
	for line in level:
		if(x+1 < len(level)):
			for point in line:
				if y+1 < len(line):
				   
					glBegin(GL_TRIANGLE_STRIP)
					glTexCoord2f(float(x)/width, float(y)/height)
					glVertex3f(x, level[x][y], y)
		 
					glTexCoord2f(float(x)/width, (float(y)+1)/height)
					glVertex3f(x, level[x][y+1], y+1)
					
					glTexCoord2f((float(x)+1)/width, float(y)/height)
					glVertex3f(x+1, level[x+1][y], y)
					
					glTexCoord2f((float(x)+1)/width, (float(y)+1)/height)
					glVertex3f(x+1, level[x+1][y+1], y+1)
					glEnd()
				y += 1
		x += 1
		y = 0
	
	
	"""
	glPointSize(4.0)
	x=0
	y=0
	for line in level:
		for point in line:
			glBegin(GL_POINTS)
			glVertex3f(x, level[x][y], y)
			glEnd()
			y+=1
		y=0
		x+=1
	"""
	glFlush()

	pygame.display.flip()

pygame.init()
pygame.display.set_mode((640,480), pygame.DOUBLEBUF|pygame.OPENGL)

init()
initGL()


def editpos():
	global Input
	Input.xpos = -400
	Input.ypos = 360
	Input.zpos = -45
	Input.xrot = -333
	Input.yrot = -250
	print "hej"


t = threading.Timer(2.0, editpos)
t.start()

while True:

	Input.handle_input()
	
	draw()
	
	#Print the position every 1000th frame
	if g_nFrames == 1:
		print Input.xpos, Input.ypos, Input.zpos, Input.xrot, Input.yrot 




