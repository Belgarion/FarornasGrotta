class GameObject:
	def __init__(self, name, position, orientation, mass, velocity ):
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity
	def draw(self):
		pass
	def checkCollision(self):
		if self.position[1] <= 0:
			self.position = (self.position[0], 0, self.position[2])
			return True
		return False
