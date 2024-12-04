from ..utils.logger import logger
from .branch import Branch

class Root:
	def __init__(self, leaf_number):
		self.level_max = self.init_level_max(leaf_number)
		logger.debug(f"create root || levelmax : {self.level_max}")
		self.level = 0
		self.prev_branch = None
		self.next_branch = None
		self.bench = None
		if self.level < self.level_max:
			self.next_branch = Branch(self.level_max, level=self.level+1, prev_branch=self)

	def init_level_max(self, leaf_number):
		level_max = 1
		if leaf_number == 0:
			return 0
		while leaf_number > 1:
			leaf_number /= 2
			level_max += 1
			if leaf_number == 1:
				break
		return level_max

	def get_current_level(self):
		if not self.next_branch:
			return self.level
		return self.next_branch.get_current_level()
	
	def get_free_branch(self, level):
		if self.level == level\
			and self.bench is None:
			return self
		if not self.next_branch:
			return None
		return self.next_branch.get_free_branch(level)
	
	def get_branches(self, level):
		branches = []
		if level == self.level:
			if self.bench:
				branches.append(self)
		elif not self.next_branch or level > self.level_max:
			return None
		else :
			self.next_branch.get_branches(branches, level)
		return branches
	
	def print(self):
		if self.bench:
			return [self.bench.name]
		return []
	
	def init_bench(self, team):
		logger.debug(f"Create bench || team : {team.name}")
		self.bench = team