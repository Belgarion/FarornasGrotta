import cPickle, math, os, os.path, pygame, pyopenal, uuid

from network import USend

class CSound:
	def __init__(self, main, frequency = 0, autoload = False):
		self.soundlist = []
		self.soundalias = []
		self.sourcelist = []

		self.listener = None
		self.buffer = None

		self.main = main

		self.data = {
						'Run' : {'UUID': None, 'Position': (0.0, 0.0, 0.0)},
						'Fireball' : {'UUID': None, 'Position': (0.0, 0.0, 0.0)},
						'Attack' : {'UUID': None, 'Position': (0.0, 0.0, 0.0)}
					}

		# TODO: Just for testing, normaly we wanna call this on our own?
		if frequency:
			self.Init_Sound(frequency)

		# TODO: Just for testing, normaly it will load sounds depending on the map
		if autoload:
			self.Load_All_Sounds()

	def __del__(self):
		self.Quit_Sound()

	def Init_Sound(self, frequency):
		pyopenal.init(None)

		self.listener = pyopenal.Listener(frequency)

	def Quit_Sound(self):
		self.Unload_All_Sound()

		self.listener = None
		self.buffer = None

		pyopenal.quit()

	def Send_Sound():
		pass

	def Source_Exist(self, uuid):
		for source in self.sourcelist:
			if uuid == source.uuid:
				return True
		return False

	def Sound_Exist(self, soundalias):
		if soundalias in self.soundalias:
			return True
		return False

	def Find_Index(self, uuid):
		for i, source in enumerate(self.sourcelist):
			if uuid == source.uuid:
				return i
		return -1

	def Find_Source(self, uuid):
		for source in self.sourcelist:
			if uuid == source.uuid:
				return source
		return None

	def Sound_Is_Playing(self, uuid):
		source = self.Find_Source(uuid)

		if self.Test_Source(source):
			if source.get_state() == pyopenal.AL_PLAYING:
				return True
			return False

	def Test_Source(self, source):
		return not source == None

	def Stop_Sound(self, uuid):
		source = self.Find_Source(uuid)

		if self.Test_Source(source):
			source.stop()

	def Play_Sound(self, soundalias, loop = False, position = (0.0, 0.0, 0.0)):
		if self.Sound_Exist(soundalias):
			# Create the source object and append it to our soundlist
			source = pyopenal.Source()
			self.sourcelist.append(source)

			# Give it a UUID
			source.uuid = uuid.uuid4().hex

			# Fetch the bufferdata and load it into our object
			source.buffer = self.soundlist[self.soundalias.index(soundalias)]

			# Some settings
			source.looping 		= loop
			source.position 	= position
			source.max_distance = 1.0

			# Start playing the sound from the buffer
			source.play()

			if self.main.networkThread.isAlive():
				USend(self.main.networkThread.addr, 6, cPickle.dumps((soundalias, source.uuid, loop, position)))

			return source.uuid

		else:
			print "Sound \"" + soundalias + "\" is NOT loaded. Skipping."

		return None

	def Add_Sound(self, soundalias, uuid, loop = False, position = (0.0, 0.0, 0.0)):
		if not self.Source_Exist(uuid):
			# Create the source object and append it to our soundlist
			source = pyopenal.Source()
			self.sourcelist.append(source)

			# Give it the right UUID
			source.uuid = uuid

			# Fetch the bufferdata and load it into our object
			source.buffer = self.soundlist[self.soundalias.index(soundalias)]

			# Some settings
			source.looping 		= loop
			source.position 	= position
			source.max_distance = 1.0

			# Start playing the sound from the buffer
			source.play()

	def Del_Sound_Net(self, uuid):
		if self.Source_Exist(uuid):
			if self.main.networkThread.isAlive():
				USend(self.main.networkThread.addr, 7, cPickle.dumps(uuid))

			self.Del_Sound(uuid)

	def Del_Sound(self, uuid):
		if self.Source_Exist(uuid):
			source = self.Find_Source(uuid)

			self.Stop_Sound(source)
			self.sourcelist.remove(source)
	

	# TODO: Load this as a loop into the processmanger or something, we dont wanna waste time here
	#		But we wanna have so we can turn our head and still have the sound correctly
	def Update_Sound(self):
		for source in self.sourcelist:
			real_x = source.position[0]
			real_z = source.position[2]

			if source.get_state() == pyopenal.AL_PLAYING:

				xrotate = self.main.player.orientation[0]

				my_x = (real_x*math.cos(xrotate)) + (real_z*math.sin(xrotate))
				my_z = (real_z*math.cos(xrotate)) - (real_x*math.sin(xrotate))

				source.position = (my_x, 0.0, my_z)

		return

	def Load_Sound(self, filename, soundalias = None):
		if not soundalias:
			soundalias = os.path.splitext(os.path.basename(filename))

		if not soundalias[0] in self.soundalias:
			if soundalias[1] == ".wav":
				sound = pyopenal.WaveBuffer(filename)

			if soundalias[1] == ".ogg":
				sound = pyopenal.OggVorbisBuffer(filename)

			self.soundlist.append(sound)
			self.soundalias.append(soundalias[0])

			print "Successfully loaded \033[0;94m" + os.path.basename(filename) + "\033[0m"
		else:
			print "Sound \"" + soundalias + "\" is already loaded. Skipping."

		return

	def Load_All_Sounds(self, directory = "data/sound/"):
		print "\033[0;92mLoading sounds...\033[0m"

		for files in os.listdir(directory):
			self.Load_Sound(directory + files)

	def Unload_All_Sound(self):
		self.soundlist = []
		self.soundalias = []

		self.sourcelist = []
