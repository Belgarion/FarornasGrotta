import pygame
import math
import sys
import time
from octree import *
from Global import *

class input():
	def __init__(self, octree, graphics, menu, player, main):
		self.player = player
		self.octree = octree
		self.main = main
		self.graphics = graphics
		self.menu = menu

		self.down_pressed = 0
		self.up_pressed = 0
		self.left_pressed = 0
		self.right_pressed = 0

		self.xpos = 0
		self.zpos = 0
		self.ypos = 0

		self.xrot = 0
		self.yrot = 0

		# Qwerty = 0, Dvorak = 1
		self.keyboardlayout = 0

		self.speed = 15	

	def handleMainMenuInput(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					Global.quit = 1
				elif event.key == pygame.K_UP:
					if self.menu.mainMenuRow > 0: self.menu.mainMenuRow -= 1
				elif event.key == pygame.K_DOWN:
					self.menu.mainMenuRow += 1
				elif event.key == pygame.K_RETURN:
					try:
						self.menu.menuEntries[self.menu.mainMenuRow][1]()
					except:
						print "Error running function for menu entry"
						print sys.exc_info()

	def handle_mouse(self):
		for event in pygame.event.get([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP]):
			if event.type == pygame.MOUSEMOTION:
				self.xrot += event.rel[1] / 10.0 # It is y pos with mouse that rotates the X axis
				self.yrot = (self.yrot + event.rel[0] / 10.0) % 360
				if self.xrot <= -90: self.xrot = -90
				if self.xrot >= 90: self.xrot = 90
				if not self.graphics.spectator:
					self.player.orientation = (
							self.player.orientation[0],
							(self.player.orientation[1] - event.rel[0]/10.0) % 360,
							self.player.orientation[2]
							)

	def handle_input(self):
		clock = pygame.time.Clock()
		time_passed = clock.tick()
		time_passed_seconds = time_passed / 1000.0
		distance_moved = time_passed_seconds * self.speed

		while not Global.quit:
			if self.main.mainMenuOpen:
				self.handleMainMenuInput()
				continue

			if self.up_pressed:
				xrotrad = self.xrot / 180 * math.pi
				yrotrad = self.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.xpos += math.sin(yrotrad) * distance_moved
					self.zpos -= math.cos(yrotrad) * distance_moved
					self.ypos -= math.sin(xrotrad) * distance_moved
				else:
					self.player.position = (
							self.player.position[0] + math.sin(yrotrad) * distance_moved,
							self.player.position[1],
							self.player.position[2] - math.cos(yrotrad) * distance_moved
							)

			if self.down_pressed:
				xrotrad = self.xrot / 180 * math.pi
				yrotrad = self.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.xpos -= math.sin(yrotrad) * distance_moved
					self.zpos += math.cos(yrotrad) * distance_moved
					self.ypos += math.sin(xrotrad) * distance_moved
				else:
					self.player.position = (
							self.player.position[0] - math.sin(yrotrad) * distance_moved, 
							self.player.position[1], 
							self.player.position[2] + math.cos(yrotrad) * distance_moved
							)

			if self.left_pressed:
				yrotrad = self.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.xpos -= math.cos(yrotrad) * distance_moved
					self.zpos -= math.sin(yrotrad) * distance_moved
				else:
					self.player.position = (
							self.player.position[0] - math.cos(yrotrad) * distance_moved,
							self.player.position[1],
							self.player.position[2] - math.sin(yrotrad) * distance_moved
							)

			if self.right_pressed:
				yrotrad = self.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.xpos += math.cos(yrotrad) * distance_moved
					self.zpos += math.sin(yrotrad) * distance_moved
				else:
					self.player.position = (
							self.player.position[0] + math.cos(yrotrad) * distance_moved,
							self.player.position[1],
							self.player.position[2] + math.sin(yrotrad) * distance_moved
							)
			
			if sys.platform != "win32":
				self.handle_mouse()

			for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
				if event.type == pygame.QUIT:
					Global.quit = 1
				elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
					#print "Button pressed: ", event.key
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_ESCAPE:
							Global.quit = 1
						elif event.key == pygame.K_F1:
							self.keyboardlayout ^= 1
						elif event.key == pygame.K_F2:
							self.octree.debugLines ^= 1
						elif event.key == pygame.K_F3:
							self.graphics.spectator ^= 1
						elif event.key == pygame.K_F6:
							self.graphics.toggleDrawAxes ^= 1
						elif event.key == pygame.K_F7:
							self.graphics.wireframe ^= 1
						elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
							#self.octree.g_MaxSubdivisions += 1
							COctree.g_MaxSubdivisions += 1
							self.graphics.reDraw = True
						elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
							if self.octree.g_MaxSubdivisions > 0:
								COctree.g_MaxSubdivisions -= 1
								self.main.graphics.reDraw = True
						elif event.key == pygame.K_j:
							self.speed += 100
						elif event.key == pygame.K_k:
							self.speed -= 100
						elif event.key == pygame.K_SPACE:
							self.player.jump()

					if event.key == pygame.K_UP:
						self.up_pressed ^= 1
					elif event.key == pygame.K_DOWN:
						self.down_pressed ^= 1
					elif event.key == pygame.K_LEFT:
						self.left_pressed ^= 1
					elif event.key == pygame.K_RIGHT:
						self.right_pressed ^= 1

					if self.keyboardlayout:
						if int(event.key) == 228:
							self.up_pressed ^= 1
						elif int(event.key) == 111:
							self.down_pressed ^= 1
						elif int(event.key) == 97:
							self.left_pressed ^= 1
						elif int(event.key) == 101:
							self.right_pressed ^= 1
					else:
						if event.key == pygame.K_w:
							self.up_pressed ^= 1
						elif event.key == pygame.K_s:
							self.down_pressed ^= 1
						elif event.key == pygame.K_a:
							self.left_pressed ^= 1
						elif event.key == pygame.K_d:
							self.right_pressed ^= 1

			time_passed = clock.tick()
			time_passed_seconds = time_passed / 1000.0

			distance_moved = time_passed_seconds * self.speed

			time.sleep(0.001)
