import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.vertex_buffer_object import *
import graphics
try:
	import numpy as Numeric
except:
	import Numeric
from font import Font
from Global import Global
import sys
import traceback

class Menu:
	def __init__(self, graphics, config):
		self.graphics = graphics

		self.hasBackground = False
		self.backgroundTextureId = None
		self.verticesId = None
		self.texCoordsId = None
		self.menuEntries = []
		self.font = None
		self.row = 0
		self.config = config
		self.current = self
	def init_font(self):
		self.font = Font()
	def KeyHandler(self):
		for event in pygame.event.get():
			if self.keyHandler(event):
				# Key already handled
				continue

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					Global.quit = 1
				elif event.key == pygame.K_UP:
					if self.row > 0:
						self.row -= 1
				elif event.key == pygame.K_DOWN:
					if self.row < len(self.menuEntries) - 1:
						self.row += 1
				elif event.key == pygame.K_RETURN:
					try:
						self.menuEntries[self.row][1]()
					except:
						print "Error running function for menu entry"
						#print sys.exc_info
						traceback.print_exc()
	def keyHandler(self, event):
		# Custom handler
		return 0
	def setBackground(self, filename):
		self.backgroundTextureId, textureWidthRatio, textureHeightRatio = \
				graphics.loadTexture(filename)

		if self.verticesId == None:
			vertices = Numeric.zeros((4, 3), 'f')
			vertices[1, 0] = 640
			vertices[2, 0] = 640
			vertices[2, 1] = 480
			vertices[3, 1] = 480
			self.verticesId = glGenBuffersARB(1)

			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
			glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)

		if self.texCoordsId == None:
			texCoords = Numeric.zeros((4, 2), 'f')
			texCoords[1, 0] = 1.0*textureWidthRatio
			texCoords[2, 0] = 1.0*textureWidthRatio
			texCoords[2, 1] = 1.0*textureHeightRatio
			texCoords[3, 1] = 1.0*textureHeightRatio

			self.texCoordsId = glGenBuffersARB(1)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.texCoordsId)
			glBufferDataARB(GL_ARRAY_BUFFER_ARB, texCoords, GL_STATIC_DRAW_ARB)

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

		row = 7
		i = 0
		for entry in self.menuEntries:
			if self.row == i:
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
