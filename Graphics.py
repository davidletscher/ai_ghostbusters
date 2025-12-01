from Board import *
from cs1graphics import *
from math import pow

intensityPower = .2

class GhostbusterGraphics:
	"""
	Class for managing the graphics for a game of Ghostbusters.
	"""
	
	def __init__(self, board, numGhosts, width):
		self._board = board
		self._scale = width / (self._board.getSize() + 7)
		self._canvas = Canvas(width, int(self._scale*self._board.getSize()), title='Ghostbusters')
		self._canvas.setBackgroundColor('tan')
		self._caughtGhosts = []
		
		self._squares = {}
		for y, row in enumerate(self._board._map):
			for x, entry in enumerate(row):
				self._squares[Coordinate(x,y)] = Square(self._scale, Point((x+.5)*self._scale, (y+.5)*self._scale))
				self._squares[Coordinate(x,y)].setBorderWidth(0)
				if entry == 'W':
					self._squares[Coordinate(x,y)].setFillColor('tan')
				else:
					self._squares[Coordinate(x,y)].setFillColor('black')
				self._canvas.add(self._squares[Coordinate(x,y)])
				
		self._pacman = Circle(.4*self._scale, Point(-100,-100))
		self._pacman.setFillColor('yellow')
		self._canvas.add(self._pacman)
		
		self._ghostBaseColors = []
		for i in range(numGhosts):
			angle = i*360/numGhosts
			if angle <= 60:
				a = angle
				self._ghostBaseColors.append( (255, int(a/60*255), 0) )
			elif angle <= 120:
				a = angle - 60
				self._ghostBaseColors.append( (int(255 - a/60*255), 255, 0) )
			elif angle <= 180:
				a = angle - 120
				self._ghostBaseColors.append( (0, 255, int(a/60*255)) )
			elif angle <= 240:
				a = angle - 180
				self._ghostBaseColors.append( (0, int(255 - a/60*255), 255) )
			elif angle <= 300:
				a = angle - 240
				self._ghostBaseColors.append( (int(a/60*255), 0, 255) )
			elif angle <= 360:
				a = angle - 300
				self._ghostBaseColors.append( (255, 0, int(255 - a/60*255)) )
					
		self._score = Text('Score: 0', .8*self._scale, Point((self._board.getSize()+3.5)*self._scale, self._scale))
		self._score.setJustification('left')
		self._canvas.add(self._score)
		
		self._turn = Text('Turn: 1', .8*self._scale, Point((self._board.getSize()+3.5)*self._scale, 3*self._scale))
		self._turn.setJustification('left')
		self._canvas.add(self._turn)
		
		for j, t in enumerate('RSCBO'):
			t = Text(t, self._scale*.5, Point((self._board.getSize()+2+j)*self._scale, 5*self._scale))
			self._canvas.add(t)
		
		self._ghostType = {}
		for i in range(numGhosts):
			c = Circle(.4*self._scale, Point((self._board.getSize()+.5)*self._scale, (6+i)*self._scale))
			c.setFillColor(Color(self._ghostBaseColors[i]))
			self._canvas.add(c)
					
			for j, t in enumerate('RSCBO'):
				c = Circle(.4*self._scale, Point((self._board.getSize()+2+j)*self._scale, (6+i)*self._scale))
				c.setFillColor('black')
				self._canvas.add(c)
				
				self._ghostType[(i,t)] = c
				
		self._ghosts = []
		for i in range(numGhosts):
			c = Circle(.3*self._scale, Point(-100, -100))
			c.setFillColor(self._ghostBaseColors[i])
			self._canvas.add(c)
			self._ghosts.append(c)
			
		self._circles = []
		for i in range(numGhosts):
			c = Polygon()
			for corner in [ (-100,0), (0,100), (-100,0), (0,-100) ]:
				c.addPoint(Point(corner[0], corner[1]))
			c.setBorderColor(self._ghostBaseColors[i])
			c.setBorderWidth(.05*self._scale)
			self._circles.append(c)
			self._canvas.add(c)
				
	def movePacman(self, location):
		self._pacman.moveTo((location.x+.5)*self._scale, (location.y+.5)*self._scale)

	def moveGhost(self, ghostId, location):
		if ghostId not in self._caughtGhosts:
			if location == Coordinate(0,0):
				self._ghosts[ghostId].moveTo((len(self._caughtGhosts)+.5)*self._scale, (self._board.getSize()-.5)*self._scale)
				self._caughtGhosts.append(ghostId)
			else:
				self._ghosts[ghostId].moveTo((location.x+.5)*self._scale, (location.y+.5)*self._scale)

	def drawObservations(self, pacmanLocation, observations):
		for ghostId, noisyDistance in enumerate(observations):
			self._circles[ghostId].clearPoints()
			if noisyDistance > 0:
				r = noisyDistance + ghostId/len(observations)
				for corner in [ (1,0), (0,1), (-1,0), (0,-1) ]:
					self._circles[ghostId].addPoint( Point( (pacmanLocation[0]+.5 + r*corner[0])*self._scale, (.5+pacmanLocation[1]+r*corner[1])*self._scale ) )
	
	def updateScoreAndTurn(self, score, turn):
		self._score.setMessage(f'Score: {score}')
		self._turn.setMessage(f'Turn: {turn}')
		
	def identifyGhostType(self, ghostId, ghostType):
		self._ghostType[(ghostId, ghostType)].setBorderColor('white')
		self._ghostType[(ghostId, ghostType)].setBorderWidth(.1*self._scale)
	
	def updateGhostType(self, ghostId, probabilities):
		for t in 'RSCBO':
			self._ghostType[(ghostId, t)].setFillColor( ( int(pow(probabilities[t], intensityPower)*self._ghostBaseColors[ghostId][0]), 
				int(pow(probabilities[t], intensityPower)*self._ghostBaseColors[ghostId][1]), 
				int(pow(probabilities[t], intensityPower)*self._ghostBaseColors[ghostId][2]) ))
				
	def updateGhostPositions(self, probabilityArray):
		for loc in self._board.validLocations():
			colors = [0,0,0]
			for ghostId, probabilities in enumerate(probabilityArray):
				if probabilities is not None:
					prob = pow(probabilities[loc], intensityPower)
					for i in range(3):
						colors[i] += prob*self._ghostBaseColors[ghostId][i]
			for i,c in enumerate(colors):
				colors[i] = min(255, int(c))
			self._squares[loc].setFillColor(tuple(colors))
