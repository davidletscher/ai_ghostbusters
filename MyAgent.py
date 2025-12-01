from Agent import *
from ParticleFilter import *
from Ghost import *
from Agent import *

from collections import defaultdict

class MyAgent(BaseAgent):
	def __init__(self, board, pacman, numGhosts, timeLimit):
		"""Create a new agent instance."""
		BaseAgent.__init__(self, board, pacman, numGhosts, timeLimit)
		
	def findMove(self, observations: list[int]) -> None:
		"""
		Determine the move that Pacman will make based on the observations and current state.
		
		** Parameter **
		
		*`observations` (list[int]): a list of integers of the noisy distances measured to each ghost.
		
		Note that if they ghost has been caught the the observed distance will always be zero.
		
		To actually set the move, `setMove` must be called before time experires.
		"""
		
		# If you are using a particle filter, you should use the observations to
		# update your predictions here
		
		# Find the direction to head that makes its average distance to the
		# ghosts as small as possible.
		bestValue = float('inf')
		for direction, newLocation in self._pacman.possibleMoves().items():
			avgDistance = 0.
			for ghostId in range(self._numGhosts):
				for loc, p in self.ghostPositionDistribution(ghostId).items():
					avgDistance += p * self._board.pathDistance(newLocation, loc)
			if avgDistance < bestValue:
				bestValue = avgDistance
				self.setMove(direction)
		
	def ghostCaught(self, ghostId: int) -> None:
		"""
		Update the predicted ghosts positions based on the fact that the ghost has just been caught by Pacman.
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has not been caught.
		
		Note that the agent has a reference to Pacman what can be used to access Pacman's current location.
		"""
		pass
		
	def ghostNotCaught(self, ghostId: int) -> None:
		"""
		Update the predicted ghosts positions based on the fact that the ghost has not been caught by Pacman in its current location.
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has been caught.
		
		Note that the agent has a reference to Pacman what can be used to access Pacman's current location.
		"""
		pass
		
	def ghostsHaveMoved(self) -> None:
		"""
		Update the predicted ghost positions knowning that each ghost now moves using its own behavior.
		"""
		pass
		
	def ghostPositionDistribution(self, ghostId: int) -> dict[Coordinate, float]:
		"""
		Return the probability of a ghost being in each possible position on the map.
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has been caught.
		
		** Return **
		
		A dictionary mapping board locations to the probability that the ghost is in that location.
		
		The sum of the dictionary values must add to 1 and each value cannot be negative.
		"""
		return { location : 1/len(self._board.validLocations()) for location in self._board.validLocations()}
		
	def ghostTypeDistribution(self, ghostId: int) -> dict[str, float]:
		"""
		Return the probability of a ghost having each particular behaviour type
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has been caught.
		
		** Return **
		
		A dictionary mapping board locations to the probability that the has a particular behavior represented
		by a single character RSCBO).  See the documentation for the Ghost module for details on each behavior.
		
		The sum of the dictionary values must add to 1 and each value cannot be negative.
		"""
		return { ghostType : .2 for ghostType in 'RSCBO' }
