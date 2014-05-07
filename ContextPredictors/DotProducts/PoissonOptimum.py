'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
from itertools import product as pr

from ContextPredictors.DotProducts.DotProduct1 import DotProduct

class PoissonOptimum(DotProduct):
    name = 'Poisson Optimum'
    
    # This needs to be input for the classifier to compute the
    #  bias properly
    delt_t = None
    
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = self.pos_to_xybin(x,y)
        
        w = self.ws[xbin,ybin,:]
        w0 = self.w0s[xbin,ybin]
        
        cntxt0 = w0+np.dot(w,X[:-2])
        
        # Put between -1 and 1
        cntxt0 /= (np.max(np.abs(self.w0s))+np.max(np.abs(self.ws)))
        cntxt0 = (cntxt0+1)/2.0
        cntxt1 = 1-cntxt0

        try:
            assert (round(cntxt0 + cntxt1,5) in [0,1])
            assert (cntxt0 >= 0 and cntxt0 <= 1)
            assert (cntxt1 >= 0 and cntxt1 <= 1)
        except Exception as e:
            print e
            import pdb; pdb.set_trace()
            raise
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}

    def train(self, X,Y,room, bin_size):
        ''' Generate self.base, where
            base[bin,context,:] is vector of firing rates.
            
            k is the number of points sampled for each population
            vector
            
            delt_t is the total time spanned by a single population
            vector
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-1] is the bin.'''

        super(PoissonOptimum,self).train(X,Y,room, bin_size)
        K = self.delt_t*1.0
        
        self.zero_0 = (self.base[:,:,0,:]==0)
        self.zero_1 = (self.base[:,:,1,:]==0)
        
        self.base[:,:,0,:][self.zero_0] = 1
        self.base[:,:,1,:][self.zero_0] = 1
        self.base[:,:,0,:][self.zero_1] = 1
        self.base[:,:,1,:][self.zero_1] = 1


        self.ws = np.log(1.0*self.base[:,:,0,:]/self.base[:,:,1,:])
        
        self.w0s = np.zeros(self.base.shape[:2])

        bind =  self._bin_indicator(X[:,-2],X[:,-1],self.xblen,self.yblen,bin_size,room)
        for xbin,ybin in pr(range(self.base.shape[0]),range(self.base.shape[1])):
            curid = self.bin_id(xbin,ybin,self.base.shape[1])
            in_bin = np.nonzero(bind==curid)[0]
            Pr0 = np.sum(Y[in_bin]==self.labels[0])
            Pr1 = np.sum(Y[in_bin]==self.labels[1])
            
            if Pr0==0 or Pr1 == 0:
                Pr0 = Pr1 = .5
            rb = self.base[xbin,ybin,1,:]
            ra = self.base[xbin,ybin,0,:]
            self.w0s[xbin,ybin] = ( np.log(1.0*Pr0/Pr1) +np.sum(rb) - np.sum(ra) ) / K


        