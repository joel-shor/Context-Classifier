'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
import itertools

from ContextPredictors.Predictor import ContextPredictor

class DotProduct(ContextPredictor):
    name = 'DP Profile 1'
    
    def __init__(self, X,Y):
        self.train(X,Y)
        
    def classify(self,sbin,X):
        cntxt0 = np.dot(self.base[self.b_rev[sbin],0,:],X)
        cntxt1 = np.dot(self.base[self.b_rev[sbin],1,:],X)
        
        # Normalize
        if cntxt0 != 0 or cntxt1 != 0:
            mag = cntxt0+cntxt1
        else:
            mag = 1
        
        cntxt0 /= mag
        cntxt1 /= mag
        
        if not (round(cntxt0 + cntxt1,5) in [0,1]):
            import pdb; pdb.set_trace()
        
        assert (round(cntxt0 + cntxt1,5) in [0,1])
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}
    
    def train(self, X,Y):
        ''' Generate self.base_vec, where
            base_vec[bin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 1] array, where
            X[:,-1] is the bin.'''

        self.bins = np.unique(X[:,-1])
        self.labels = np.unique(Y)
        base = np.zeros([len(self.bins),len(self.labels),X.shape[1]-1])
        
        # Make reverse mappings
        self.b_rev = {self.bins[i]:i  for i in range(len(self.bins))}
        self.l_rev = {self.labels[i]:i for i in range(len(self.labels))}
        
        for sbin, label in itertools.product(self.bins,self.labels):
            cur_i = (X[:,-1]==sbin)&(Y.reshape([-1])==label)
            if not np.any(cur_i):
                mean_vec = 0
            else:
                mean_vec = np.mean(X[cur_i,:-1],axis=0)
            if np.any(np.isnan(mean_vec)):
                import pdb; pdb.set_trace()
            base[self.b_rev[sbin],self.l_rev[label],:] = mean_vec
        self.base = base
                