import os, sys
import pygame
import threading
import StringIO
import ConfigParser

from network import *
from input import *
from physics import *
from graphics import *
from menu import *


from ProcessManager import *
from StateManager import *

from OpenGL.GL import *
from OpenGL.GLU import *

from tests import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (200,200) # Move window from so fps displayed on xmonad


def init_config():
	defaultConfig = StringIO.StringIO(\
				"[Resolution]\n"\
				"Width: 640\n"\
				"Height: 480\n"\
				"\n"\
				"[Input]\n"\
				"KeyboardLayout: qwerty\n"\
				)

	config = ConfigParser.SafeConfigParser()
	config.readfp(defaultConfig)
	config.read('config')
	return config

def init_pygame(main):
	pygame.init()
	pygame.display.set_mode(
			(main.config.getint('Resolution','Width'),
				main.config.getint('Resolution', 'Height')),
				pygame.DOUBLEBUF | pygame.OPENGL)

class Object:
	def __init__(self, type, name, position, orientation, mass, velocity):
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity

class CaveOfDanger:
	def __init__(self):
		self.running = 1
		self.config = init_config()

		init_pygame(self)
		init_opengl(self)

		#self.network = Network()
		self.physics = Physics(self)
		self.graphics = Graphics(self)
		self.input = Input(self)

		self.input_thread = InputThread(self.input)
		self.input_thread.start()

		self.process_manager = ProcessManager()
		self.state_manager = StateManager()

		menu = Menu(self)
		self.state_manager.push(self.quit, None)
		self.state_manager.push(menu.menu_is_open, None)
		self.state_manager.process(None)
	def run(self):
		while self.running:
			pygame.display.flip()
			self.state_manager.process(None)
			self.process_manager.process(None)
			pygame.time.wait(60)

		self.input.running = False
		#self.state_manager.push()
		#self.networkThread.start()
		#test_process()
		#test_states()

	def quit(self, caller, purpose):
		if purpose is "STOP_PURPOSE":
			print "quit stopping"
			self.running = 0
		elif purpose is "INIT_PURPOSE":
			pass
		elif purpose is "FRAME_PURPOSE":
			self.running = 0
		else:
			print "quit: no purpose"
