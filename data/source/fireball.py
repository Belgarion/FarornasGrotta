from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from gameObject import GameObject
import graphics

class Fireball(GameObject):
	def __init__(self, name = "Fireball 1", position = (0.0, 20.0, -40.0), \
			orientation = (0.0, 180.0, 0.0), mass = 20, velocity = (0.0, 0.0, 0.0), \
			guid = None, sound = None):
		GameObject.__init__(self, "Fireball", name, position,
				orientation, mass, velocity, guid)

		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj("data/model/Fireball.obj")
		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		self.sound = sound

	def draw(self):
		glPushMatrix()

		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 0.0, 1.0)

		glTranslate(self.data.position[0],
				self.data.position[1],
				self.data.position[2])
		glRotatef(self.data.orientation[1], 0.0, 1.0, 0.0)

		glScalef(0.02, 0.02, 0.02)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()
