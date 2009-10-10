import pygame
import math
import sys

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
		self.keyboardlayout = 1
		
		self.speed = 2

	def handle_input(self):
		while not quit:
			if self.up_pressed:
				xrotrad = self.xrot/180*math.pi
				yrotrad = self.yrot/180*math.pi
				self.xpos += math.sin(yrotrad)*self.speed
				self.zpos -= math.cos(yrotrad)*self.speed
				self.ypos -= math.sin(xrotrad)*self.speed

			if self.down_pressed:

				xrotrad = self.xrot / 180 * math.pi
				yrotrad = self.yrot / 180 * math.pi
				self.xpos -= math.sin(yrotrad)*self.speed
				self.zpos += math.cos(yrotrad)*self.speed
				self.ypos += math.sin(xrotrad)*self.speed

			if self.left_pressed:
				yrotrad = self.yrot / 180 * math.pi
				self.xpos -= math.cos(yrotrad)*self.speed
				self.zpos -= math.sin(yrotrad)*self.speed
				
			if self.right_pressed:
				yrotrad = self.yrot/180*math.pi
				self.xpos += math.cos(yrotrad)*self.speed
				self.zpos += math.sin(yrotrad)*self.speed
				


			rel = pygame.mouse.get_rel()
			self.xrot += rel[1]/10.0 # It is y pos with mouse that rotates the X axis					   
			self.yrot += rel[0]/10.0
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit(1)
				if event.type == pygame.KEYDOWN:
					print "Button pressed: ", event.key
					if event.key == pygame.K_ESCAPE:
						sys.exit(1)

					if self.keyboardlayout:
						if int(event.key) == 228:
							self.up_pressed = 1
						if int(event.key) == 111:
							self.down_pressed = 1
						if int(event.key) == 97:
							self.left_pressed = 1
						if int(event.key) == 101:
							self.right_pressed = 1
					else:
						if int(event.key) == pygame.K_w:
							self.up_pressed = 1
						if int(event.key) == pygame.K_s:
							self.down_pressed = 1
						if int(event.key) == pygame.K_a:
							self.left_pressed = 1
						if int(event.key) == pygame.K_d:
							self.right_pressed = 1

					if event.key == pygame.K_F1:
						self.keyboardlayout ^= 1
				
				if event.type == pygame.KEYUP:
					if self.keyboardlayout:
						if int(event.key) == 228:
							self.up_pressed = 0
						if int(event.key) == 111:
							self.down_pressed = 0
						if int(event.key) == 97:
							self.left_pressed = 0
						if int(event.key) == 101:
							self.right_pressed = 0
					else:
						if int(event.key) == pygame.K_w:
							self.up_pressed = 0
						if int(event.key) == pygame.K_s:
							self.down_pressed = 0
						if int(event.key) == pygame.K_a:
							self.left_pressed = 0
						if int(event.key) == pygame.K_d:
							self.right_pressed = 0
			time.sleep(0.001)
