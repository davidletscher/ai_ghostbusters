from Ghost import *
from Pacman import *
from Board import *
from Agent import *

import sys, importlib, argparse, time, random, traceback

class Ghostbusters:
	"""
	Manages a game of ghostbusters.
	
	** Member data **
	
	* `_agent` (Agent): the agent instance that makes Pacmans decision
	* `_board` (Board): the game board
	* `_pacman` (Pacman): stores Pacman's current state
	* `_ghosts` (list[GhostState]): the state of each ghost
	* `_informationLevel` (int): how much information to display during each turn (0 = only observations,
		1 = also show predictions, 2 = show actual information)
	* `_timeDelay` (float): time delay (in seconds) at the end of each turn
	* `_graphics`: graphics instance for rendering game or None
	"""
	
	_agent: BaseAgent
	_board: Board
	_pacman: Pacman
	_ghosts: list[GhostState]
	_informationLevel: int
	_timeDelay: float
	
	def __init__(self, pacmanAgentClass, numGhosts: int, timeLimit: float, informationLevel, graphicsSize: int, timeDelay: float):
		"""
		Initialize a new game of Ghostbusters
		"""
		
		self._board = Board()
		self._pacman = Pacman(self._board)
		self._agent = pacmanAgentClass(self._board, self._pacman, numGhosts, timeLimit)
		self._numGhosts = numGhosts
		self._ghosts = [ randomGhost(self._board) for ghostId in range(numGhosts) ]
		self._informationLevel = informationLevel
		self._timeDelay = timeDelay
		
		if graphicsSize > 0:
			self._graphics = GhostbusterGraphics(self._board, self._numGhosts, graphicsSize)
		else:
			self._graphics = None

		
	def play(self) -> int:
		"""
		Play a game of pacman.
		
		** Return value **
		
		The score of the game
		"""
		
		# Play the games
		turn = 0
		gameOver = False
		score = 0

		if self._graphics:
			self._graphics.movePacman(self._pacman.getState().location)
			if self._informationLevel >= 2:
				for ghostId, ghost in enumerate(self._ghosts):
					self._graphics.moveGhost(ghostId, ghost.location)
					self._graphics.identifyGhostType(ghostId, ghost.ghostType)
					
		while turn < 1000 and not gameOver:
			turn += 1
			print(f'Turn {turn}')
			
			# Get noisy distance measurements, update predictions and choose move
			observations = []
			for ghost in self._ghosts:
				if ghost.alive:
					observations.append(self._board.noisyDistance(self._pacman.getState().location, ghost.location))
				else:
					observations.append(0)
					
			print(f'Observed distances {", ".join(str(o) for o in observations)}.')
			if self._graphics:
				self._graphics.drawObservations((self._pacman.getState().location.x, self._pacman.getState().location.y), observations)
			
			if self._timeDelay <= -2:
				input('Hit enter to continue')
			
			# Move Pacman and check if any ghosts are caught
			self._agent._startTime = time.time()
			self._agent.findMove(observations)
			action = self._agent.getMove()
			
			self._pacman.move(action)
			
			print(f'Pacman at {self._pacman.getState().location}, moving {action}')
			
			if self._graphics:
				self._graphics.movePacman(self._pacman.getState().location)
			
			if self._timeDelay <= -2:
				input('Hit enter to continue')
			
			if self._informationLevel >= 1:
				print('Predicted ghost types:')
				for ghostId, ghost in enumerate(self._ghosts):
					if ghost.alive:
						distribution = self._agent.ghostTypeDistribution(ghostId)
						guess = max(distribution, key=distribution.get)
						if self._informationLevel >= 2:
							print(f'\t{guess} ({distribution[guess]*100:.2f}%), actual {ghost.ghostType} ({distribution.get(ghost.ghostType,0)*100:.2f}%)')
						else:
							print(f'\t{guess} ({distribution[guess]*100:.2f}%)')
						
						if self._graphics:
							self._graphics.updateGhostType(ghostId, distribution)
			
			if self._informationLevel >= 1:
				print('Predicted ghost positions:')
				allDistributions = []
				for ghostId, ghost in enumerate(self._ghosts):
					if ghost.alive:
						distribution = self._agent.ghostPositionDistribution(ghostId)
						allDistributions.append(distribution)
						guess = max(distribution, key=distribution.get)
						if self._informationLevel >= 2:
							print(f'\t{guess} ({distribution[guess]*100:.2f})%, actual {ghost.location} ({distribution.get(ghost.location,0)*100:.2f}%)')
						else:
							print(f'\t{guess} ({distribution[guess]*100:.2f})%')
					else:
						allDistributions.append(None)
				
				if self._graphics:
					self._graphics.updateGhostPositions(allDistributions)
			
			
			if self._timeDelay <= -2:
				input('Hit enter to continue')
			
			for ghostId, ghost in enumerate(self._ghosts):
				if ghost.alive and ghost.location == self._pacman.getState().location:
					self._ghosts[ghostId] = GhostState(alive=False, ghostType='', location=Coordinate(0,0), heading='', thinking=False)
					score += 1000
					self._agent.ghostCaught(ghostId)
					
					if self._graphics:
						self._graphics.moveGhost(ghostId, self._ghosts[ghostId].location)
					
					print(f'Ghost {ghostId} caught!')
				else:
					self._agent.ghostNotCaught(ghostId)
			
			# Move ghosts and see if any run into Pacman
			self._ghosts = [ moveGhost(ghost, self._pacman.getState().location, self._board) for ghost in self._ghosts ]
			self._agent.ghostsHaveMoved()
			
			if self._informationLevel >= 2 and self._graphics:
				for ghostId, ghost in enumerate(self._ghosts):
					self._graphics.moveGhost(ghostId, ghost.location)
			
			for ghostId, ghost in enumerate(self._ghosts):
				if ghost.alive and ghost.location == self._pacman.getState().location:
					self._ghosts[ghostId] = GhostState(alive=False, ghostType='', location=Coordinate(0,0), heading='', thinking=False)
					score += 1000
					self._agent.ghostCaught(ghostId)
					if self._graphics:
						self._graphics.moveGhost(ghostId, self._ghosts[ghostId].location)
					print(f'Ghost {ghostId} ran into Pacman')
				else:
					self._agent.ghostNotCaught(ghostId)
					
			if self._timeDelay <= -2:
				input('Hit enter to continue')
			
			# Update scores
			gameOver = True
			for ghost in self._ghosts:
				if ghost.alive:
					score -= 1
					gameOver = False
					
			print(f'Score is {score}.')
			print()
			print(self)
			print()
			
			if self._graphics:
				self._graphics.updateScoreAndTurn(score, turn)
				
			if self._timeDelay >= 0:
				time.sleep(self._timeDelay)
			else:
				input('Hit enter to continue')
		
		if self._graphics:
			self._graphics.movePacman(self._pacman.getState().location)
		
		return score
					
	def __str__(self):
		"""Represent the current board state as text."""
		
		s = ''
		for y in range(self._board.getSize()):
			for x, entry in enumerate(self._board._map[y]):
				if entry == 'W':
					s += 'W'
				elif self._pacman.getState().location == Coordinate(x,y):
					s += 'P'
				elif Coordinate(x,y) in [ g.location for g in self._ghosts if g.alive ] and self._informationLevel >= 2:
					s += 'G'
				else:
					s += ' '
			s += '\n'
		return s

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description ='Play Ghostbusters')
	parser.add_argument('agent', type=str)
	parser.add_argument('num_ghosts', type=int, help="number of ghosts in the game")
	parser.add_argument('time_limit', type=float, help="time to make a move")
	parser.add_argument('information_level', type=int, help="0=only show observations, 1 also show predictions and 2 show everything")
	parser.add_argument('-g', type=int, help="size of graphics window")
	parser.add_argument('-t', type=float, help="time delay")
	args = parser.parse_args()

	try:
		agentModule = importlib.import_module(args.agent.split('.')[0])
	except ModuleNotFoundError:
		print('Invalid agent module name')
		sys.exit()
	except Exception as e:
		traceback.print_exc()
		sys.exit()

	if args.g:
		from Graphics import *
		graphicsSize = args.g
	else:
		graphicsSize = 0
		
	if args.t:
		timeDelay = args.t
	else:
		timeDelay = 0.
		
	game = Ghostbusters(agentModule.MyAgent, args.num_ghosts, args.time_limit, args.information_level, graphicsSize, timeDelay)
	game.play()
