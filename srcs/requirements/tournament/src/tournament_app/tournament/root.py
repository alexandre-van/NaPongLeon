#from ..utils.logger import logger
from .branch import Branch
import math

class Root:
	def __init__(self, leaf_number):
		self.level_max = self.init_level_max(leaf_number)
		self.level = 0
		self.prev_branch = None
		self.next_branches = None
		if self.level < self.level_max:
			self.next_branches = []
			self.next_branches.append(Branch(self.level_max, level=self.level+1, prev_branch=self))
			self.next_branches.append(Branch(self.level_max, level=self.level+1, prev_branch=self))
		logger.debug(f"create root || levelmax : {self.level_max}")

	def init_level_max(self, leaf_number):
		level_max = 0
		while leaf_number >= 1:
			leaf_number /= 2
			level_max += 1
			if leaf_number == 1:
				break
		return level_max