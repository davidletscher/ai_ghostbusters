from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Coordinate:
	"""Stores the location on the Ghostbusters board."""
	
	x: int
	y: int
	
	def __str__(self):
		return f'({self.x}, {self.y})'

class Board:
	"""
	Base class for a board in Ghostbusters game.
	
	** Member data **
	
	* `_map` (list[str]): effectively a 2D array of what is at each map location.
	Each entry is W = wall, S = Pacman starting location, A/B = endpoints of the tunnel
	to the other side of the board.
	* `_size' (int): the width and height of the game board
	"""
	
	_map: list[str]
	_size: int
	_mapDistance: dict[ tuple[Coordinate, Coordinate], int ]
	_fieldOfPlay: set[Coordinate]
	
	def __init__(self):
		self._map = [	'WWWWWWWWWWWWWWWWWWW', 
						'W        W        W',
						'W WW WWW W WWW WW W',
						'W  W           W  W', 
						'WW W W WWWWW W W WW', 
						'W    W   W   W    W',
						'W WW WWW W WWW WW W', 
						'W    W       W    W', 
						'WWWW W WW WW W WWWW',
						'A      WWSWW      B', 
						'WWWW W WW WW W WWWW', 
						'W    W       W    W',
						'W WW WWW W WWW WW W', 
						'W    W   W   W    W', 
						'WW W W WWWWW W W WW',
						'W  W           W  W', 
						'W WW WWW W WWW WW W', 
						'W        W        W',
						'WWWWWWWWWWWWWWWWWWW' ]
	
		self._size = len(self._map)
		
		self.reverseDirection = { '': '', 'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E' }
		
		# Find the possible locations for the pacman and ghosts on the board.
		self._fieldOfPlay = []
		for y, row in enumerate(self._map):
			for x, entry in enumerate(row):
				if entry != 'W':
					self._fieldOfPlay.append(Coordinate(x,y))
					
				if entry == 'S':
					self._pacmanStart = Coordinate(x,y)	
				elif entry == 'A':
					self._tunnelA = Coordinate(x,y)
				elif entry == 'B':
					self._tunnelB = Coordinate(x,y)
					
		# Calculate the distance from any two valid coordinates
		self._mapDistance = { (location,location) : 0 for location in self._fieldOfPlay }
		changed = True
		explored = set()
		while changed:
			changed = False
			currentDist = max(self._mapDistance.values())
			for (loc1,loc2) in list(self._mapDistance.keys()):
				if (loc1, loc2) not in explored:
					explored.add((loc1, loc2))
					if self._mapDistance[(loc1,loc2)] == currentDist:
						for location in self.possibleMoves(loc1).values():
							if (loc2, location) not in self._mapDistance:
								self._mapDistance[(loc2, location)] = currentDist + 1
								self._mapDistance[(location, loc2)] = currentDist + 1
								changed = True
						for location in self.possibleMoves(loc2).values():
							if (loc1, location) not in self._mapDistance:
								self._mapDistance[(loc1, location)] = currentDist + 1
								self._mapDistance[(location, loc1)] = currentDist + 1
								changed = True
							
		# Setup noisy distances
		self._errorDistribution = [ 1.7**i for i in range(6) ]
		self._errorDistribution += self._errorDistribution[:-1][::-1]

		s = float(sum(self._errorDistribution))
		for i in range(len(self._errorDistribution)):
			self._errorDistribution[i] /= s
			
		distribution = {}
		maxN = 0
		for d in range(1,2*self._size):
			for i in range(len(self._errorDistribution)):
				n = min(max(1,d+i-len(self._errorDistribution)//2), 2*self._size+2)
				maxN = max(n,maxN)
				distribution[(n,d)] = distribution.get((n,d), 0) + self._errorDistribution[i]
		
		for n in range(maxN+1):
			s = 0
			for ((n2,d),v) in distribution.items():
				if n == n2:
					s += v
			  
			for ((n2,d),v) in distribution.items():
				if n == n2:
					distribution[(n,d)] /= s
			  
		distribution[(0,0)] = 1.
		self._noisyDistanceProb = distribution
		
	def possibleMoves(self, location: Coordinate) -> dict[str, Coordinate]:
		"""
		Return the possible moves that can be made from a location.
		
		location	the location to be examined
		return		a dictionary maping possible directions (NESW) to 
					the resulting coordinate of a move in that direction
		"""
		possiblities = dict()		
		
		if Coordinate(location.x-1, location.y) in self._fieldOfPlay:
			possiblities['W'] = Coordinate(location.x-1, location.y)
		if Coordinate(location.x+1, location.y) in self._fieldOfPlay:
			possiblities['E'] = Coordinate(location.x+1, location.y)
		if Coordinate(location.x, location.y-1) in self._fieldOfPlay:
			possiblities['N'] = Coordinate(location.x, location.y-1)
		if Coordinate(location.x, location.y+1) in self._fieldOfPlay:
			possiblities['S'] = Coordinate(location.x, location.y+1)
		
		# Special case for classical map for the tunnel from one side 
		# of screen to the other
		if self._map[location.y][location.x] == 'A':
			possiblities['W'] = self._tunnelB
		elif self._map[location.y][location.x] == 'B':
			possiblities['E'] = self._tunnelA
			
		return possiblities

	def validLocations(self) -> set[Coordinate]:
		"""Return all of the valid locations for a ghost on the board."""
		return self._fieldOfPlay
		
	@staticmethod
	def manhattanDistance(location1: Coordinate, location2: Coordinate) -> int:
		"""Return the Manhattan distance between two board locations"""
		
		return abs(location1.x - location2.x) + abs(location1.y - location2.y)
		
	def pathDistance(self, location1: Coordinate, location2: Coordinate) -> int:
		"""Return the distance following a path on the board between two locations."""
		return self._mapDistance[(location1, location2)]

	def noisyDistance(self, location1:  Coordinate, location2: Coordinate) -> int:
		"""Return a noisy Manhattan distance measurement between the two locations."""
		
		m = self.manhattanDistance(location1, location2)
		e = random.choices(list(range(len(self._errorDistribution))), weights=self._errorDistribution, k=1)[0] - len(self._errorDistribution)//2
		return min(max(1,m+e), 2*self._size+2)
		
	def noisyDistanceProb(self, noisyDistance: int, actualDistance: int) -> float:
		"""
		Return the probability of an actual distance having a particular noisy distance.
		
		**Parameters**
		
		* `noisyDistance` (int): the measured noisy distance between two locations
		* `actualDistance` (int): the actual distance between the two locations
		
		**Return**
		
		The probability that two locations `actualDistance` apart are measurd to be
		`noisyDistance` away from each other.
		"""
		
		return self._noisyDistanceProb.get((noisyDistance,actualDistance),0.)

	def getPacmanStart(self):
		return self._pacmanStart
		
	def getCorners(self):
		return [Coordinate(1,1), Coordinate(1,self._size-2), Coordinate(self._size-2,1), Coordinate(self._size-2,self._size-2)]

	def getSize(self):
		return self._size
