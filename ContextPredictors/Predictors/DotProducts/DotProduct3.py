'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
from itertools import product

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct

class DotProduct(DotProduct):
    name = 'Normalized'
    
    def classify(self,X):
        
        bin_frac = X[-self.bins:].reshape([self.xblen,self.yblen])
        X = X[:-self.bins]
        
        def _t(xbin,ybin,lbl):
            return np.sum( (X-self.means[:,xbin,ybin])*
                              bin_frac[xbin,ybin] *
                              self.base[:,lbl,xbin,ybin]     )
        
        cntxt0 = np.sum([_t(xbin,ybin,0) for xbin,ybin in product(range(self.xblen),range(self.yblen))])
        cntxt1 = np.sum([_t(xbin,ybin,1) for xbin,ybin in product(range(self.xblen),range(self.yblen))])

        if cntxt0 > cntxt1:
            return {self.labels[0]: 1,
                self.labels[1]: 0}
        else:
            return {self.labels[0]: 0,
                self.labels[1]: 1}
    
    def train(self, X, Y, room, bin_size):
        ''' Generate self.base_vec, where
            base_vec[xbin,ybin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-2] is the x loc and X[:,-1] is y loc.
            
            room is [[xmin,xmax],[ymin,ymax]]'''

        super(DotProduct,self).train(X, Y,room,bin_size)
        #self.base[cell id, lbl, xbin, ybin] = rate
        self.means = 1.0*np.mean(self.base,axis=1)
        stddev = 1.0 * np.std(self.base,axis=1)
        stddev[stddev==0]=1
        
        for lbl in range(self.base.shape[1]):
            self.base[:,lbl,:,:] = (self.base[:,lbl,:,:]-self.means)/np.power(stddev,2)