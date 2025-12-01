from ParticleFilter import *
from random import *
import sys

numCards = 52
sensorRange = 5
maxMove = 3
steps = int(sys.argv[2])

buzzCorrectly = .9
nobuzzCorrectly = .8

class CardGame:
	def __init__(self):
		self._trueState = randrange(numCards)
		self._direction = ''
		self._buzz = True
		
	def shuffle(self):
		if randint(0,1) == 0:
			self._direction = 'Move from bottom'
			self._trueState = choice(self.moveUp(self._trueState))
		else:
			self._direction = 'Move from top'
			self._trueState = choice(self.moveDown(self._trueState))

	def observe(self):
		if self._trueState < sensorRange:
			self._buzz = True if random() < buzzCorrectly else False
		else:
			self._buzz = True if random() < 1 - nobuzzCorrectly else False
	
	def moveUp(self, state):
		return [ (state-i) % numCards for i in range(1,maxMove) ]
	
	def moveDown(self, state):
		return [ (state+i) % numCards for i in range(1,maxMove) ]
	
	def initialState(self):
		return randrange(numCards)
	
	def possibleMoves(self, currentState):
		if self._direction == 'Move from top':
			return self.moveUp(currentState)
		else:
			return self.moveDown(currentState)
			
	def reweightLikelihood(self, currentState):
		if self._buzz:
			if currentState < sensorRange: return buzzCorrectly
			else: return 1 - nobuzzCorrectly
		else:
			if currentState < sensorRange: return 1 - buzzCorrectly
			else: return nobuzzCorrectly	
			
particles = ParticleFilter()
for i in range(int(sys.argv[1])):
	particles.addParticle(randrange(numCards))
game = CardGame()

for i in range(steps):
	game.shuffle()
	particles.advance(game.possibleMoves)
	
	game.observe()
	particles.reweight(game.reweightLikelihood)
	particles.resample()
	
	mode = particles.mostLikelyParticle()
	probabilities = particles.getParticleProbabilties()
	print(f'Turn {i+1}, true position {game._trueState} ({probabilities.get(game._trueState,0)*100:.2f}%), buzz {game._buzz}, {game._direction}, most likely position {mode} ({probabilities.get(mode,0)*100:.2f}%)')

print()
for k in sorted(list(probabilities.keys())):
	print(f'{k} \t {100*probabilities[k]:4.2f}')
print()
