from .branch import Branch
from ..utils.logger import logger

class Tree:
	def __init__(self, teams):
		logger.debug(f"create tree")
		self.branches = []
		i = 0
		prv_team = None
		for team in teams:
			if len(self.branches) <= i:
				self.branches.append([])
			if prv_team:
				self.branches[i] = Branch(prv_team, team)
				prv_team = None
				i += 1
			else:
				prv_team = team