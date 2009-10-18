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
	def __init__(self):
		self.hasBackground = False
		self.backgroundTextureId = None
		self.verticesId = None
		self.texCoordsId = None
		self.menuEntries = []
		self.font = None
	
	def init_font(self):
		self.font = Font()

	def setBackground(self, filename):
		image = pygame.image.load(filename)

		width = nearestPowerOfTwo(image.get_width())
		height = nearestPowerOfTwo(image.get_height())

		textureWidthRatio = float(image.get_width()) / width
		textureHeightRatio = float(image.get_height()) / height

		if width > glGetIntegerv(GL_MAX_TEXTURE_SIZE):
			sys.stderr.write("ERROR: Texture is bigger than the maximum texture size of your graphics card\n")
			return

		if self.verticesId == None:
			vertices = Numeric.zeros((4, 3), 'f')
			vertices[1, 0] = 640.0
			vertices[2, 0] = 640.0
			vertices[2, 1] = 480.0
			vertices[3, 1] = 480.0
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


		self.backgroundTextureId = texture = glGenTextures(1)

		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
		glTexSubImage2D(GL_TEXTURE_2D, 0 , 0, 0, image.get_width(), image.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glEnable(GL_TEXTURE_2D)

		if Global.VBOSupported:
			glEnableClientState(GL_VERTEX_ARRAY)
			glEnableClientState(GL_TEXTURE_COORD_ARRAY)

			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
			glVertexPointer(3, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.texCoordsId)
			glTexCoordPointer(2, GL_FLOAT, 0, None)

			glDisableClientState(GL_VERTEX_ARRAY)
			glDisableClientState(GL_TEXTURE_COORD_ARRAY)


		glDisable(GL_TEXTURE_2D)

		self.hasBackground = True


	def draw(self):
		glClearColor(0.4, 0.4, 0.4, 0.0)

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		glDisable(GL_LIGHTING)

		if Global.wireframe:
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


		if Global.mainMenuRow > len(self.menuEntries)  - 1:
			Global.mainMenuRow = len(self.menuEntries) - 1

		row = 2
		i = 0
		for entry in self.menuEntries:
			if Global.mainMenuRow == i:
				glColor3f(0.0, 1.0, 0.0)
			else:
				glColor3f(1.0, 0.0, 0.0)

			glBegin(GL_QUADS)
			glVertex3f(50.0,  480 - 50.0*row, 1.0)
			glVertex3f(590.0, 480 - 50.0*row, 1.0)
			glVertex3f(590.0, 480 - 50.0*row + 40, 1.0)
			glVertex3f(50.0,  480 - 50.0*row + 40, 1.0)
			glEnd()

			glColor3f(1.0, 1.0, 0.0)
			self.font.glPrint(50.0, 480.0 - 50.0*row, entry[0])

			i += 1
			row += 1


		glEnable(GL_LIGHTING)

		glFlush()
		pygame.display.flip()
		
	def addMenuEntry(self, title, function):
		print "Adding menu entry:", title
		self.menuEntries.append( (title, function) )
