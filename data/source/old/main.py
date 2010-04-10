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
from sound import *

from ProcessManager import *
from StateManager import *
from CallbackManager import *

from gameObject import *
from object import *

from OpenGL.GL import *
from OpenGL.GLU import *
import time
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
		self.sound = CSound(self, self.config.getint('Sound','Frequency'), True)

		self.player = Player(self,sound = self.sound)
		self.object_manager.objects.append(self.player.object)

		self.input_thread = InputThread(self.input)
		self.input_thread.start()

		self.networkThread = network.NetworkThread(self)

		self.process_manager = ProcessManager()
		self.state_manager = StateManager()
		self.callback_manager = CallbackManager()

		self.menu = Menu(self)
		self.state_manager.push(self.quit, None)
		self.state_manager.push(self.menu.menu_is_open, None)
		self.state_manager.process(None)

		self.physics.updateObjects(self.object_manager.objects)

		self.callback_manager.Add_Trigger("FUNCTION", [self.player.jump], permanent = True, triggers = {"Keys" : {"KEY_SPACE" : True}})
		self.callback_manager.Add_Trigger("FUNCTION", [self.player.walk, self, 0.0], permanent = True, triggers = {"Keys" : {"KEY_W" : False, "KEY_UP" : False}})
		self.callback_manager.Add_Trigger("FUNCTION", [self.player.walk, self, -90.0], permanent = True, triggers = {"Keys" : {"KEY_A" : False, "KEY_LEFT" : False}})
		self.callback_manager.Add_Trigger("FUNCTION", [self.player.walk, self, 180.0], permanent = True, triggers = {"Keys" : {"KEY_S" : False, "KEY_DOWN" : False}})
		self.callback_manager.Add_Trigger("FUNCTION", [self.player.walk, self, 90.0], permanent = True, triggers = {"Keys" : {"KEY_D" : False, "KEY_RIGHT" : False}})

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
			self.graphics.init_game()

			self.physics.lastTime = time.time()
			self.fpsTime = 0
			if self.args['host'] != None:
				try:
					self.networkThread.addr = \
							(self.args['host'], self.args['port'])
					network.Connect(self.args['host'], self.args['port'])
					self.networkThread.start()
				except:
					traceback.print_exc()


			pygame.mouse.set_visible(0)
			pygame.event.set_grab(0)
			self.clock = pygame.time.Clock()
		elif purpose is "FRAME_PURPOSE":
			rel = self.input.yrot - self.player.rotated
			self.player.rotated += rel
			if not self.graphics.spectator:
					self.player.object.orientation = (
							self.player.object.orientation[0],
							(self.player.object.orientation[1] \
									- rel) % 360,
							self.player.object.orientation[2]
							)
			
			if time.time() - self.fpsTime >= 1.0:
				self.fpsTime = time.time()
				self.graphics.printFPS()
			#print "game processing"
			self.physics.updateObjects(self.object_manager.objects)
			self.object_manager.objects = self.physics.update()
			objects = self.object_manager.objects
			
			
			for i in self.networkThread.objdataToAdd:
				if i.type == "Player":
					p = Player(self,"Player 2",
							i.position,
							i.orientation,
							i.mass, i.id)
					objects.append(p)
				elif i.type == "monster1":
					g = Object(
							i.type,
							i.name,
							i.position,
							i.orientation,
							i.scale,
							i.mass, 
							i.velocity,
							i.id)
					objects.append(g)
					self.physics.add_object(g)
				elif i.type == "Fireball":
					f = Fireball(i.name, i.position,
							i.orientation, i.mass,
							i.velocity, i.id, i.scale)
					objects.append(f)
				self.networkThread.objdataToAdd.remove(i)
			self.object_manager.objects = objects
			self.graphics.draw(self.object_manager.objects)
			
			time_passed = self.clock.tick()
			time_passed_seconds = time_passed / 1000.0

			distance_moved = time_passed_seconds * self.input.speed
			self.distance_moved = distance_moved

			# I pass the keys, it can figure out the time-triggers and position-triggers itself
			self.callback_manager.Check_Triggers(self.input.keys)

			
#			if self.input.resetKey("KEY_SPACE") == 1:
#				self.player.jump()

			if self.input.resetKey("KEY_F") == 1:
				f = Fireball("Fireball 1",
						(self.player.object.position[0],
							self.player.object.position[1],
							self.player.object.position[2] + 1.0),
						(0.0, 0.0, 0.0), 20, (10.0, 10.0, 0.0))
				objects.append(f)
				network.USend(self.networkThread.addr, 2,
						cPickle.dumps(f.data))

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

			self.physics.updateObjects(objects)
