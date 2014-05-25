'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct

class DotProduct(DotProduct):
    name = 'Mean normalized'
    
    def train(self, X, Y, room, bin_size):
        ''' Generate self.base_vec, where
            base_vec[xbin,ybin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-2] is the x loc and X[:,-1] is y loc.
            
            room is [[xmin,xmax],[ymin,ymax]]'''
        super(DotProduct,self).train(X, Y,room,bin_size)
        #self.base[cell id, lbl, xbin, ybin] = rate
        means = 1.0*np.mean(self.base,axis=1)
        means[means==0] = 1 # If it's 0, then it doesn't matter anyways
        for i in range(self.base.shape[1]):
            self.base[:,i,:,:] = self.base[:,i,:,:]/means
        