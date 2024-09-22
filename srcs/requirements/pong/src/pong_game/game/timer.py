import time

class Timer:
	def __init__(self):
		self.start = time.time()

	def reset(self):
		self.start = time.time()

	def get_elapsed_time(self):
		if self.start == None:
			self.start = time.time()
		return time.time() - self.start

	def waiting(self, timer):
		if self.get_elapsed_time() >= timer:
			return 1
		return 0
	
	def settup(self, value):
		self.start = value
