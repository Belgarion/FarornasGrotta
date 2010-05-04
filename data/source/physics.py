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
		self.objectsToRemove = []
		self.lastTime = time.time()
		self.isClient = True
		if os.path.basename(sys.argv[0]) == "server.py":
			self.isClient = False
		if self.isClient:
			self.oldPos[main.player.data.id] = self.main.player.data.position

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
				if self.objects[i].data.type != "player1":
					obj = self.updatePos(self.objects[i], relTime)
					if obj == None:
						self.objectsToRemove.append(self.objects[i])
					else:
						self.objects[i] = obj

		for obj in self.objectsToRemove:
			if obj in self.objects:
				self.objects.remove(obj)
				if obj.data.type == "Fireball":
					self.objectsToRemove.remove(obj)

		self.lastTime = time.time()


		if self.isClient:
			#update player position in the octree
			pos = self.main.player.data.position
			self.octree.deletePosition(
					self.octree.root,
					self.oldPos[self.main.player.data.id],
					self.main.player.data
					)
			self.octree.insertNode(self.octree.root,15000.0, self.octree.root, \
					self.main.player.data)
			self.oldPos[self.main.player.data.id] = pos

			result = self.octree.findPosition(self.octree.root, pos)
			self.objects_in_players_node = result
			if result != None:
				self.objects_in_players_node = result


		return self.objects

	def updatePos(self, obj, relTime):
		if self.isClient and obj != self.main.player:
			return

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

		if self.isClient:
			if self.playerCollision(new_pos):
				collide = 1


		if not collide:# or velY < 0:
			obj.data.position = new_pos
		elif self.isClient:
			# check if we are standin on something
			pos_y_down = new_pos[0], y, new_pos[2]
			if y <= 0 or self.playerCollision(pos_y_down):
				self.main.player.can_jump = 1
				self.main.player.data.velocity = (
						self.main.player.data.velocity[0],
						0,
						self.main.player.data.velocity[2]
						)

		if not self.isClient:
			if obj.data.type == "Fireball":
				monster = self.fireballCollision(obj, new_pos)
				if new_pos[1] <= 0 or monster != None:
					if monster != None:
						monster.data.hp -= 50
						if monster.data.hp <= 0 and obj.data.owner != None:
							for i in self.objects:
								if i.data.id == obj.data.owner:
									i.data.frags += 1
									break
					return None
			elif self.collisionBetweenObjectsWithoutOctree(obj, new_pos):
				obj.data.velocity = (0.0, 0.0, 0.0)
			elif y <= 0:
				obj.data.velocity = \
						obj.data.velocity[0], 0.0, obj.data.velocity[2]
				obj.data.position = new_pos[0], 0.0, new_pos[2]
			else:
				obj.data.position = new_pos

		return obj

	def collisionBetweenObjectsWithoutOctree(self, obj1, pos1):
		for obj2 in self.objects:
			if obj2 == obj1:
				continue
			dist = self.dist_between_points(pos1, obj2.data.position)
			if dist < 5:
				return True
		return False

	def fireballCollision(self, obj, pos):
		for obj2 in self.objects:
			if obj2.data.type != "GingerbreadMonster":
				continue
			dist = self.dist_between_points(pos, obj2.data.position)
			if dist < 5:
				return obj2
		return None

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
