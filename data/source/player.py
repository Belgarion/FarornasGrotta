from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from gameObject import GameObject
import graphics
import math

class Player(GameObject):
	def __init__(self, name = "Player 1", position = (0.0, 20.0, -40.0), \
			orientation = (0.0, 180.0, 0.0), mass = 100, guid = None, \
			sound = None):
		GameObject.__init__(self, "Player", name, position,
				orientation, mass, (0.0, 0.0, 0.0), guid, "data/model/player1.obj")

		vertices, vnormals, f, self.vertexCount = \
				graphics.loadObj("data/model/player1.obj")
		self.verticesId, self.normalsId = graphics.createVBO(vertices, vnormals)

		self.sound = sound

	def makeNoise(self):
		if self.sound:
			self.sound.Update_Sound()

	def start_walk(self, main, direction):
		xrotrad = (main.input.xrot + direction) / 180 * math.pi
		yrotrad = (main.input.yrot + direction) / 180 * math.pi

		main.player.data.position = (
			self.data.position[0] + math.sin(yrotrad) * main.distance_moved,
			self.data.position[1],
			self.data.position[2] - math.cos(yrotrad) * main.distance_moved
		)
		#self.sound.FadeIn_Sound(self.sound.data["Run"]["UUID"]

		if self.sound.data['Run']['UUID'] == None:
			self.sound.data['Run']['UUID'] = self.sound.Play_Sound("run_ground")

		elif not self.sound.Sound_Is_Playing(self.sound.data['Run']['UUID']):
			self.sound.data['Run']['UUID'] = self.sound.Play_Sound("run_ground")

	def stop_walk(self):
		#self.sound.FadeOut_Sound(self.sound.data["Run"]["UUID"])
		self.sound.Del_Sound_Net(self.sound.data['Run']['UUID'])

	def walk(self, main, direction):
		xrotrad = (main.input.xrot + direction) / 180 * math.pi
		yrotrad = (main.input.yrot + direction) / 180 * math.pi

		# TODO: Spectator is on the wrong place.. make a own object
		if main.graphics.spectator:
			main.input.xpos += math.sin(yrotrad) * main.distance_moved
			main.input.zpos -= math.cos(yrotrad) * main.distance_moved
			main.input.ypos -= math.sin(xrotrad) * main.distance_moved
		else:
			main.player.data.position = (
				self.data.position[0] + math.sin(yrotrad) * main.distance_moved,
				self.data.position[1],
				self.data.position[2] - math.cos(yrotrad) * main.distance_moved
			)

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

		glColor3f(1.0, 1.0, 0.0)

		glTranslatef(self.data.position[0],
				self.data.position[1],
				self.data.position[2])
		glRotatef(self.data.orientation[1], 0.0, 1.0, 0.0)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()
