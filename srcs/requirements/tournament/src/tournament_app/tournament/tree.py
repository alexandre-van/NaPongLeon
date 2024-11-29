from root import Root
#from ..utils.logger import logger
import math

class Tree:
	def __init__(self, teams):
		print(f"create tree")
		leaf_number = math.ceil(len(teams) / 2)
		if len(teams) == 1:
			leaf_number = 0
		self.root = Root(leaf_number=leaf_number)
		self.init_matchs(teams)
		self.print(self.export())

	def init_matchs(self, teams):
		prev_team = None
		for team in teams:
			if prev_team:
				branch = self.root.get_free_branch(self.root.level_max)
				if branch:
					print(f"level : {branch.level}")
					branch.init_match(prev_team, team)
				prev_team = None
			else:
				prev_team = team
		if prev_team:
			branch = self.root.get_free_branch(self.root.level_max)
			if branch:
				if branch.prev_branch:
					branch = branch.prev_branch
				print(f"level : {branch.level}")
				branch.init_bench(team)

	def export(self):
		tree = []
		i = 0
		while i <= self.root.level_max:
			tree.append(list(branch.print() for branch in self.root.get_branches(i)))
			i += 1
		return tree
	
	def print(self, tree):
		i = 0
		for level in tree:
			if i == 0:
				print("Winner")
			elif i == 1:
				print("Final")
			elif i == 2:
				print("Demi-final")
			elif i == 3:
				print("Quart-final")
			else:
				print(f"level {i}")
			for branch in level:
				print(branch)
			i += 1

