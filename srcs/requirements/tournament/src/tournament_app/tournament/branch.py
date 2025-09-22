from .match import Match
from ..utils.logger import logger
from .status import match_status

class Branch:
	def __init__(self, level_max, level, prev_branch, id, id_set):
		self.level = level
		self.id = id
		self.prev_branch = prev_branch
		self.next_branches = None
		self.game_mode = None
		self.modifiers = None
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

	def init_match(self, team1, team2, game_mode, modifiers):
		self.game_mode = game_mode
		self.modifiers = modifiers
		team1.set_current_branch(self)
		team2.set_current_branch(self)
		self.match = Match(self, team1, team2, game_mode, modifiers)
		self.bench = None

	def init_bench(self, team, game_mode, modifiers):
		self.game_mode = game_mode
		self.modifiers = modifiers
		team.set_current_branch(self)
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

	def ascend_team(self, team):
		if self.prev_branch.is_free():
			self.prev_branch.bench = team
			team.set_current_branch(self.prev_branch)
			if self.prev_branch.level > 0:
				for branch in self.prev_branch.next_branches:
					if branch.is_free():
						self.prev_branch.ascend_team(team)
		elif self.prev_branch.id != 0 and self.prev_branch.match is None \
			and self.prev_branch.bench != team:
			self.prev_branch.init_match(
				self.prev_branch.bench, team,
				self.game_mode, self.modifiers)

	async def update(self):
		if self.match:
			await self.match.update()
			if self.match.winner:
				self.ascend_team(self.match.winner)
		elif self.bench:
			wait = not any(next_branch.is_free() for next_branch in self.next_branches)
			if wait is False:
				self.ascend_team(self.bench)


	def is_free(self):
		ret = (self.match and (match_status['aborted'] == self.match.status or match_status['finished'] == self.match.status) and not self.match.winner) or (\
			self.match is None and self.bench is None)
		if ret:
			logger.debug(f"\n\n{self.id} is FREE\n\n")
		else:
			logger.debug(f"\n\n{self.id} is OCCUPED\n\n")
		return ret

	def export(self):
		return {
			'id': self.id,
			'level': self.level,
			'match': self.match.export() if self.match else None,
			'bench': self.bench.export() if self.bench else None
		}