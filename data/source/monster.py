from gameObject import GameObject

import threading
import time

import sys, os

if os.path.basename(sys.argv[0]) != "server.py":
	from OpenGL.GL import *
	from OpenGL.GL.ARB.vertex_buffer_object import *

	import graphics


class Monster(GameObject):
	def __init__(self, type, name, position, orientation, mass, objects, \
			server = False, guid = None):
		self.objects = objects

		GameObject.__init__(self, type, name, position,
				orientation, mass, (0.0, 0.0, 0.0), guid)

		if server:
			return

		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj(self.objPath())
		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)
	def jump(self):
		if self.data.velocity[1] == 0:
			self.data.position = (self.data.position[0],
					self.data.position[1] + 0.1,
					self.data.position[2])

			self.data.velocity = (self.data.velocity[0],
					self.data.velocity[1] - 9.82,
					self.data.velocity[2])
	def draw(self):
		glPushMatrix()

		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 0.0, 0.0)

		glTranslatef(self.data.position[0],
				self.data.position[1],
				self.data.position[2])
		glRotatef(self.data.orientation[1], 0.0, 1.0, 0.0)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()
	def intelligence(self):
		# implement this in subclasses
		pass

	class IntelligenceThread(threading.Thread):
		def __init__(self, monster):
			self.monster = monster
			threading.Thread.__init__(self)

		def run(self):
			while True:
				self.monster.intelligence()
				time.sleep(0.01)
