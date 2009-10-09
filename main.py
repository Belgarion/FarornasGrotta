#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import pygame
import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU


g_nFPS = 0
g_nFrames = 0;										# // FPS and FPS Counter
g_dwLastFPS = 0;									# // Last FPS Check Time	

xpos = 0
zpos = 0
ypos = 0

xrot = 0
yrot = 0

down_pressed = 0
up_pressed = 0
left_pressed = 0
right_pressed = 0



speed = 2

# 0 = QWERTY, 1 = DVORAK
keyboardlayout = 0
level = []


width = 0
height = 0
texture = 0


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

def handle_input():
	global xrot, yrot, zpos, xpos, ypos, down_pressed, up_pressed, left_pressed, right_pressed, keyboardlayout
	
	if up_pressed:
		xrotrad = xrot/180*math.pi
		yrotrad = yrot/180*math.pi
		xpos += math.sin(yrotrad)*speed
		zpos -= math.cos(yrotrad)*speed
		ypos -= math.sin(xrotrad)*speed

	if down_pressed:

		xrotrad = xrot / 180 * math.pi
		yrotrad = yrot / 180 * math.pi
		xpos -= math.sin(yrotrad)*speed
		zpos += math.cos(yrotrad)*speed
		ypos += math.sin(xrotrad)*speed

	if left_pressed:
		yrotrad = yrot / 180 * math.pi
		xpos -= math.cos(yrotrad)*speed
		zpos -= math.sin(yrotrad)*speed
		
	if right_pressed:
		yrotrad = yrot/180*math.pi
		xpos += math.cos(yrotrad)*speed
		zpos += math.sin(yrotrad)*speed
		


	rel = pygame.mouse.get_rel()
	xrot += rel[1]/10.0 # It is y pos with mouse that rotates the X axis					   
	yrot += rel[0]/10.0
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit(1)
		if event.type == pygame.KEYDOWN:
			print "Button pressed: ", event.key
			if event.key == pygame.K_ESCAPE:
				sys.exit(1)

			if keyboardlayout:
				if int(event.key) == 228:
					up_pressed = 1
				if int(event.key) == 111:
					down_pressed = 1
				if int(event.key) == 97:
					left_pressed = 1
				if int(event.key) == 101:
					right_pressed = 1
			else:
				if int(event.key) == pygame.K_w:
					up_pressed = 1
				if int(event.key) == pygame.K_s:
					down_pressed = 1
				if int(event.key) == pygame.K_a:
					left_pressed = 1
				if int(event.key) == pygame.K_d:
					right_pressed = 1

			if int(event.key) == pygame.K_F1:
				keyboardlayout = not keyboardlayout

		if event.type == pygame.KEYUP:
			if keyboardlayout:
				if int(event.key) == 228:
					up_pressed = 0
				if int(event.key) == 111:
					down_pressed = 0
				if int(event.key) == 97:
					left_pressed = 0
				if int(event.key) == 101:
					right_pressed = 0
			else: 
				if int(event.key) == pygame.K_w:
					up_pressed = 0
				if int(event.key) == pygame.K_s:
					down_pressed = 0
				if int(event.key) == pygame.K_a:
					left_pressed = 0
				if int(event.key) == pygame.K_d:
					right_pressed = 0

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

def draw():
	global g_nFPS, g_nFrames, g_dwLastFPS

	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
	glLoadIdentity()
	glRotatef(xrot, 1.0, 0.0, 0.0)
	glRotatef(yrot, 0.0, 1.0, 0.0)
	glTranslated(-xpos, -ypos,-zpos)
	
	# // Get FPS
	milliseconds = time.clock () * 1000.0
	if (milliseconds - g_dwLastFPS >= 1000):					# // When A Second Has Passed...
		g_dwLastFPS = time.clock () * 1000.0
		g_nFPS = g_nFrames;										# // Save The FPS
		g_nFrames = 0;											# // Reset The FPS Counter

		# // Build The Title String
		#szTitle = "FarornasGrotta - %d Triangles, %d FPS" % (g_pMesh.m_nVertexCount / 3, g_nFPS );
		szTitle = "FarornasGrotta - %d FPS" % (g_nFPS);
		#if ( g_fVBOSupported ):									# // Include A Notice About VBOs
		#	szTitle = szTitle + ", Using VBOs";
		#else:
		#	szTitle = szTitle + ", Not Using VBOs";

		pygame.display.set_caption(szTitle)

	
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
from Image import *
initGL()

frames = 0

xpos = -400
ypos = 360
zpos = -45
xrot = -333
yrot = -250

while True:

	handle_input()
	
	draw()

	#Print the position every 1000th frame
	if frames % 1000 == 0:
		print xpos, ypos, zpos 

	frames += 1
