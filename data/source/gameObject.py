import uuid
from graphics import *

class GameObjectData:
	def __init__(self, id, type, name, position, orientation, mass, velocity,
			filename = ""):
		self.id = str(id)
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity

		# Fulhack
		self.width, self.heigth, self.depth = \
			Calculate_Size(Get_Vertices(filename))

class GameObject:
	def __init__(self, type, name, position, orientation, mass, velocity, \
			guid = None, filename = ""):
		if guid == None:
			guid = uuid.uuid4().hex
		self.data = GameObjectData(guid, type, name, position,
				orientation, mass, velocity, filename)

	def draw(self):
		pass

	def checkCollision(self):
		if self.data.position[1] <= 0:
			self.data.position = \
					(self.data.position[0], 0, self.data.position[2])
			return True
		return False
