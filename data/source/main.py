import os, sys
import pygame
import threading
import StringIO
import ConfigParser

import network
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

from gingerbreadMonster import GingerbreadMonster

# Move window from so fps displayed on xmonad
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (200,200)


def init_config():
	defaultConfig = StringIO.StringIO(\
				"[Resolution]\n"\
				"Width: 640\n"\
				"Height: 480\n"\
				"\n"\
				"[Input]\n"\
				"KeyboardLayout: qwerty_swe\n"\
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

		for line in f:
			if not line: continue
			if line[0] is "#": continue
			split = line.split(" ")
			if split[0] == "object":
				objects_on_level.append(split[1].replace("\n",""))

class Object:
	def __init__(self, type, name, position, orientation, mass=1, \
			velocity=(0,0,0)):
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
				self.add_object(split[1], split[2], pos[0], pos[1], pos[2], \
						split[4])



class CaveOfDanger:
	def __init__(self):
		self.objects = []
		self.running = 1

		self.checkArgs()

		self.config = init_config()

		init_pygame(self)
		init_opengl(self)

		self.data = Data()
		self.object_manager = ObjectManager()
		self.physics = Physics(self)
		self.octree = COctree()
		self.graphics = Graphics(self)
		self.input = Input(self)
		self.player = Player()
		self.objects.append(self.player)

		self.input_thread = InputThread(self.input)
		self.input_thread.start()

		self.networkThread = network.NetworkThread(self)

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
		self.networkThread.running = False
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
			self.graphics.addSurface(0, "data/model/terrain.obj", \
				"data/image/grass.jpg")

			if self.args['host'] != None:
				try:
					self.networkThread.addr = \
							(self.args['host'], self.args['port'])
					network.Connect(self.args['host'], self.args['port'])
					self.networkThread.start()
				except:
					traceback.print_exc()

			self.physics.lastTime = time.time()

			pygame.mouse.set_visible(0)
			pygame.event.set_grab(1)

			self.clock = pygame.time.Clock()
		elif purpose is "FRAME_PURPOSE":
			#print "game processing"

			objects = self.physics.update()
			for i in self.networkThread.objdataToAdd:
				if i.type == "Player":
					print "Append a player!"
					p = Player("Player 2",
							i.position,
							i.orientation,
							i.mass, i.id)
					objects.append(p)
				elif i.type == "GingerbreadMonster":
					print "Append a monster!"
					g = GingerbreadMonster(
							"GingerbreadMonster",
							"Gingerbread 1",
							i.position,
							i.orientation,
							i.mass, objects, False, i.id)
					objects.append(g)
				self.networkThread.objdataToAdd.remove(i)
			self.physics.updateObjects(objects)
			self.graphics.draw(objects)

			time_passed = self.clock.tick()
			time_passed_seconds = time_passed / 1000.0

			distance_moved = time_passed_seconds * self.input.speed

			if self.input.keys["KEY_UP"] == 1 or self.input.keys["KEY_W"] == 1:
				xrotrad = self.input.xrot / 180 * math.pi
				yrotrad = self.input.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.input.xpos += math.sin(yrotrad) * distance_moved
					self.input.zpos -= math.cos(yrotrad) * distance_moved
					self.input.ypos -= math.sin(xrotrad) * distance_moved
				else:
					self.player.data.position = (
							self.player.data.position[0] \
									+ math.sin(yrotrad) * distance_moved,
							self.player.data.position[1],
							self.player.data.position[2] \
									- math.cos(yrotrad) * distance_moved
							)
			elif self.input.keys["KEY_DOWN"] == 1 or \
					self.input.keys["KEY_S"] == 1:
				xrotrad = self.input.xrot / 180 * math.pi
				yrotrad = self.input.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.input.xpos -= math.sin(yrotrad) * distance_moved
					self.input.zpos += math.cos(yrotrad) * distance_moved
					self.input.ypos += math.sin(xrotrad) * distance_moved
				else:
					self.player.data.position = (
							self.player.data.position[0] \
									- math.sin(yrotrad) * distance_moved,
							self.player.data.position[1],
							self.player.data.position[2] \
									+ math.cos(yrotrad) * distance_moved
							)

			if self.input.keys["KEY_LEFT"] == 1 or \
					self.input.keys["KEY_A"] == 1:
				yrotrad = self.input.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.input.xpos -= math.cos(yrotrad) * distance_moved
					self.input.zpos -= math.sin(yrotrad) * distance_moved
				else:
					self.player.data.position = (
							self.player.data.position[0] \
									- math.cos(yrotrad) * distance_moved,
							self.player.data.position[1],
							self.player.data.position[2] \
									- math.sin(yrotrad) * distance_moved
							)
			elif self.input.keys["KEY_RIGHT"] == 1 or \
					self.input.keys["KEY_D"] == 1:
				yrotrad = self.input.yrot / 180 * math.pi
				if self.graphics.spectator:
					self.input.xpos += math.cos(yrotrad) * distance_moved
					self.input.zpos += math.sin(yrotrad) * distance_moved
				else:
					self.player.data.position = (
							self.player.data.position[0] \
									+ math.cos(yrotrad) * distance_moved,
							self.player.data.position[1],
							self.player.data.position[2] \
									+ math.sin(yrotrad) * distance_moved
							)

			if self.input.resetKey("KEY_SPACE") == 1:
				self.player.jump()

			if self.input.resetKey("KEY_ESCAPE") == 1:
				self.state_manager.push(self.menu.menu_is_open, None)

			if self.input.resetKey("KEY_U") == 1:
				pygame.event.set_grab(0)
				pygame.mouse.set_visible(1)
			elif self.input.resetKey("KEY_G") == 1:
				pygame.event.set_grab(1)
				pygame.mouse.set_visible(0)

			if self.input.resetKey("KEY_F3") == 1:
				self.graphics.spectator ^= 1

			if self.input.resetKey("KEY_F6") == 1:
				self.graphics.toggleDrawAxes ^= 1

			if self.input.resetKey("KEY_F7") == 1:
				self.graphics.wireframe ^= 1

			if self.input.resetKey("KEY_J") == 1:
				self.input.speed += 100

			if self.input.resetKey("KEY_K") == 1:
				self.input.speed -= 100

