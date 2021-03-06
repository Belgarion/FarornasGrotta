# -*- coding: utf-8 -*-
import pygame, math, sys, time, threading, traceback

class Input():
	def __init__(self, main):
		self.main = main
		self.graphics = main.graphics

		self.keymap = self.load_keymap()

		self.keys = {}
		self.init_keys()

		self.xpos = 0
		self.zpos = 0
		self.ypos = 0

		self.xrot = 0
		self.yrot = 0

		self.speed = 15
		self.running = True

	def translate(self, key):
		return self.dict[key]

	def load_keymap(self):
		layout = self.main.config.get("Input", "KeyboardLayout")

		self.dict = {}

		try:
			f = open("data/keyboard/" + layout)
			while 1:
				line = f.readline()
				if not line: break
				list = line.split(" ")
				foo = list[0]
				bar = list[1].replace("\n", "")
				self.dict[foo] = bar # reversing for faster lookup
			f.close
		except:
			traceback.print_exc()

	def handle_mouse(self):
		for event in pygame.event.get(\
				[pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP]
				):
			if event.type == pygame.MOUSEMOTION:
				# It is y pos with mouse that rotates the X axis
				self.xrot += event.rel[1] / 10.0
				self.yrot = (self.yrot + event.rel[0] / 10.0) % 360
				if self.xrot <= -90: self.xrot = -90
				if self.xrot >= 90: self.xrot = 90
				continue
				if not self.graphics.spectator:
					self.player.data.orientation = (
							self.player.data.orientation[0],
							(self.player.data.orientation[1] \
									- event.rel[0]/10.0) % 360,
							self.player.data.orientation[2]
							)

	def handle_input(self):
		clock = pygame.time.Clock()
		time_passed = clock.tick()
		time_passed_seconds = time_passed / 1000.0
		distance_moved = time_passed_seconds * self.speed

		while self.running:
			#if self.main.mainMenuOpen:
			#	self.menu.current.KeyHandler()
			#	continue

			if sys.platform != "win32":
				self.handle_mouse()
			# 1 = pressed down, 0 = unpressed and handled, -1 = pressed down and up but not handled
			for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
				if event.type == pygame.QUIT:
					self.main.running = 0
				elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
					#print "Button pressed: ", event.key
					#if event.key == pygame.K_ESCAPE:
					#	self.keys["KEY_ESCAPE"] = 1
					name_of_key = pygame.key.name(event.key)
					if name_of_key == "world 69":
						name_of_key = "å"
					elif name_of_key == "world 68":
						name_of_key = "ä"
					elif name_of_key == "world 86":
						name_of_key = "ö"

					for key in self.keys:
						try: # translate key if key is a-z (possibly affected by layout)
							translated = self.translate(key)
						except KeyError:
							translated = key
							translated = translated.replace("KEY_", "") #ex: KEY_A->A
							translated = translated.lower() # A->a
						if name_of_key == translated:
							if event.type == pygame.KEYDOWN:
								self.keys[key] = 1
							else:
								self.keys[key] = -1
							break

			time_passed = clock.tick()
			time_passed_seconds = time_passed / 1000.0

			distance_moved = time_passed_seconds * self.speed

			time.sleep(0.001)

	def init_keys(self):
		self.keys = {
			"KEY_A":0,
			"KEY_B":0,
			"KEY_C":0,
			"KEY_D":0,
			"KEY_E":0,
			"KEY_F":0,
			"KEY_G":0,
			"KEY_H":0,
			"KEY_I":0,
			"KEY_J":0,
			"KEY_K":0,
			"KEY_L":0,
			"KEY_M":0,
			"KEY_N":0,
			"KEY_O":0,
			"KEY_P":0,
			"KEY_Q":0,
			"KEY_R":0,
			"KEY_S":0,
			"KEY_T":0,
			"KEY_U":0,
			"KEY_V":0,
			"KEY_W":0,
			"KEY_X":0,
			"KEY_Y":0,
			"KEY_Z":0,
			"KEY_1":0,
			"KEY_2":0,
			"KEY_3":0,
			"KEY_4":0,
			"KEY_5":0,
			"KEY_6":0,
			"KEY_7":0,
			"KEY_8":0,
			"KEY_9":0,
			"KEY_0":0,
			"KEY_F1":0,
			"KEY_F2":0,
			"KEY_F3":0,
			"KEY_F4":0,
			"KEY_F5":0,
			"KEY_F6":0,
			"KEY_F7":0,
			"KEY_F8":0,
			"KEY_F9":0,
			"KEY_F10":0,
			"KEY_F11":0,
			"KEY_F12":0,
			"KEY_SPACE":0,
			"KEY_RETURN":0,
			"KEY_ESCAPE":0,
			"KEY_UP":0,
			"KEY_DOWN":0,
			"KEY_LEFT":0,
			"KEY_RIGHT":0,
			"KEY_+":0,
			"KEY_-":0,
			"KEY_KP_PLUS":0,
			"KEY_KP_MINUS":0,
			"KEY_TAB":0,
			}

	def resetKey(self, key):
		oldval = self.keys[key]
		self.keys[key] = 0
		return oldval

class InputThread(threading.Thread):
	def __init__(self, input):
                self.input = input
                threading.Thread.__init__(self)
        def run(self):
                self.input.handle_input()
