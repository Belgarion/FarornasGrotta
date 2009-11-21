from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from Global import *
from gameObject import GameObject

class Player(GameObject):
	def __init__(self):
		GameObject.__init__(self, "Player 1", (0.0, 20.0, -40.0), (0.0, 180.0, 0.0), 100, (0.0, 0.0, 0.0))

		vertices, vnormals, f, self.vertexCount = loadObj("player.obj")

		self.verticesId = glGenBuffersARB(1)
		self.normalsId = glGenBuffersARB(1)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.normalsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vnormals, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		self.x = 100
		self.y = 100
	def jump(self):
		#if checkCollisionY():
		self.position = (self.position[0], self.position[1] + 1.2*10, self.position[2])
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

		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
		glVertexPointer(3, GL_FLOAT, 0, None)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.normalsId)
		glNormalPointer(GL_FLOAT, 0, None)
		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_NORMAL_ARRAY)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()
