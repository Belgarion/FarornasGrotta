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

		velocity = obj.velocity
		mass = obj.mass


		obj.velocity = (velocity[0],  velocity[1] - 9.82*relTime , velocity[2]) 

		obj.position = (obj.position[0]+obj.velocity[0]*relTime, obj.position[1] +  obj.velocity[1] * relTime, obj.position[2]+obj.velocity[2]*relTime)
		

		return obj
