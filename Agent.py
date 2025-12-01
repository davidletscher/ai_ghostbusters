from Board import *
from Pacman import *

import time

class BaseAgent:
	"""
	Agent for deciding on the actions in Ghostbusters.
	
	** Member data **
	
	*`board` (Board): the map of the current game
	*`pacman` (Pacman): the Pacman instance storing its position and movement.
	*`numGhosts` (int): the number of ghosts in the game
	*`timeLimit` (float): how long the agent has to determine the next move
	
	In the child class the following methods must be overloaded:
	
	* `findMove`
	* `ghostCaught`
	* `ghostNotCaught`
	* `ghostsHaveMoved`
	* `ghostPositionDistribution`
	* `ghostTypeDistribution`
	
	Also the constructor for the child class must call BaseAgent's constructor.
	"""
	
	def __init__(self, board: Board, pacman: Pacman, numGhosts: int, timeLimit: float):
		"""Create a new agent instance."""
		self._board = board
		self._pacman = pacman
		self._numGhosts = numGhosts
		self._timeLimit = timeLimit
		self._startTime = 0
		self._move = None

	def timeRemaining(self) -> bool:
		"""Check if time remains before the turn expires."""
		
		if time.time() < self._startTime + self._timeLimit:
			return True
		return False

	def setMove(self, move: str) -> None:
		"""
		Set the move that the agent would like to make.
		
		** Parameter **
		
		*`move` (str): One of 'N', 'S', 'E' or 'W'
		"""
		
		if self.timeRemaining():
			self._move = move

	def getMove(self) -> str | None:
		"""Return the move that has been set (if any)"""
		return self._move
		
	def findMove(self, observations: list[int]) -> None:
		"""
		Determined the move that Pacman will make based on the observations and current state.
		
		** Parameter **
		
		*`observations` (list[int]): a list of integers of the noisy distances measured to each ghost.
		
		Note that if they ghost has been caught the the observed distance will always be zero.
		
		To actually set the move, `setMove` must be called before time experires.
		"""
		pass
		
	def ghostCaught(self, ghostId: int) -> None:
		"""
		Update the predicted ghosts positions based on the fact that the ghost has just been caught by Pacman.
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has been caught.
		
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
		pass
		
	def ghostTypeDistribution(self, ghostId) -> dict[str, float]:
		"""
		Return the probability of a ghost having each particular behaviour type
		
		** Parameter **
		
		*`ghostId` (int): a integer (0 to number of ghosts - 1) indicating which ghost has been caught.
		
		** Return **
		
		A dictionary mapping board locations to the probability that the has a particular behavior represented
		by a single character RSCBO).  See the documentation for the Ghost module for details on each behavior.
		
		The sum of the dictionary values must add to 1 and each value cannot be negative.
		"""
		pass
