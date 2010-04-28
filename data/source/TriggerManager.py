import pygame, time

from gameObject import GameObject

class Dummy:
	pass

# FROM input.py
# 1		= pressed down
# 0		= unpressed and handled
# -1	= pressed down and up but not handled
class TriggerManager:
	def __init__(self, main):
		self.timer_triggers = []
		self.key_triggers = []
		self.position_triggers = []
		self.lastFireball = time.time()

		self.main = main

	def Add_Trigger(self, \
				triggers = {
					'Seconds' : None,
					'Keys' : {},
					'Area' : {'Position' : None, 'Radie' :  None}
				},
				conditions = {
					'Wait' : None,
					'Something' : None
				},
				trigger_settings = [],
				callback_settings = [],
				permanent = True
			):


		trigger = Dummy()

		trigger.triggers = triggers
		trigger.permanent = permanent

		trigger.settings = trigger_settings
		trigger.callbacks = callback_settings

		if "Seconds" in triggers:
			now = time.time()

			trigger.triggers['Start_Time'] = now
			trigger.triggers['Stop_Time'] = now + triggers['Seconds']
			self.timer_triggers.append(trigger)

		if "Keys" in triggers:
			self.key_triggers.append(trigger)

		if "Area" in triggers \
				and triggers['Area']['Position'] \
				and triggers['Area']['Radie']:
			self.position_triggers.append(trigger)

	def Find_Trigger(self):
		pass

	def Execute_Trigger(self, trigger):
		for setting in trigger.settings:
			if setting[0] == "FUNCTION":
				setting[1](*setting[2:])

			elif setting[0] == "EXECUTE":
				exec("%s" % (setting[1]))

			elif setting[0] == "NETWORK":
				pass

			elif setting[0] == "CALLBACK":
				pass

			else:
				print "This trigger doesn't got any template"

	def Execute_Callback(self, trigger):
		for setting in trigger.callbacks:
			if setting[0] == "FUNCTION":
				setting[1](*setting[2:])

			elif setting[0] == "EXECUTE":
				exec("%s" % (setting[1]))

			elif setting[0] == "NETWORK":
				pass

			elif setting[0] == "CALLBACK":
				pass

			else:
				print "This trigger doesn't got any template"

	def Check_Triggers(self, keys):
		now = time.time()

		# Loop all timer-triggers
		for trigger in self.timer_triggers:
			# If our timer have run out,
			if trigger.triggers['Stop_Time'] < now:
				self.Execute_Trigger(trigger)

				if not trigger.permanent:
					self.Del_Trigger(trigger)

		# Loop all key-triggers
		for trigger in self.key_triggers:
			for key in trigger.triggers['Keys']:

				# If the key is pressed right now
				if keys[key] == 1:
					self.Execute_Trigger(trigger)

					# Don't reset the key of we got a callback, the callback takes care of it then
					if trigger.triggers['Keys'][key] and not len(trigger.callbacks):
						keys[key] = 0

					# Neither delete it if we got a trigger
					if not trigger.permanent and not len(trigger.callbacks):
						self.Del_Trigger(trigger)

					break

				# If the key have been released
				elif keys[key] == -1:
					if len(trigger.callbacks):
						self.Execute_Callback(trigger)

					if trigger.triggers['Keys'][key]:
						keys[key] = 0

					if not trigger.permanent:
						self.Del_Trigger(trigger)


		# TODO: Implement triggercheck for positions

	def Del_Trigger(self):
		pass

	def Ugly_Function_For_Loading_Main_Keytriggers(self):
		# TODO: These triggers should be initialize when the game starts,
		#		we dont wanna bind these in the menu, tho
		#		right now we only check triggers when the game is running,
		#		but it could be input for the menu as well
		# TODO: Load these triggers from a CONFIG FILE INSTEAD, thank ya
		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_SPACE" : True}},
			trigger_settings = [["FUNCTION", self.main.player.jump]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_W" : True, "KEY_UP" : True}},
			trigger_settings = [["FUNCTION", self.main.player.start_walk, \
					self.main, 0.0]],
			callback_settings = [["FUNCTION", self.main.player.stop_walk]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_A" : True, "KEY_LEFT" : True}},
			trigger_settings = [["FUNCTION", self.main.player.start_walk, \
					self.main, -90.0]],
			callback_settings = [["FUNCTION", self.main.player.stop_walk]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_S" : True, "KEY_DOWN" : True}},
			trigger_settings = [["FUNCTION", self.main.player.start_walk, \
					self.main, 180.0]],
			callback_settings = [["FUNCTION", self.main.player.stop_walk]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_D" : True, "KEY_RIGHT" : True}},
			trigger_settings = [["FUNCTION", self.main.player.start_walk, \
					self.main, 90.0]],
			callback_settings = [["FUNCTION", self.main.player.stop_walk]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F" : True}},
			trigger_settings = [
				["EXECUTE",
"""import math
if time.time() - self.lastFireball > 0.5:
	self.lastFireball = time.time()
	xrotrad = math.radians(self.main.input.xrot)
	yrotrad = math.radians(self.main.input.yrot + 180.0)
	f = GameObject(\"Fireball\", \"Fireball 1\",
		(self.main.player.data.position[0],
		self.main.player.data.position[1],
		self.main.player.data.position[2]),
		(0.0, 0.0, 0.0), 0.1, 20,
		(14.0 * math.sin(yrotrad), -5 - 14.0 * -math.sin(xrotrad), 14.0 * -math.cos(yrotrad)),
		None, self.main.player.data.id)
	print self.main.player.data.id
	print f.data.owner

	import cPickle
	from network import *

	USend(self.main.networkThread.addr, 2,
		cPickle.dumps(f.data))"""
				]
			],
			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_ESCAPE" : True}},
			trigger_settings = [["FUNCTION", self.main.state_manager.push, \
					self.main.menu.menu_is_open, None]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_U" : True}},
			trigger_settings = [
				["FUNCTION", pygame.mouse.set_visible, 1],
				["FUNCTION", pygame.event.set_grab, 0]
			],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_G" : True}},
			trigger_settings = [
				["FUNCTION", pygame.mouse.set_visible, 0],
				["FUNCTION", pygame.event.set_grab, 1]
			],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F1" : True}},
			trigger_settings = [["EXECUTE", \
					"self.main.player.data.position = (0.0, 0.0, -40.0)"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F2" : True}},
			trigger_settings = [["EXECUTE", \
					"self.main.octree.debugLines ^= 1"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F3" : True}},
			trigger_settings = [["EXECUTE", \
					"self.main.graphics.spectator ^= 1"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F6" : True}},
			trigger_settings = [["EXECUTE", \
					"self.main.graphics.toggleDrawAxes ^= 1"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_F7" : True}},
			trigger_settings = \
					[["EXECUTE", "self.main.graphics.wireframe ^= 1"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_J" : True}},
			trigger_settings = [["EXECUTE", "self.main.input.speed += 100"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_K" : True}},
			trigger_settings = [["EXECUTE", "self.main.input.speed -= 100"]],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_+" : True, "KEY_KP_PLUS" : True}},
			trigger_settings = [
				["EXECUTE", "self.main.graphics.reDraw = True"]
			],

			permanent = True
		)

		self.Add_Trigger(
			triggers = {"Keys" : {"KEY_-" : True, "KEY_KP_MINUS" : True}},
			trigger_settings = [
				["EXECUTE", "self.main.graphics.reDraw = True"]
			],

			permanent = True
		)
