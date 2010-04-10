# -*- coding: utf-8 -*-
import time
import sys
import os
import math
from octree_new import *

#TODO: Use acceleration to change velocity
class Physics:
	def __init__(self, main):
		self.objects_in_players_node = []
		self.oldPos = {}
		self.octree = Octree(15000.0000)
		self.main = main
		self.objects = []
		self.lastTime = time.time()
		self.isClient = True
	def add_object(self, object):
		self.octree.insertNode(self.octree.root, 15000.000, self.octree.root, object)
		self.oldPos[object.id] = object.position	
	
	def updateObjects(self, objects):
		self.objects = objects
	def update(self):
		self.time = time.time()
		relTime = self.lastTime-self.time
	 	for object in self.objects:
			if self.isClient:
				#if self.object.id == self.main.player.data.id:

				object = self.updatePos(object, relTime)
			else:
				if object.type != "Player":
					object = self.updatePos(object, relTime)
		self.lastTime = time.time()
				return self.objects
	def updatePos(self, obj, relTime):
		velocity = obj.velocity
		mass = obj.mass

		y = obj.position[1]
		velY = obj.velocity[1]

		if obj.position[1] <= 0:
                        obj.position = (obj.position[0], 0, obj.position[2])
	
			velY = 0
		else:	
			velY += -9.82*relTime
			y += velY*relTime

		obj.velocity = (velocity[0], velY , velocity[2])
		obj.position = (obj.position[0]+obj.velocity[0]*relTime,
				y,
				obj.position[2] + obj.velocity[2]*relTime)

		return obj
	

	
