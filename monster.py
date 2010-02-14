from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from gameObject import GameObject
import graphics

import threading
import time

from Global import Global


#TODO: Monsters has to be handled by the server somehow

class Monster(GameObject):
	def __init__(self, name, position, orientation, mass, objects):
		self.objects = objects

		GameObject.__init__(self, name, position,
				orientation, mass, (0.0, 0.0, 0.0))

		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj(self.objPath())
		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		self.x = 100
		self.y = 100
	def jump(self):
		if self.velocity[1] == 0:
			self.position = (self.position[0],
					self.position[1] + 0.1,
					self.position[2])

			self.velocity = (self.velocity[0],
					self.velocity[1] - 9.82,
					self.velocity[2])
	def draw(self):
		glPushMatrix()

		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 0.0, 0.0)

		#glTranslatef(self.x, self.y, 0.0)
		glTranslatef(self.position[0], self.position[1], self.position[2])
		glRotatef(self.orientation[1], 0.0, 1.0, 0.0)

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
			while not Global.quit:
				self.monster.intelligence()
				time.sleep(0.01)
