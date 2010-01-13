import time


class Physics:
	def __init__(self, objects):
		self.objects = objects
		self.lastTime = time.time()
	def updateObjects(self, objects):
		self.objects = objects
	def update(self):
		self.time = time.time()
		relTime = self.lastTime-self.time

		for i in xrange(len(self.objects)):
			self.objects[i] = self.updatePos(self.objects[i], relTime)
			
		self.lastTime = time.time()

		return self.objects
	def updatePos(self, obj, relTime):
		#print "updating",obj.name

		velocity = obj.velocity
		mass = obj.mass

		y = obj.position[1]
		velY = obj.velocity[1]

		if obj.checkCollision():# and velY > 0:
			velY = 0
		else:
			velY += -9.82*relTime
			y += velY*relTime

		obj.velocity = (velocity[0], velY , velocity[2]) 
		obj.position = (obj.position[0]+obj.velocity[0]*relTime, y, obj.position[2] + obj.velocity[2]*relTime)
		

		return obj
