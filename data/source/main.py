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
from fireball import Fireball
from octree import *

from ProcessManager import *
from StateManager import *
from TriggerManager import *

from OpenGL.GL import *
from OpenGL.GLU import *

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
				"\n"\
				"[Sound]\n"\
				"Frequency: 22050\n"
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


class CaveOfDanger:
	def __init__(self):
		self.objects = []
		self.running = 1

		self.checkArgs()

		self.config = init_config()

		init_pygame(self)
		init_opengl(self)

		if self.args['disableSound'] or sys.platform == "win32":
			self.sound = None
		else:
			from sound import *
			self.sound = CSound(self, self.config.getint('Sound','Frequency'), True)

		self.player = Player(sound = self.sound)


		self.physics = Physics(self)
		self.octree = self.physics.octree
		self.graphics = Graphics(self)
		self.input = Input(self)

		self.objects.append(self.player)

		self.input_thread = InputThread(self.input)
		self.input_thread.start()

		self.networkThread = network.NetworkThread(self)

		self.process_manager = ProcessManager()
		self.state_manager = StateManager()
		self.trigger_manager = TriggerManager(self)

		self.menu = Menu(self)
		self.state_manager.push(self.quit, None)
		self.state_manager.push(self.menu.menu_is_open, None)
		self.state_manager.process(None)

		self.physics.updateObjects(self.objects)

		self.fpsTime = time.time()

		# TODO: Don't ask me, iam an alien
		self.trigger_manager.Ugly_Function_For_Loading_Main_Keytriggers()

	def checkArgs(self):
		self.args = {'disableWater': False,
				'host': None,
				'port': 30000}
		if len(sys.argv) > 1:
			for index, arg in enumerate(sys.argv):
				if arg == "--help" or arg == "-h":
					print "Arguments: \n"\
							"	--nowater		Disable water\n"\
							"	--nosound		Disable sound\n"\
							"	--host			Connect to host\n"\
							"	--port			Port (Default: 30000)\n"
					sys.exit(0)
				elif arg == "--nowater":
					self.args['disableWater'] = True
				elif arg == "--nosound":
					self.args['disableSound'] = True
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

		del self.sound
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

			terrain = "data/model/terrain.obj"

			self.graphics.addSurface(0, terrain, "data/image/grass.jpg")

			"""
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player().data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-10.0, 20.0, -20.0)).data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-15.0, 20.0, -20.0)).data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-20.0, 20.0, -20.0)).data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-30.0, 20.0, -20.0)).data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-35.0, 20.0, -20.0)).data)
			self.octree.insertNode(self.octree.root, 100.0, self.octree.root, Player(position = (-40.0, 20.0, -20.0)).data)
			"""

			self.graphics.loadStaticObject(0.0, 0.0, 0.0, "data/model/cave.obj", \
				"data/image/img2.png")

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
			pygame.event.set_grab(0)

			self.clock = pygame.time.Clock()

		elif purpose is "FRAME_PURPOSE":
			if sys.platform == "win32":
				self.input.handle_mouse()

			objects = self.physics.update()

			rel = self.input.yrot - self.player.rotated
			self.player.rotated += rel
			if not self.graphics.spectator:
					self.player.data.orientation = (
							self.player.data.orientation[0],
							(self.player.data.orientation[1] \
									- rel) % 360,
							self.player.data.orientation[2]
							)


			self.networkThread.addNewObjects()
			if time.time() - self.fpsTime >= 1.0:
				self.fpsTime = time.time()
				self.graphics.printFPS()


			#self.physics.octree.checkCollision(self.octree.root, self.player.data.position)
			#self.physics.handleCollision()

			self.physics.updateObjects(objects)
			#self.sound.Update_Sound(objects)
			self.graphics.draw(objects)


			time_passed = self.clock.tick()
			time_passed_seconds = time_passed / 1000.0

			distance_moved = time_passed_seconds * self.input.speed
			self.distance_moved = distance_moved

			# I pass the keys, it can figure out the time-triggers and position-triggers itself
			self.trigger_manager.Check_Triggers(self.input.keys)
