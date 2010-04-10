from octree import *
import time
import sys
import os
import math

#TODO: Use acceleration to change velocity
class Physics:
	def __init__(self, main):
		self.objects_in_players_node = []
		self.oldPos = {}
		self.main = main
		self.octree = self.octree = Octree(100.0, self)	
		self.objects = []
		self.lastTime = time.time()
		self.isClient = True
		if os.path.basename(sys.argv[0]) != "server.py":
			self.oldPos[self.main.player.data.id] = self.main.player.data.position

	def updateObjects(self, objects):
		self.objects = objects

	def update(self):
		self.time = time.time()
		relTime = self.lastTime-self.time

	 	for i in xrange(len(self.objects)):
			if self.isClient:
				if self.objects[i].data.id == self.main.player.data.id:
					self.objects[i] = self.updatePos(self.objects[i], relTime)
					break
			else:
				if self.objects[i].data.type != "Player":
					self.objects[i] = self.updatePos(self.objects[i], relTime)

		self.lastTime = time.time()
		

		if os.path.basename(sys.argv[0]) != "server.py":
			
			#update player position in the octree
			pos = self.main.player.data.position
			self.octree.deletePosition(
					self.octree.root,
					self.oldPos[self.main.player.data.id],
					self.main.player.data
					)
			self.octree.insertNode(self.octree.root, 15000, self.octree.root, self.main.player.data)
			self.oldPos[self.main.player.data.id] = pos

			result = self.octree.findPosition(self.octree.root, pos)
			self.objects_in_players_node = result
			if result != None:
				self.objects_in_players_node = result


		return self.objects

	def updatePos(self, obj, relTime):
		velocity = obj.data.velocity
		mass = obj.data.mass

		y = obj.data.position[1]
		velY = obj.data.velocity[1]
		collide = 0
		
		velY += -9.82*relTime
		y += velY*relTime
		obj.data.velocity = (velocity[0], velY , velocity[2])
		new_pos = (obj.data.position[0]+obj.data.velocity[0]*relTime,
				y,
				obj.data.position[2] + obj.data.velocity[2]*relTime)

		if new_pos[1] < 0:
			collide = 1
		if os.path.basename(sys.argv[0]) != "server.py":
			if self.playerCollision(new_pos):
				collide = 1
		if not collide:# or velY < 0:
			obj.data.position = new_pos		
		elif os.path.basename(sys.argv[0]) != "server.py":
			# check if we are standin on something
			pos_y_down = obj.data.position[0], y, obj.data.position[2]
			if self.playerCollision(pos_y_down) or (y<=0):
				self.main.player.can_jump = 1
				self.main.player.data.velocity = self.main.player.data.velocity[0], 0 , self.main.player.data.velocity[2]
		

		# actually put att zero to not crap with the check for can jump
		if new_pos[1] < 0:
			obj.data.velocity = obj.data.velocity[0], 0, obj.data.velocity[2]


		return obj

	def playerCollision(self,newPos):
		return self.collisionPlayerMonster(newPos)

	def collisionPlayerMonster(self, playerpos):
		for obj in self.objects_in_players_node:
			if not obj.id == self.main.player.data.id:
				dist = self.dist_between_points(
					(playerpos[0], playerpos[1], playerpos[2]) ,
					(obj.position[0], obj.position[1],obj.position[2]) )
				if dist < 5:
					return True
		return False

	def dist_between_points(self,point1, point2):
		# sqrt( (x1-x2)^2 + (y1-y2)^2 )
		return math.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2 + (point1[2]-point2[2])**2)
