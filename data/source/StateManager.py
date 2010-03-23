class State:
	def __init__(self):
		self.prev = None
		self.function = None

class StateManager:
	def __init__(self):
		self.current_state = None
	
	def __del__(self):
		self.pop_all(None)
	
	def push(self, function, caller):
		if function is not None:
			
			new_state = State()
			new_state.prev = self.current_state
			new_state.function = function

			self.current_state = new_state

			new_state.function(caller, "INIT_PURPOSE")

			return True

		return False

	def pop(self, caller):
		if self.current_state is not None:
			self.current_state.function(caller, "STOP_PURPOSE")

			del_state = self.current_state

			self.current_state = self.current_state.prev

			del_state.prev = None

			return True

		return False
	
	def pop_all(self, caller):
		if self.current_state is not None:
			while self.current_state is not None:
				self.pop(caller)
			
			return True

		return False

	def process(self, caller):
		if self.current_state is not None:
			self.current_state.function(caller, "FRAME_PURPOSE")
			return True

		return False	
