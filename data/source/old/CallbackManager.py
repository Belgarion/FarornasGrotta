import time

class Dummy:
	pass

class CallbackManager:
	def __init__(self):
		self.timer_triggers = []
		self.key_triggers = []
		self.position_triggers = []


	def Add_Trigger(self, template, options, permanent = False, triggers = {'Seconds' : None, 'Keys' : {}, 'Area' : {'Position' : None, 'Radie' :  None}}):
		trigger = Dummy()

		trigger.template = template

		trigger.options = options
		trigger.permanent = permanent

		trigger.triggers = triggers

		if template == "FUNCTION":
			trigger.function = options[0]

		if "Seconds" in triggers:
			now = time.time()

			trigger.triggers['Start_Time'] = now
			trigger.triggers['Stop_Time'] = now + triggers['Seconds']
			self.timer_triggers.append(trigger)

		if "Keys" in triggers:
			self.key_triggers.append(trigger)

		if "Area" in triggers and triggers['Area']['Position'] and triggers['Area']['Radie']:
			self.position_triggers.append(trigger)


	def Find_Trigger(self):
		pass

	def Execute_Trigger(self, trigger):
		if trigger.template is "FUNCTION":
			trigger.function(*trigger.options[1:])

		elif trigger.template is "VARIABLE":
			pass

		elif trigger.template is "NETWORK":
			pass

		elif trigger.template is "CALLBACK":
			pass

		else:
			print "This trigger doesn't got any template"

		return
	
	def D(self, trigger, keys):
		pass

	def Check_Triggers(self, keys):
		now = time.time()

		for trigger in self.timer_triggers:
			# If our timer have run out, 
			if trigger.triggers['Stop_Time'] < now:
				self.Execute_Trigger(trigger)

				if not trigger.permanent:
					self.Del_Trigger(trigger)

		for trigger in self.key_triggers:
			for key in trigger.triggers['Keys']:
				if keys[key] == 1:
					self.Execute_Trigger(trigger)	

					if trigger.triggers['Keys'][key]:
						keys[key] = 0

					if not trigger.permanent:
						self.Del_Trigger(trigger)

					break

	def Del_Trigger(self):
		pass
