import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
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
	def __init__(self, main):
		self.main = main
		self.config = self.main.config
		self.menuEntries = []
		self.hasBackground = False
		self.isSubMenu = False
		self.row = 0
		pass
		#self.backgroundTextureId = None
		self.verticesId = None
		self.texCoordsId = None
		#self.font = font
		self.row = 0

	def menu_is_open(self, caller, purpose):
		if purpose is "STOP_PURPOSE":
			print "menu stopping"
		elif purpose is "INIT_PURPOSE":
			if not self.menuEntries: # if the first one
				if not self.isSubMenu:
					self.initMenus()
			print "menu starting"
		elif purpose is "FRAME_PURPOSE":
			#print "menu processing"

			#print self.main.input.keys["KEY_A"]
			self.draw()
			if self.main.input.keys["KEY_ESCAPE"] == 1:
				self.main.state_manager.pop(None)
				self.main.input.keys["KEY_ESCAPE"] = 0
			elif self.main.input.keys["KEY_UP"] == 1:
				if self.row > 0:
					self.row -= 1
				self.main.input.keys["KEY_UP"] = 0
			elif self.main.input.keys["KEY_DOWN"] == 1:
				if self.row < len(self.menuEntries) - 1:
					self.row += 1
				self.main.input.keys["KEY_DOWN"] = 0
			elif self.main.input.keys["KEY_RETURN"] == 1:
				try:
					self.menuEntries[self.row][1]()
				except:
					print "Error running function for menu entry"
					#print sys.exc_info
					traceback.print_exc()
				self.main.input.keys["KEY_RETURN"] = 0

		else:
			print "menu no purpose"

	def draw(self):
		glClearColor(0.4, 0.4, 0.4, 0.0)

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		glDisable(GL_LIGHTING)

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

	def setBackground(self, path):
		self.backgroundTextureId, textureWidthRatio, textureHeightRatio = \
				graphics.loadTexture(path)

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

	def initMenus(self):
		self.font = Font()

		self.menu = self

		self.menu.setBackground("data/image/img2.png")

		def MStart():
			def MResume():
				self.main.state_manager.pop(None)
			self.menu.menuEntries[self.menu.row] = ("Resume", MResume)
			self.main.state_manager.push(self.main.runGame, None)
		self.menu.addMenuEntry("Start", MStart)

		def MOptions():
			self.main.state_manager.push(self.optionsMenu.menu_is_open, None)
		self.menu.addMenuEntry("Options", MOptions)

		def MQuit():
			self.main.state_manager.pop_all(None)
		self.menu.addMenuEntry("Quit", MQuit)

		#self.optionsMenu = Menu(self.graphics, self.config, self.font)
		self.optionsMenu = Menu(self.main)
		self.optionsMenu.font = self.font
		self.optionsMenu.isSubMenu = True
		self.optionsMenu.setBackground("data/image/img2.png")

		resolutions = [(640, 480),
				(800, 600),
				(1024, 768),
				(1280, 960),
				(1400, 1050),
				(1600, 1200),
				(1680, 1260),
				(1920, 1440),
				(2048, 1536)]

		def OMResolution():
			om = self.optionsMenu
			wstr, hstr = om.menuEntries[om.row][0].split(":")[1] \
					.lstrip().split("x")
			w, h = int(wstr), int(hstr)
			for i, r in enumerate(resolutions):
				if r[0] == w or \
						(len(resolutions) > i + 1 and resolutions[i+1][0] > w):
					index = (i + 1) % (len(resolutions))
					nw, nh = resolutions[index]
					self.config.set("Resolution", "Width", str(nw))
					self.config.set("Resolution", "Height", str(nh))
					om.menuEntries[om.row] = ("Resolution: " + \
							str(nw) + "x" + str(nh),
							om.menuEntries[om.row][1])
					break

		self.optionsMenu.addMenuEntry(
				"Resolution: " + self.config.get("Resolution","Width") \
						+ "x" + \
						self.config.get("Resolution","Height"),
				OMResolution)

		keyboardLayouts = ["qwerty", "dvorak"]
		def OMKeyboardLayout():
			om = self.optionsMenu
			layout = om.menuEntries[om.row][0].split(":")[1].lstrip()
			for i, l in enumerate(keyboardLayouts):
				if layout == l:
					index = (i + 1) % (len(keyboardLayouts))
					nl = keyboardLayouts[index]
					self.config.set("Input", "KeyboardLayout", nl)
					om.menuEntries[om.row] = \
							("Keyboard Layout: " + nl,
									om.menuEntries[om.row][1])

		self.optionsMenu.addMenuEntry(
			"Keyboard Layout: " + self.config.get("Input", "KeyboardLayout"),
			OMKeyboardLayout)

		def OMBack():
			with open("config", "wb") as configfile:
				self.main.config.write(configfile)
			self.main.state_manager.pop(None)

		self.optionsMenu.addMenuEntry("Back", OMBack)


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
			def draw(self):
				pygame.display.flip()

	def addMenuEntry(self, title, function):
		print "Adding menu entry:", title
		self.menuEntries.append( (title, function) )
