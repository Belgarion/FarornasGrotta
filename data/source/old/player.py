from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from gameObject import GameObject
from object import *

import graphics
import math

class Player:
	def __init__(self, main, name = "player1_1", position = (0.0, 20.0, -40.0), \
			orientation = (0.0, 180.0, 0.0), mass = 100, guid = None, sound = None):
		self.main = main
		self.object = Object("player1", name, position,
				orientation, 1.0, mass, (0.0, 0.0, 0.0), guid)
	
		self.main.physics.add_object(self.object)
		self.sound = sound
		self.rotated = 0.0

	def makeNoise(self):
		if self.sound:
			self.sound.Update_Sound()

	def walk(self, main, direction):
		xrotrad = (main.input.xrot + direction) / 180 * math.pi
		yrotrad = (main.input.yrot + direction) / 180 * math.pi
		if main.graphics.spectator:
			main.input.xpos += math.sin(yrotrad) * main.distance_moved
			main.input.zpos -= math.cos(yrotrad) * main.distance_moved
			main.input.ypos -= math.sin(xrotrad) * main.distance_moved
		else:
			new_position = (
					self.object.position[0] \
							+ math.sin(yrotrad) * main.distance_moved,
					self.object.position[1],
					self.object.position[2] \
							- math.cos(yrotrad) * main.distance_moved
					)
			if self.main.physics.collisionPlayerMonster(new_position):
				return
			else:
				main.player.object.position = new_position

	def jump(self):
		if self.object.velocity[1] == 0:
			self.object.position = (self.object.position[0],
					self.object.position[1] + 0.1,
					self.object.position[2])

			self.object.velocity = (self.object.velocity[0],
					self.object.velocity[1] - 9.82,
					self.object.velocity[2])
