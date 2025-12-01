"""
Management routines for ghosts in a game of Ghostbusters.

##Ghost behavior##

There are five different types of ghosts in the game, each with a distinct
behavior.

**Behaviors common to all ghosts**
	
* Ghosts will never reverse their direction.
	Because of this, ghosts will sometime run into Pacman.

* Once a ghost starts down a corridor it will follow it and its turns until an intersection is reached.

* Once an intersection is reached the ghost paused for one turn to decide it's next move.
	
**Behaviors specific to each ghost type**
	
*Random ghost*

At each intersection, the random ghost will choose randomly which way to go.
It will never go back the way it came and all options are equally likely.

*Scared ghost*

Scared ghosts will identify where Pacman will be in four moves if it doesn't turn and choose
an action, if possible, that increases its path distance to Pacman.  The ghost will never turn arrow, though.
Note that if more than one direction takes it away from Pacman then it will choose randomly among the options.

*Corner seeking ghost*

The ghost will move towards a corner point that is furthest from Pacman's current location.  This can be
exploited by Pacman if the ghost is cornered as the shortest path to that corner might take it nearer to Pacman.
If there are multiple directions that it can take to the corner, then it will choose one that takes it further
from Pacman.

*Brave(ish) ghost*

This ghost is brave until it gets too close and then it acts like a scared ghost.  If Pacman is more that 6
spaces away, it will move towards Pacman when given a choice.  However, if it is within 6 spaces of Pacman then
it's behavior is the same as the scared ghost.

*Orbitting ghost*

As long as Pacman is a distance 6 or more away, the ghost moves towards the center of the board and circles it. 
Otherwise it will move away from Pacman like the scared ghost does.
	
"""

from Board import *
from Pacman import *

from dataclasses import dataclass
import random
import copy

@dataclass(frozen=True)
class GhostState:
	"""
	Stores current state information about the ghost.
	
	**Member data:**
	
	* `alive` (bool): is the ghost currently alive
	* `ghostType` (str): single character indicating which ghost logic is used to make decisions
	* `location` (Coordinate): where the ghost is current located
	* `heading` (str): the direction (UDLR) that the ghost is facing
	* `thinking` (bool): is the ghost currently paused at an intersection to think
	
	*Ghost types:*
	
	* `'R'` Random ghost:  moves randomly
	* `'S'` Scared ghost:  always moves away from Pacman
	* `'C'` Corner seeking ghost:  always moves towards the corner of the board furthest from Pacman.
	* `'B'` Brave(ish) ghost:  Moves toward Pacman until it is withing 6 spaces and then moves away.
	* `'O'` Orbitting ghost:  Circles around the center of the board.
	"""
	
	alive: bool
	ghostType: str
	location: Coordinate
	heading: str
	thinking: bool
	
def moveGhost(state: GhostState, pacmanLocation: Coordinate, board: Board) -> GhostState:
	"""
	Advance the ghosts position to the next state.
	
	**Parameters**
	
	* `state` (GhostState): the current state of the ghost
	* `pacmanLocation` (Coordinate): the current location of Pacman
	* `board` (Board): the board/map for the game
	
	**Return**
	
	The resulting ghost state
	"""
	return random.choice(possibleGhostMoves(state, pacmanLocation, board))
	
