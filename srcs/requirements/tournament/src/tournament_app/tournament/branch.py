from ..utils.logger import logger
from .match import Match

class Branch:
	def __init__(self, level_max, level, prev_branch):
		self.level = level
		self.prev_branch = prev_branch
		self.next_branches = None
		if level < level_max:
			self.next_branches = []
			self.next_branches.append(Branch(level_max, level=level+1, prev_branch=self))
			self.next_branches.append(Branch(level_max, level=level+1, prev_branch=self))
		self.match = None
		logger.debug(f"create branch || level : {level}")

	def init_match(self, teams):
		self.match = Match(teams)