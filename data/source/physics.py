import time
import sys

#TODO: Use acceleration to change velocity
class Physics:
	def __init__(self, main):
		self.main = main
		self.objects = []
		self.lastTime = time.time()
		self.isClient = True

	def updateObjects(self, objects):
		self.objects = objects

	def update(self):
		self.time = time.time()
		relTime = self.lastTime-self.time

	 	for i in xrange(len(self.objects)):
			if self.isClient:
				if self.objects[i].data.id == self.main.player.data.id:
					self.objects[i] = self.updatePos(self.objects[i], relTime)
			else:
				if self.objects[i].data.type != "Player":
					self.objects[i] = self.updatePos(self.objects[i], relTime)

		self.lastTime = time.time()

		return self.objects

	def updatePos(self, obj, relTime):
		velocity = obj.data.velocity
		mass = obj.data.mass

		y = obj.data.position[1]
		velY = obj.data.velocity[1]

		if obj.checkCollision():# and velY > 0:
			velY = 0
		else:
			velY += -9.82*relTime
			y += velY*relTime

		obj.data.velocity = (velocity[0], velY , velocity[2])
		obj.data.position = (obj.data.position[0]+obj.data.velocity[0]*relTime,
				y,
				obj.data.position[2] + obj.data.velocity[2]*relTime)

		return obj
