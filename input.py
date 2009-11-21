import pygame
import math
import sys
import time
from Global import *

class input:
	def __init__(self):
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
					if Global.mainMenuRow > 0: Global.mainMenuRow -= 1
				elif event.key == pygame.K_DOWN:
					Global.mainMenuRow += 1
				elif event.key == pygame.K_RETURN:
					try:
						Global.menu.menuEntries[Global.mainMenuRow][1]()
					except:
						print "Error running function for menu entry"


	def handle_mouse(self):
		for event in pygame.event.get([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP]):
			if event.type == pygame.MOUSEMOTION:
				self.xrot += event.rel[1] / 10.0 # It is y pos with mouse that rotates the X axis
				self.yrot = (self.yrot + event.rel[0] / 10.0) % 360
				if self.xrot <= -90: self.xrot = -90
				if self.xrot >= 90: self.xrot = 90
				if not Global.spectator:
					Global.player.orientation = (
							Global.player.orientation[0],
							(Global.player.orientation[1] - event.rel[0]/10.0) % 360,
							Global.player.orientation[2]
							)

	def handle_input(self):
		clock = pygame.time.Clock()
		time_passed = clock.tick()
		time_passed_seconds = time_passed / 1000.0
		distance_moved = time_passed_seconds * self.speed

		while not Global.quit:
			if Global.mainMenuOpen:
				self.handleMainMenuInput()
				continue

			if self.up_pressed:
				xrotrad = self.xrot / 180 * math.pi
				yrotrad = self.yrot / 180 * math.pi
				if Global.spectator:
					self.xpos += math.sin(yrotrad) * distance_moved
					self.zpos -= math.cos(yrotrad) * distance_moved
					self.ypos -= math.sin(xrotrad) * distance_moved
				else:
					Global.player.position = (
							Global.player.position[0] + math.sin(yrotrad) * distance_moved,
							Global.player.position[1],
							Global.player.position[2] - math.cos(yrotrad) * distance_moved
							)

			if self.down_pressed:
				xrotrad = self.xrot / 180 * math.pi
				yrotrad = self.yrot / 180 * math.pi
				if Global.spectator:
					self.xpos -= math.sin(yrotrad) * distance_moved
					self.zpos += math.cos(yrotrad) * distance_moved
					self.ypos += math.sin(xrotrad) * distance_moved
				else:
					Global.player.position = (
							Global.player.position[0] - math.sin(yrotrad) * distance_moved, 
							Global.player.position[1], 
							Global.player.position[2] + math.cos(yrotrad) * distance_moved
							)

			if self.left_pressed:
				yrotrad = self.yrot / 180 * math.pi
				if Global.spectator:
					self.xpos -= math.cos(yrotrad) * distance_moved
					self.zpos -= math.sin(yrotrad) * distance_moved
				else:
					Global.player.position = (
							Global.player.position[0] - math.cos(yrotrad) * distance_moved,
							Global.player.position[1],
							Global.player.position[2] - math.sin(yrotrad) * distance_moved
							)

			if self.right_pressed:
				yrotrad = self.yrot / 180 * math.pi
				if Global.spectator:
					self.xpos += math.cos(yrotrad) * distance_moved
					self.zpos += math.sin(yrotrad) * distance_moved
				else:
					Global.player.position = (
							Global.player.position[0] + math.cos(yrotrad) * distance_moved,
							Global.player.position[1],
							Global.player.position[2] + math.sin(yrotrad) * distance_moved
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
							Global.debugLines ^= 1
							Global.g_bDebugLines ^= 1
						elif event.key == pygame.K_F3:
							Global.spectator ^= 1
						elif event.key == pygame.K_F6:
							Global.drawAxes ^= 1
						elif event.key == pygame.K_F7:
							Global.wireframe ^= 1
						elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
							Global.g_MaxSubdivisions += 1
							Global.reDraw = True
						elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
							if Global.g_MaxSubdivisions > 0:
								Global.g_MaxSubdivisions -= 1
								Global.reDraw = True
						elif event.key == pygame.K_j:
							self.speed += 100
						elif event.key == pygame.K_k:
							self.speed -= 100
						elif event.key == pygame.K_SPACE:
							Global.player.jump()

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
