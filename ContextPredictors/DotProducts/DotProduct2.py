'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
import itertools

from ContextPredictors.DotProducts.DotProduct1 import DotProduct

class DotProduct(DotProduct):
    name = 'DP Profile 2'
    
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = self.pos_to_xybin(x,y)
        
        cntxt0 = np.dot(self.base[xbin,ybin,0,:]/self.means,X[:-2]/self.means)
        cntxt1 = np.dot(self.base[xbin,ybin,1,:]/self.means,X[:-2]/self.means)
        
        # Normalize
        if cntxt0 != 0 or cntxt1 != 0:
            mag = cntxt0+cntxt1
        else:
            mag = 1
        
        cntxt0 /= mag
        cntxt1 /= mag
        
        if not (round(cntxt0 + cntxt1,5) in [0,1]):
            import pdb; pdb.set_trace()
            raise Exception()
        
        assert (round(cntxt0 + cntxt1,5) in [0,1])
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}
    
    def train(self, X,XLocs, YLocs, Y, room, bin_size):
        ''' Generate self.base_vec, where
            base_vec[xbin,ybin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-2] is the x loc and X[:,-1] is y loc.
            
            room is [[xmin,xmax],[ymin,ymax]]'''

        super(DotProduct,self).train(X,XLocs, YLocs, Y,room,bin_size)
        self.means = np.mean(X,axis=0)
        self.means[self.means==0] = 1 # If it's 0, then it doesn't matter anyways