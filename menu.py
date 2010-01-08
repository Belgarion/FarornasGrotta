from Global import Global
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from graphics import nearestPowerOfTwo
try:
	import numpy as Numeric
except:
	import Numeric
from font import Font

class Menu:
	def __init__(self, graphics,config):
		self.graphics = graphics
			
		self.hasBackground = False
		self.backgroundTextureId = None
		self.verticesId = None
		self.texCoordsId = None
		self.menuEntries = []
		self.font = None
		self.mainMenuRow = 0
		self.config = config
		
	
	def init_font(self):
		self.font = Font()

	def setBackground(self, filename):
		self.backgroundTextureId, textureWidthRatio, textureHeightRatio = self.graphics.loadTexture(filename)

		if self.verticesId == None:
			vertices = Numeric.zeros((4, 3), 'f')
			vertices[1, 0] = float(self.config['reswidth'])
			vertices[2, 0] = float(self.config['reswidth'])
			vertices[2, 1] = float(self.config['resheight'])
			vertices[3, 1] = float(self.config['resheight'])
			self.verticesId = glGenBuffersARB(1)

			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
			glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB) # Vertices

		if self.texCoordsId == None:
			texCoords = Numeric.zeros((4, 2), 'f')
			texCoords[1, 0] = 1.0*textureWidthRatio
			texCoords[2, 0] = 1.0*textureWidthRatio
			texCoords[2, 1] = 1.0*textureHeightRatio
			texCoords[3, 1] = 1.0*textureHeightRatio

			self.texCoordsId = glGenBuffersARB(1)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.texCoordsId)
			glBufferDataARB(GL_ARRAY_BUFFER_ARB, texCoords, GL_STATIC_DRAW_ARB) # TexCoords

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		self.hasBackground = True


	def draw(self):
		glClearColor(0.4, 0.4, 0.4, 0.0)

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		glDisable(GL_LIGHTING)

		if self.graphics.wireframe:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


		glLoadIdentity()
		glTranslated(-320.0, -240.0, -410.0)

		glColor3f(1.0, 1.0, 1.0)

		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_TEXTURE_COORD_ARRAY)

		if self.hasBackground:
			glBindTexture(GL_TEXTURE_2D, self.backgroundTextureId)
			glEnable(GL_TEXTURE_2D)

			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
			glVertexPointer(3, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.texCoordsId)
			glTexCoordPointer(2, GL_FLOAT, 0, None)
			
			glDrawArrays(GL_QUADS, 0, 4)

			glDisable(GL_TEXTURE_2D)

		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)


		if self.mainMenuRow > len(self.menuEntries)  - 1:
			self.mainMenuRow = len(self.menuEntries) - 1

		row = 7
		i = 0
		for entry in self.menuEntries:
			if self.mainMenuRow == i:
				glColor3f(0.0, 1.0, 0.0)
			else:
				glColor3f(1.0, 0.0, 0.0)

			self.font.glPrint(320.0, 480.0 - 50.0*row, entry[0])

			i += 1
			row += 1


		glEnable(GL_LIGHTING)

		glFlush()
		pygame.display.flip()
		
	def addMenuEntry(self, title, function):
		print "Adding menu entry:", title
		self.menuEntries.append( (title, function) )
