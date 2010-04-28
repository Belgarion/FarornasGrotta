import uuid
import graphics

class GameObjectData:
	def __init__(self, id, type, name, position, orientation, scale, mass, velocity, owner):
		if id == None:
			id = uuid.uuid4().hex
		self.id = str(id)
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation
		self.scale = scale
		self.mass = mass
		self.velocity = velocity
		self.hp = 100
		self.frags = 0
		self.deaths = 0
		self.owner = owner

		# Fulhack
		filename = "data/model/"+type+".obj"
		self.width, self.height, self.depth = \
			graphics.Calculate_Size(graphics.Get_Vertices(filename))

class GameObject:
	def __init__(self, type, name, position, orientation, scale, mass, velocity, \
			guid = None, owner = None):
		self.data = GameObjectData(guid, type, name, position,
				orientation, scale, mass, velocity, owner)

	def draw(self):
		pass

	def checkCollision(self):
		if self.data.position[1] <= 0:
			self.data.position = \
					(self.data.position[0], 0, self.data.position[2])
			return True
		return False

	def handleCollision(self):
		pass
