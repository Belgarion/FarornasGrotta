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
from player import Player
from octree import *


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

class Data:
	def __init__(self):
		self.list = {}
		self.load_level("level1")
	def add_data(self):
		pass
	def load_level(self, name):
		f = open("data/level/" + name + ".lvl")
		
		objects_on_level=[]
		spawns_on_level=[]

		for line in f:
			if not line: continue
			if line[0] is "#": continue
			split = line.split(" ")
			if split[0] == "object":
				objects_on_level.append(split[1].replace("\n",""))

class Object:
	def __init__(self, type, name, position, orientation, mass=1, velocity=(0,0,0)):
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation
		self.mass = mass
		self.velocity = velocity

class ObjectManager:
	def __init__(self):
		self.objects = []
		self.load_level("level1")
	def add_object(self, object, name, x, y, z, angle):
		object = Object(object, name, (x,y,z), angle)
		self.objects.append(object)
	def load_level(self,name):
		f = open("data/level/" + name + ".lvl")
		for line in f:
			if not line: continue
			if line[0] is "#": continue
			split = line.split(" ")
			if split[0] == "spawn":
				pos = split[3].split(",")
				self.add_object(split[1], split[2], pos[0], pos[1], pos[2], split[4])



class CaveOfDanger:
	def __init__(self):
		self.objects = []
		self.running = 1
		self.config = init_config()

		self.checkArgs()

		init_pygame(self)
		init_opengl(self)

		self.data = Data()
		self.object_manager = ObjectManager()
		#self.network = Network()
		self.physics = Physics(self)
		self.octree = COctree()
		self.graphics = Graphics(self)
		self.input = Input(self)
		self.player = Player()
		self.objects.append(self.player)

		self.input_thread = InputThread(self.input)
		self.input_thread.start()

		self.process_manager = ProcessManager()
		self.state_manager = StateManager()

		self.menu = Menu(self)
		self.state_manager.push(self.quit, None)
		self.state_manager.push(self.menu.menu_is_open, None)
		self.state_manager.process(None)

		self.physics.updateObjects(self.objects)

	def checkArgs(self):
		self.args = {'disableWater': False,
				'host': None,
				'port': 30000}
		if len(sys.argv) > 1:
			for index, arg in enumerate(sys.argv):
				if arg == "--help" or arg == "-h":
					print "Arguments: \n"\
							"	--nowater		Disable water\n"\
							"	--host			Connect to host\n"\
							"	--port			Port (Default: 30000)\n"
					sys.exit(0)
				elif arg == "--nowater":
					self.args['disableWater'] = True
				elif arg == "--host":
					if not len(sys.argv) > index + 1:
						print "No host specified for --host"
						continue
					self.args['host'] = sys.argv[index + 1]
				elif arg == "--port":
					if not len(sys.argv) > index + 1:
						print "No port specified for --port"
						continue
					self.args['port'] = int(sys.argv[index + 1])

	def run(self):
		while self.running:
			self.state_manager.process(None)
			self.process_manager.process(None)
			#pygame.time.wait(60)
	
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

	def runGame(self, caller, purpose):
		if purpose is "STOP_PURPOSE":
			print "game stopping"
		elif purpose is "INIT_PURPOSE":
			print "game starting"
			self.graphics.initGL()
			self.physics.lastTime = time.time()
		elif purpose is "FRAME_PURPOSE":
			print "game processing"

			objects = self.physics.update()
			self.graphics.draw(objects)

			if self.input.keys["KEY_ESCAPE"] == 1:
				self.state_manager.push(self.menu.menu_is_open, None)
				self.input.keys["KEY_ESCAPE"] = 0
