from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from Global import Global, loadRaw, loadTexture, loadObj
try:
	import numpy as Numeric
except:
	import Numeric
import pygame
import math
import time
import random
import graphics

class Sun:
	def __init__(self):
		vertices, vnormals, f, self.vertexCount = loadObj("models/sun.obj")

		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)
	
		#self.angle = 3.1415/4.0 #in radians
		self.angle = 90.0 * (3.1415/180.0)
	def update(self):
		# 360 / 24 = 15
		# 15/60 = 0.25

		now = time.gmtime()
		self.angle += 0.003
		#self.angle = (15 * (now.tm_hour - 6) + 0.25*now.tm_min) * (3.1415/180.0)
		#self.angle = 160 * (3.1415/180.0)
		#self.angle = 20 * (3.1415/180.0)
		self.x = math.cos(self.angle) * 900
		self.y = math.sin(self.angle) * 900

		if -3.1415 < self.angle < 3.1415:
			#print "day"
			pass
		else:
			#print "night"
			pass
	def draw(self):
		self.update()

		glPushMatrix()


		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 1.0, 0.0)
		
		glRotatef(60.0, 0.0, 1.0, 0.0)
		glScalef(0.1, 0.1, 0.1)
		glTranslatef(self.x, self.y, 0.0)

		#glPushMatrix()
		#glLightfv(GL_LIGHT0, GL_POSITION, (self.x, self.y, 0.0, 10000.0) )

		#glLightfv(GL_LIGHT1, GL_POSITION, (1.0, 1.0, 0.0, 0.0) )
		#glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0) )
		#glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0) )

		glLightfv(GL_LIGHT1, GL_POSITION, (0.0, 0.0, 0.0, 1.0))
		glLightfv(GL_LIGHT1, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
		glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
		glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 1.0, 0.0, 1.0))

		#glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 180)
		#glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (1.0, 1.0, 1.0))
		#glPopMatrix()
	
		#glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 0)
		glMaterialfv(GL_FRONT, GL_EMISSION, (0.3, 0.1, 0.0, 1.0))
		#glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.5, 0.5, 0.0, 1.0))
		#glMaterialfv(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
		#glMaterialfv(GL_FRONT, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
		#glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.0, 0.0, 0.0, 1.0))

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		glMaterialfv(GL_FRONT, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))

		#glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()

class Skydome:
	def __init__(self):
		self.sun = Sun()


		vertices, vnormals, f, self.vertexCount = loadObj("models/skydome.obj")

		self.textureId, textureWidthRatio, textureHeightRatio = loadTexture("cl.jpg")

		xMax = xMin = vertices[0][0]
		zMax = zMin = vertices[0][2]
		for i in vertices:
			if i[0] < xMin: xMin = i[0]
			elif i[0] > xMax: xMax = i[0]

			if i[2] < zMin: zMin = i[2]
			elif i[2] > zMax: zMax = i[2]

		sizeX = xMax - xMin
		sizeY = zMax - zMin

		texCoords = Numeric.zeros((self.vertexCount, 2), 'f')

		nIndex = 0
		for i in vertices:
			texCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			texCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			nIndex += 1

		self.verticesId, self.normalsId, self.texCoordsId = graphics.createVBO(
				vertices, vnormals, texCoords)

		self.vertices = vertices
		self.normals = vnormals
	def draw(self):
		glPushMatrix()
		
		glDisable(GL_LIGHTING)
		glColor3f(0.0, 0.749, 1.0)

		glScalef(10.0, 10.0, 10.0)
		glTranslatef(0.0, -20.0, 0.0)
		
		self.sun.draw()

		#glColor3f(0.0, 0.749, 1.0)
		glColor3f(1.0, 1.0, 1.0)
		#glDisable(GL_DEPTH_TEST)

		glBindTexture(GL_TEXTURE_2D, self.textureId)
		glEnable(GL_TEXTURE_2D)
		
		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount,
				self.texCoordsId)

		glDisable(GL_TEXTURE_2D)

		#glEnable(GL_DEPTH_TEST)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)


		"""glDisable(GL_LIGHTING)
		vertices = self.vertices
		normals = self.normals
		for i in xrange(len(vertices)):
			glBegin(GL_LINES)
			glVertex3f(vertices[i][0], vertices[i][1], vertices[i][2])
			glVertex3f(vertices[i][0] + normals[i][0]*20, vertices[i][1] + normals[i][1]*20, vertices[i][2] + normals[i][2]*20)
			glEnd()
		glEnable(GL_LIGHTING)"""

		if not light:
			glDisable(GL_LIGHTING)

		glEnable(GL_LIGHTING)


		glPopMatrix()
