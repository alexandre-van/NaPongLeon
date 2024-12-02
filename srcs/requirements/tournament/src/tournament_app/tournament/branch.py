from .match import Match
from ..utils.logger import logger

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
		self.bench = None
		logger.debug(f"create branch || level : {level}")

	def init_match(self, team1, team2):
		self.match = Match(team1, team2)

	def init_bench(self, team):
		logger.debug(f"Create bench || team : {team.name}")
		self.bench = team

	def get_current_level(self):
		if not self.next_branches or len(self.next_branches) == 0:
			return self.level
		return max(next_branch.get_current_level() for next_branch in self.next_branches)
	
	def get_free_branch(self, level):
		if self.level == level\
			and self.match is None\
				and self.bench is None:
			return self
		if not self.next_branches or len(self.next_branches) == 0:
			return None
		return self.next_branches[0].get_free_branch(level) or self.next_branches[1].get_free_branch(level)

	def get_branches(self, branches, level):
		if self.level == level:
			branches.append(self)
		if not self.next_branches or len(self.next_branches) == 0:
			return
		list(next_branch.get_branches(branches, level) for next_branch in self.next_branches)

	def print(self):
		if self.match:
			return [self.match.print()]
		if self.bench:
			return [self.bench.name]
		return []