from .root import Root
from ..utils.logger import logger
import math

class Tree:
	def __init__(self, teams):
		logger.debug(f"create tree")
		leaf_number = math.ceil(len(teams) / 2)
		self.root = Root(leaf_number=leaf_number)

	def export(self):
		tree = []
