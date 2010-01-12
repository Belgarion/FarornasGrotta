from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from gameObject import GameObject
import graphics

class Player(GameObject):
	def __init__(self):
		GameObject.__init__(self, "Player 1", (0.0, 20.0, -40.0), (0.0, 180.0, 0.0), 100, (0.0, 0.0, 0.0))

		vertices, vnormals, f, self.vertexCount = graphics.loadObj("models/player.obj")
		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		self.x = 100
		self.y = 100
	def jump(self):
		if self.velocity[1] == 0: #< 1 and self.velocity[1] > -1:
			self.position = (self.position[0], self.position[1] + 1.0, self.position[2])
			self.velocity = (self.velocity[0], self.velocity[1] - 9.82, self.velocity[2])
	def draw(self):
		glPushMatrix()

		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 1.0, 0.0)
		
		#glTranslatef(self.x, self.y, 0.0)
		glTranslatef(self.position[0], self.position[1], self.position[2])
		glRotatef(self.orientation[1], 0.0, 1.0, 0.0)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()
