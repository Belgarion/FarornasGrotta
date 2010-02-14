from monster import Monster
import time
import math

class GingerbreadMonster(Monster):
	def objPath(self):
		return "models/gingerbreadMonster.obj"
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
			self.velocity = (1.0, 0.0, 0.0)

		if time.time() - self.startRunning > 5 and self.running:
			self.running = False
			self.stopRunning = time.time()
			self.velocity = (0.0, 0.0, 0.0)

		distance = 1000000.0
		for i in self.objects:
			# Find the closest player
			if i.name[0:6] == "Player":
				dx = self.position[0] - i.position[0]
				dy = self.position[1] - i.position[1]
				dz = self.position[2] - i.position[2]
				d = math.sqrt(dx*dx + dy*dy + dz*dz)

				if d < distance:
					self.playerToFollow = i
					distance = d

		print "Following:", self.playerToFollow.name

		self.orientation = (
				self.orientation[0],
				(math.degrees(math.atan2(
					self.playerToFollow.position[0] - self.position[0],
					self.playerToFollow.position[2] - self.position[2])) \
						+ 90.0) % 360,
				self.orientation[2]
				)

		if distance > 2.02:
			self.velocity = (
					3*math.sin(math.radians(self.orientation[1] + 90.0)),
					self.velocity[1],
					3*math.cos(math.radians(self.orientation[1] + 90.0))
					)
		elif distance < 1.98:
			self.velocity = (
					-3*math.sin(math.radians(self.orientation[1] + 90.0)),
					self.velocity[1],
					-3*math.cos(math.radians(self.orientation[1] + 90.0))
					)
		else:
			self.velocity = (0.0, self.velocity[1], 0.0)