def possibleGhostMoves(state: GhostState, pacmanLocation: Coordinate, board: Board) -> list[GhostState]:
	"""
	Find all possible results for the ghost moving.
	
	This returns a list of possible results (all equally likely) for where the ghost has moved to.  See the documention for
	moveGhost for a description of the possible results.
	"""
	
	if not state.alive:
		return [state]
	
	possibleMoves = []
	
	# If the ghost is moving down a coridor, have it continue
	moveOptions = { direction : newLocation for (direction, newLocation) in board.possibleMoves(state.location).items() if direction != board.reverseDirection[state.heading] }
	if len(moveOptions) == 1:
		for (direction, newLocation) in moveOptions.items():
			if direction != board.reverseDirection[state.heading]: # Only happens once in loop
				result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
				possibleMoves.append(result)
	
	# If it arrives at a corridor then have it pause
	elif not state.thinking and len(moveOptions) >= 2:
		result = GhostState(alive=True, ghostType=state.ghostType, location=state.location, heading=state.heading, thinking=True)
		possibleMoves.append(result)
	
	# Otherwise, have it decide based on its specific behavior pattern.
	else:
		match state.ghostType:
			case 'R':
				for (direction, newLocation) in moveOptions.items():
					result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
					possibleMoves.append(result)
				
			case 'S':
				distancesToPacman = [ (direction, newLocation, board.pathDistance(pacmanLocation, newLocation)) for (direction, newLocation) in moveOptions.items() ]
				maxDistanceToPacman = max( data[2] for data in distancesToPacman )
				for (direction, newLocation, distance) in distancesToPacman:
					if distance == maxDistanceToPacman:
						result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
						possibleMoves.append(result)
				
			case 'C':
				# Find the furthest corner
				cornerDistancesToPacman = { corner : board.pathDistance(pacmanLocation, corner) for corner in board.getCorners() }
				maxDistanceFrmCornerToPacman = max(cornerDistancesToPacman.values())
				furthestCorners = [ corner for (corner, distanceToPacman) in cornerDistancesToPacman.items() if distanceToPacman == maxDistanceFrmCornerToPacman ]
				
				for corner in furthestCorners:					
					# Choose direction that moves closer to that corner and away from Pacman, if possible.
					distancesToCorner = [ (direction, newLocation, board.pathDistance(corner, newLocation), board.pathDistance(pacmanLocation, newLocation)) for (direction, newLocation) in moveOptions.items() ]
					minDistanceToCorner = min( (data[2], -data[3]) for data in distancesToCorner )
					for (direction, newLocation, distance, distance2) in distancesToCorner:
						if (distance, -distance2) == minDistanceToCorner:
							result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
							possibleMoves.append(result)	
									
			case 'B':
				distancesToPacman = [ (direction, newLocation, board.pathDistance(pacmanLocation, newLocation)) for (direction, newLocation) in moveOptions.items() ]
				if board.pathDistance(pacmanLocation, state.location) > 6:
					minDistanceToPacman = min( data[2] for data in distancesToPacman )
					for (direction, newLocation, distance) in distancesToPacman:
						if distance == minDistanceToPacman:
							result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
							possibleMoves.append(result)
							
				else:
					maxDistanceToPacman = max( data[2] for data in distancesToPacman )
					for (direction, newLocation, distance) in distancesToPacman:
						if distance == maxDistanceToPacman:
							result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
							possibleMoves.append(result)
							
			case 'O':
				distancesToPacman = [ (direction, newLocation, board.pathDistance(pacmanLocation, newLocation)) for (direction, newLocation) in moveOptions.items() ]
				if board.pathDistance(pacmanLocation, state.location) <= 6:
					maxDistanceToPacman = max( data[2] for data in distancesToPacman )
					for (direction, newLocation, distance) in distancesToPacman:
						if distance == maxDistanceToPacman:
							result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
							possibleMoves.append(result)
							
				else:
					distancesToCenter = [ (direction, newLocation, board.pathDistance(board.getPacmanStart(), newLocation)) for (direction, newLocation) in moveOptions.items() ]
					minDistanceToCenter = min( data[2] for data in distancesToCenter )
					for (direction, newLocation, distance) in distancesToCenter:
						if distance == minDistanceToCenter:
							result = GhostState(alive=True, ghostType=state.ghostType, location=newLocation, heading=direction, thinking=False)
							possibleMoves.append(result)
	
	return possibleMoves

def randomGhost(board: Board) -> GhostState:
	"""
	Return a random ghost starting state.
	
	**Parameter**
	
	* `board` (Board): the board the the ghost will be placed on.
	
	The ghost will be choosen randomly among the five different behaviors and placed
	randomly on the board at least 3 moves away from Pacman's starting location.  The
	ghost will be initialized in thinking mode and will not move until the second turn.
	"""
	
	valid = False
	while not valid:
		ghost = GhostState(alive=True, ghostType = random.choice('RSCBO'), location = random.choice(board.validLocations()), heading='', thinking=True)
		valid = Board.manhattanDistance(ghost.location, board.getPacmanStart()) > 2

	return ghost
