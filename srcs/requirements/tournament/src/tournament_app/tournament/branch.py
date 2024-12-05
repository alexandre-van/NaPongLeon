from .match import Match
from ..utils.logger import logger

class Branch:
	def __init__(self, level_max, level, prev_branch, id, id_set):
		self.level = level
		self.id = id
		self.prev_branch = prev_branch
		self.next_branches = None
		if level < level_max:
			self.next_branches = []
			left_id = id + 1
			# Vérification de l'unicité de left_id
			while left_id in id_set:
				left_id += 1
			id_set.add(left_id)
			self.next_branches.append(Branch(level_max, level=level+1, prev_branch=self, id=left_id, id_set=id_set))

			right_id = left_id + pow(2, level_max - level - 1)
			# Vérification de l'unicité de right_id
			while right_id in id_set:
				right_id += 1
			id_set.add(right_id)
			self.next_branches.append(Branch(level_max, level=level+1, prev_branch=self, id=right_id, id_set=id_set))
		self.match = None
		self.bench = None
		logger.debug(f"create branch || level : {level}")

	def init_match(self, team1, team2):
		self.match = Match(self.id, team1, team2)

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

	def export(self):
		return {
			'id': self.id,
			'level': self.level,
			'match': self.match.export() if self.match else None,
			'bench': self.bench.export() if self.bench else None
		}