'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct

class DotProduct(DotProduct):
    name = 'Mean normalized (before)'
    
    def classify(self,X):
        bin_frac = X[-self.bins:].reshape([self.xblen,self.yblen])
        X = X[:-self.bins]/self.means
        
        #self.base[cell id, lbl, xbin, ybin] = rate
        cntxt0 = np.einsum('cxy,c,xy',self.base[:,0,:,:],X,bin_frac)
        cntxt1 = np.einsum('cxy,c,xy',self.base[:,1,:,:],X,bin_frac)
        
        if logging.getLogger().level <= 5:
            tmp0 = 0
            for cell in range(len(X)):
                tmp0 += np.sum(X[cell]*bin_frac*self.base[cell,0,:,:])
            
            tmp1 = 0
            for cell in range(len(X)):
                tmp1 += np.sum(X[cell]*bin_frac*self.base[cell,1,:,:])
            
            assert np.allclose(tmp0,cntxt0)
            assert np.allclose(tmp1,cntxt1)
        
        #import pdb; pdb.set_trace()
        
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
        self.means = 1.0*np.mean(X[:,:-self.bins],axis=0)
        self.means[self.means==0]=1
        for i in range(X.shape[0]):
            X[i,:-self.bins] /= self.means

        super(DotProduct,self).train(X, Y,room,bin_size)
        
        