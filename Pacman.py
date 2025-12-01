from Board import *

from dataclasses import dataclass
		
@dataclass
class PacmanState:
	"""
	Store the state information of Pacman.
	
	location	a map Coordinate for Pacman
	heading		the direction pacman is facing (NESW or empty)
	"""
	
	location: Coordinate
	heading: str = ''


class Pacman:
	"""
	Manages state of Pacman in the Ghostbusters game.
	"""
	
	_board: Board
	_state: PacmanState
	
	def __init__(self, board: Board):
		"""
		Create a new Pacman instance starting a Pacmans starting point on the board.
		"""
		
		self._board = board
		self._state = PacmanState(board.getPacmanStart(), '')
		
	def getState(self) -> PacmanState:
		"""Return the current state of Pacman"""
		
		return self._state
		
	def possibleMoves(self) -> dict[str, Coordinate]:
		"""
		Return all of the valid moves that Pacman can make.
		
		** Return value **
		
		A dictionary mapping possible directions (NESW) to the resulting
		location that Pacman would move to.
		"""
		
		return self._board.possibleMoves(self._state.location)
		
	def move(self, direction: str) -> None:
		"""
		Move pacman in the specified direction.
		
		If the direction is invalid, then the location is not changed.
		"""
		
		result = self._board.possibleMoves(self._state.location)[direction]
		if result:
			self._state.location = result
		
