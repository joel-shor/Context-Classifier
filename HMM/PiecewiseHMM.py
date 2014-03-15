'''

'''

import numpy as np
from sklearn.hmm import GaussianHMM
import logging

POS_PTS_PER_CELL = 1000.0
SIZE_OF_CELL = 0
NONE = -1

class PiecewiseHMM:
	''' A hidden markov model that calculates the state
		of a sequence of x,y,waveform triples. There are a number of
		models for each sector of the physical environment.
	'''
	def __init__(self,xs,ys,wave_l, actual_classification,split_method='Num'):
		self.xs = xs; self.ys = ys
		self.wave_l = wave_l; self.actual_classification = actual_classification
		
		# Should we split the physical domain by number or sectors or size of sectors
		if split_method == 'Num':
			self.cll_p_sd = int(np.sqrt(len(xs)/POS_PTS_PER_CELL))
		elif split_method == 'Size':
			self.cll_p_sd = int((np.max(xs)-np.min(xs))/SIZE_OF_CELL)
		logging.info('Cells per size: %d', self.cll_p_sd)
		
		self.xrange = [np.min(xs), np.max(xs)]
		self.yrange = [np.min(ys), np.max(ys)]
		self.dx = 1.0*(np.max(xs)-np.min(xs))/self.cll_p_sd
		self.dy = 1.0*(np.max(ys)-np.min(ys))/self.cll_p_sd

		# Makes a dictionary of time points where the animal is in
		#  sector i
		self.sectorize = self._get_sector(np.array(xs), np.array(ys))
		segments = {}
		for i in range(self.cll_p_sd**2):
			segments[i] = self._split_into_chunks(self.sectorize, i)
		
		# self.HMMs is an array of the HMMs for sector i
		self.HMMs = [None]*self.cll_p_sd**2
		for i in range(self.cll_p_sd**2):
			observation_l = []
			for seg in segments[i]:
				if len(seg) <= 1 or np.std(wave_l[seg]) == 0: 
					continue

				observation_l.append(wave_l[seg].reshape(-1,1) 		 )
			#observations = np.array(wave_l[x] for x in )
			# make an HMM instance and execute fit
			
			if len(observation_l) == 0:
				logging.warning('Sector %i had not enough data',i)
				continue
			
			logprobs = []
			models = []
			for n_components in range(2,5):
				model = GaussianHMM(n_components, covariance_type="diag", n_iter=1000)
	
				try:
					model.fit(observation_l)
				except:
					logging.warning('Busted on training %i', i)
					continue
				#import pdb; pdb.set_trace()
				tots_prob = np.sum(model.score(obs)*len(obs) for obs in observation_l)
				logprobs.append(tots_prob)
				models.append(model)
				
			if models == []: continue
			model = models[np.argmax(logprobs)]

			states = self._what_do_states_mean(model)
			self.HMMs[i] = (states, model)
	
	def _what_do_states_mean(self, model):
		m = model.means_
		states = {}
		for i in range(len(m)):
			if -.1 < m[i] and m[i] < .1:
				states[i] = -1
			elif m[i] > .1:
				states[i] = 1
			else:
				states[i] = 0
		return states
	
	def _which_state_is_clockwise(self, observations,model,actual):
		count = np.sum(model.predict(observations.reshape([-1,1]))-actual)
		
		if count < len(actual)/2.0: return 1
		else: return 0
	
	def make_predictions(self):
		self.predictions = np.array([NONE]*len(self.xs))
		chunk_l = []
		for i in range(self.cll_p_sd**2):
			chunk_l.extend([np.append(chunk,i) for chunk in self._split_into_chunks(self.sectorize, i)])
		chunk_l.sort(key=lambda x: x[0])
		
		
		logging.info('Predicting hidden states...')
		prob = np.array([.5,.5])
		for chunk in chunk_l:
			sector = chunk[-1]
			try:
				states, hmm = self.HMMs[sector]
			except:
				prob = np.array([.5,.5])
				self.predictions[chunk[:-1]] = [NONE] * (len(chunk)-1)
				continue
			
			hmm.startprob_ = prob
			pred = hmm.predict(self.wave_l[chunk[:-1]].reshape([-1,1]))
			
			for i in states:
				self.predictions[chunk[pred == i]] = states[i]

			prob = hmm.predict_proba(chunk[:-1].reshape([-1,1]))[-1]
	
	def print_perc_correct(self):
		''' This is going to cheat and look into the future. '''
		logging.info('Checking HMMs accuracy...')
		
		tot = len(self.predictions)
		nones = np.sum(self.predictions == NONE)
		crct = np.sum((self.predictions-self.actual_classification)==0)
		crct_wout_zero = np.sum(np.logical_and((self.predictions-self.actual_classification) ==0, 
												self.wave_l != 0))
		tot_wout_zero = np.sum(np.logical_and(self.predictions != NONE,
												self.wave_l != 0))
		
		print '%35s %i/%5i = %.3f'%('Total correct:',crct,tot,1.0*crct/tot)
		print '%35s %i/%5i = %.3f'%('Tot correct w/out nones:',crct,tot-nones,1.0*crct/(tot-nones))
		print '%35s %i/%5i = %.3f'%('Correct w/out nones or 0 waveform:',crct_wout_zero,tot_wout_zero, 1.0*crct_wout_zero/tot_wout_zero)
	
	def _split_into_chunks(self,arr, itm):
		''' Returns the indices of the points where the animal is
			in sector itm. '''
		chunks = []
		a = (np.array(arr) == itm)
		b = np.append(a,a[-1])
	
		end = np.nonzero(np.logical_and(a,np.diff(b) != 0))[0]
		beginning = np.nonzero(np.logical_and(a!= True,np.diff(b) != 0))[0]
		
		if len(end) > 0 and len(beginning) > 0 and end[0] < beginning[0]:
			chunks.append(range(end[0]+1))
			end = end[1:]
		if len(end) > 0 and len(beginning) > 0 and end[-1] < beginning[-1]:
			chunks.append(range(beginning[-1]+1,len(arr)))
			beginning = beginning[:-1]
		
		if len(end) != len(beginning):
			import pdb; pdb.set_trace()
			raise Exception('Somewhere over the rainbox')
		
		
		for start, stop in zip(beginning,end):
			chunks.append(range(start+1,stop+1))
		
		return chunks
	
	def _get_sector(self,x,y):
		''' Gets the index of the grid sector that the point (x,y)
			falls in.'''
		x_sec = (x-self.xrange[0])/self.dx

		y_sec = (y-self.yrange[0])/self.dy

		return x_sec.astype(int) + y_sec.astype(int)*self.cll_p_sd
	