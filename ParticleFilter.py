from collections import defaultdict
import random
import numpy.random

rng = numpy.random.default_rng()

class ParticleFilter:
	"""
	Manage particle filtering to estimate states in an HMM.
	
	**Member Data**
	
	* `_numParticles` (int): the number of particles present in the particle filter.
	* `_particleWeight` (dict): a dictionary from a particle to the number of times the 
		particle is present.  As long as the particle filter does not need reweighting
		these values will be intergers.
		
	The typical workflow of this class is:
	
	* Call addParticle for each new particle to create.
	
	* Update the states of the particles using a call to advance.  This
		moves each particle to its next state.
		
	* Call reweight to update the weights of each particle so they add up to 1.
	
	* Call resample, to get a new sample of particles.
	
	* Repeat starting at step 2 as necessary.
	"""
	
	def __init__(self):
		"""Initialize the particle filter with no particles."""
		self._numParticles = 0
		self._particleWeight = defaultdict(float)
		
	def addParticle(self, particle):
		"""
		Add a new particle to the system.
		
		**Parameters**
		
		* `particle`: an immutable representation of a single particle.
		"""
		
		self._numParticles += 1
		self._particleWeight[particle] += 1

	def resample(self):
		"""
		Create a new sample of particles.
		
		It creates `_numParticles` particles using the weights in the
		current particle sample.  
		"""
		
		particles = []
		weights = []
		factor = 1./sum(self._particleWeight.values())
		for (particle, weight) in self._particleWeight.items():
			particles.append(particle)
			weights.append(weight*factor)
		
		newWeight = defaultdict(float)
		
		for (particleId, count) in enumerate(rng.multinomial(self._numParticles, weights)):
			newWeight[particles[particleId]] = count
			
		self._particleWeight = newWeight
		
	def advance(self, possibleMoves):
		"""
		Move each particle using the provided possibleMoves function.
		
		**Parameters**
		
		* `possibleMoves`: a function that takes a particle as input and gives a list of possible next states of that particle.
		
		Precondition, the particle weights are all integers.  For example, this is called after a resample.
		"""
		
		newParticles = defaultdict(float)
		for (particle, count) in self._particleWeight.items():
			count = int(round(count))
			possibleResults = possibleMoves(particle)
			for repeat in range(count):
				result = random.choice(possibleResults)
				newParticles[result] += 1
			self._particleWeight = newParticles
		
	def reweight(self, likelihood):
		"""
		Reweight the particles based on the likelihood of them matching the current observations.
		
		**Parameters**
		
		* `likelyhood`: a function that gives a likelyhood (0 to 1) of how consistent the particles state is with the observations.
		"""
		
		self._particleWeight = { particle : currentWeight * likelihood(particle) for (particle, currentWeight) in self._particleWeight.items() }

	def getParticleProbabilties(self):
		"""
		Return a dictionary of the probability of each particle occuring in the system.
		"""
		
		probabilities = defaultdict(float)
		for (particle, count) in self._particleWeight.items():
			probabilities[particle] = count/self._numParticles
		return probabilities
		
	def mostLikelyParticle(self):
		"""
		Return the particle whose copies occur most often in the system.
		
		In there are multiple particles with the same count, then one is
		choosen at random.
		"""
		
		maxProb = 0.
		mostLikely = []
		for (particle, count) in self._particleWeight.items():
			prob = count/self._numParticles
			if prob > maxProb:
				maxProb = prob
				mostLikely = [particle]
			elif prob == maxProb:
				mostLikely.append(particle)
				
		return random.choice(mostLikely)
