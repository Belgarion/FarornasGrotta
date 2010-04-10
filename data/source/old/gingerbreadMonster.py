from monster import Monster
import time
import math

class GingerbreadMonster(Monster):
	def objPath(self):
		return "data/model/gingerbreadMonster.obj"
	def intelligence(self):
		try:
			a = self.startRunning
		except:
			self.startRunning = time.time()
			self.stopRunning = 0
			self.running = False
			self.playerToFollow = None

		if time.time() - self.stopRunning > 5 and not self.running:
			self.running = True
			self.startRunning = time.time()
			self.data.velocity = (1.0, 0.0, 0.0)

		if time.time() - self.startRunning > 5 and self.running:
			self.running = False
			self.stopRunning = time.time()
			self.data.velocity = (0.0, 0.0, 0.0)

		distance = 1000000.0
		for i in self.objects:
			# Find the closest player
			if i.type == "Player":
				dx = self.position[0] - i.position[0]
				dy = self.position[1] - i.position[1]
				dz = self.position[2] - i.position[2]
				d = math.sqrt(dx*dx + dy*dy + dz*dz)

				if d < distance:
					self.playerToFollow = i
					distance = d

		#if self.playerToFollow != None:
		#	print "Following:", self.playerToFollow.data.name

		if self.playerToFollow == None:
			#print "No one to follow"
			#print self.objects
			self.data.velocity = (0.0, self.data.velocity[1], 0.0)
			return

		self.data.orientation = (
				self.data.orientation[0],
				(math.degrees(math.atan2(
					self.playerToFollow.data.position[0] \
							- self.data.position[0],
					self.playerToFollow.data.position[2] \
							- self.data.position[2])) \
						+ 90.0) % 360,
				self.data.orientation[2]
				)

		if distance > 5.5:
			self.data.velocity = (
					3*math.sin(math.radians(self.data.orientation[1] + 90.0)),
					self.data.velocity[1],
					3*math.cos(math.radians(self.data.orientation[1] + 90.0))
					)
		elif distance < 4.5:
			self.data.velocity = (
					-3*math.sin(math.radians(self.data.orientation[1] + 90.0)),
					self.data.velocity[1],
					-3*math.cos(math.radians(self.data.orientation[1] + 90.0))
					)
		else:
			self.data.velocity = (0.0, self.data.velocity[1], 0.0)
