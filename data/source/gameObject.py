import uuid

class GameObjectData:
	def __init__(self, id, type, name, position, orientation, mass, velocity):
		self.id = str(id)
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity

class GameObject:
	def __init__(self, type, name, position, orientation, mass, velocity, \
			guid = None):
		if guid == None:
			guid = uuid.uuid4().hex
		self.data = GameObjectData(guid, type, name, position,
				orientation, mass, velocity)

	def draw(self):
		pass

	def checkCollision(self):
		if self.data.position[1] <= 0:
			self.data.position = \
					(self.data.position[0], 0, self.data.position[2])
			return True
		return False
