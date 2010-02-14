from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.vertex_buffer_object import *

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
		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj("models/sun.obj")

		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		#self.angle = 3.1415/4.0 #in radians
		self.angle = 90.0 * (3.1415/180.0)
	def update(self):
		# 360 / 24 = 15
		# 15/60 = 0.25

		now = time.gmtime()
		self.angle = (15 * (now.tm_hour - 6) + 0.25*now.tm_min) * (3.1415/180.0)

		#self.angle += 0.003

		self.x = math.cos(self.angle) * 900
		self.y = math.sin(self.angle) * 900
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
		glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.3, 0.3, 0.2, 1.0))

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

class Moon:
	def __init__(self):
		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj("models/moon.obj")

		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		self.angle = 270.0 * (3.1415/180.0)
	def update(self):
		# 360 / 24 = 15
		# 15/60 = 0.25

		now = time.gmtime()
		self.angle = \
				(15 * (now.tm_hour - 18) + 0.25*now.tm_min) * (3.1415/180.0)

		#self.angle += 0.003

		self.x = math.cos(self.angle) * 900
		self.y = math.sin(self.angle) * 900
	def draw(self):
		self.update()

		glPushMatrix()


		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(0.4, 0.4, 0.4)

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
		glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.3, 0.3, 0.3, 1.0))

		#glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 180)
		#glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (1.0, 1.0, 1.0))
		#glPopMatrix()

		#glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, 0)
		glMaterialfv(GL_FRONT, GL_EMISSION, (0.1, 0.1, 0.1, 1.0))
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
		self.moon = Moon()


		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj("models/skydome.obj")

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
		nightTexCoords = Numeric.zeros((self.vertexCount, 2), 'f')

		self.textureId, textureWidthRatio, textureHeightRatio = \
				graphics.loadTexture("cl.jpg")

		nIndex = 0
		for i in vertices:
			texCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			texCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			nIndex += 1

		self.nightTextureId, textureWidthRatio, textureHeightRatio = \
				graphics.loadTexture("nightsky.jpg")
		nIndex = 0
		for i in vertices:
			nightTexCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			nightTexCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			nIndex += 1

		self.nightTexCoordsId = glGenBuffersARB(1)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.nightTexCoordsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, nightTexCoords, GL_STATIC_DRAW_ARB)

		self.verticesId, self.normalsId, self.texCoordsId = graphics.createVBO(
				vertices, vnormals, texCoords)

		self.vertices = vertices
		self.normals = vnormals
	def draw(self):
		glPushMatrix()

		glDisable(GL_LIGHTING)

		glScalef(10.0, 10.0, 10.0)
		glTranslatef(0.0, -20.0, 0.0)

		now = time.gmtime()
		if now.tm_hour > 6 and now.tm_hour < 18:
			self.sun.draw()
			brightness = \
					((15 * (now.tm_hour - 6) + \
							0.25*now.tm_min) * (3.1415/180.0)) / 6.28
			texCoordsId = self.texCoordsId
			textureId = self.textureId
		else:
			self.moon.draw()
			brightness = 1.0
			texCoordsId = self.nightTexCoordsId
			textureId = self.nightTextureId

		glColor3f(brightness, brightness, brightness)
		#glDisable(GL_DEPTH_TEST)

		glBindTexture(GL_TEXTURE_2D, textureId)
		glEnable(GL_TEXTURE_2D)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount,
				texCoordsId)

		glDisable(GL_TEXTURE_2D)

		#glEnable(GL_DEPTH_TEST)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		if not light:
			glDisable(GL_LIGHTING)

		glEnable(GL_LIGHTING)


		glPopMatrix()
