class Process:
	def __init__(self):
		self.prev = None
		self.next = None
		self.function = None
		self.id = 0

class ProcessManager:
	def __init__(self):
		self.first_process = None
		self.last_process = None
	def __del__(self):
		self.pop_all(None)

	def push(self, function,  caller):
		if function is not None:
			new_process = Process()
			new_process.next = None
			new_process.prev = self.last_process
			new_process.function = function

			if self.first_process is None:
				self.first_process = new_process
				new_process.id = 1
			else:
				new_process.id = self.last_process.id + 1
				self.last_process.next = new_process

			self.last_process = new_process
			new_process.function(caller, "INIT_PURPOSE")

			return new_process.id
		return None

	def pop(self, id, caller):
		cur_proc = Process
		cur_proc = self.first_process

		while cur_proc is not None:
			if cur_proc.id is id:
				if cur_proc.prev is None:
					self.first_process = cur_proc.next
				else:
					 cur_proc.prev.next = cur_proc.next
				if cur_proc.next is None:
					self.last_process = cur_proc.prev
				else:
					cur_proc.next.prev = cur_proc.prev

				cur_proc.function(caller, "STOP_PURPOSE")

				cur_proc.next = None
				cur_proc.prev = None

				return True
			cur_proc = cur_proc.next
		return False

	def pop_all(self, caller):
		cur_proc = self.first_process
		pop_proc = Process

		if cur_proc is None:
			return False

		while cur_proc is not None:
			pop_proc = cur_proc
			cur_proc = cur_proc.next

			self.pop(pop_proc.id, None)

		self.first_process = None
		last_process = None

		return True


	def process(self, caller):
		if self.first_process is not None:
			cur_proc = self.first_process
			while cur_proc is not None:
				cur_proc.function(caller, "FRAME_PURPOSE")
				cur_proc = cur_proc.next

			return True

		return False

		pass


