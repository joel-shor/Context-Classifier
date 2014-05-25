'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
from itertools import product

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct
from Analysis.Indicators import bin_id
from Analysis.Indicators import bin_indicator, spk_indicators, bin_id, cell_id, bin_index

class BinomialOptimum2(DotProduct):
    name = 'Binomial2 Opt'
    
    # This needs to be input for the classifier to compute the
    #  bias properly
    delt_t = None
    
    def classify(self,X):
        bin_frac = X[-self.bins:].reshape([self.xblen,self.yblen])
        X = X[:-self.bins]*self.delt_t
        assert np.isclose(np.sum(bin_frac),1)
        assert np.all(X>=0) and np.all(X<=self.delt_t)
        
        #self.base[cell id, lbl, xbin, ybin] = rate
        hyperplane = np.einsum('cxy,c,xy',self.ws,X,bin_frac) + np.sum(self.w0s*bin_frac)
        
        if logging.getLogger().level <= 10:
            tmp0 = 0
            for xbin,ybin in product(range(self.xblen),range(self.yblen)):
                tmp0 += (np.dot(self.ws[:,xbin,ybin],X)+self.w0s[xbin,ybin])*bin_frac[xbin,ybin]
            
            assert np.allclose(tmp0,hyperplane)
        
        if hyperplane>0:
            return {self.labels[0]: 1,
                self.labels[1]: 0}
        else:
            return {self.labels[0]: 0,
                self.labels[1]: 1}

    def train(self, X,Y,room, bin_size):
        ''' Generate self.base, where
            base[bin,context,:] is vector of firing rates.
            
            k is the number of points sampled for each population
            vector
            
            delt_t is the total time spanned by a single population
            vector
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-1] is the bin.'''

        X*=self.delt_t
        super(BinomialOptimum2,self).train(X,Y,room, bin_size)
        #self.base[cell id, lbl, xbin, ybin] = rate
        eps = 10**-10
        self.base[self.base==0]=eps
        self.base[self.base==1]=1-eps

        num = 1.0*self.base[:,0,:,:]*(1-self.base[:,1,:,:])
        denom = 1.0*self.base[:,1,:,:]*(1-self.base[:,0,:,:])
        self.ws = np.log(num/denom)
        
        xbins = self.xblen; ybins = self.yblen
        
        lbl_id0 = np.nonzero(Y==self.labels[0])[0]
        lbl_id1 = np.nonzero(Y==self.labels[1])[0]
        
        self.w0s = np.zeros(self.base.shape[2:])

        dd = np.sum(X[:,-self.bins:],axis=0)
        dd[dd==0]=1

        Pr0 = 1.0*np.sum(X[lbl_id0,-self.bins:],axis=0)/dd
        Pr1 = 1.0*np.sum(X[lbl_id1,-self.bins:],axis=0)/dd
        
        Pr0 = Pr0.reshape([xbins,ybins])
        Pr1 = Pr1.reshape([xbins,ybins])


        tt=np.nonzero(Pr0!=0)
        assert np.allclose(Pr0[tt]+Pr1[tt],1)

        Pr0[Pr0==0]=eps
        Pr1[Pr1==0]=eps
        
        num = 1.0*self.base[:,0,:,:]*(1-self.base[:,1,:,:])
        denom = 1.0*self.base[:,1,:,:]*(1-self.base[:,0,:,:])
        
        num = 1.0*(1-self.base[:,0,:,:])
        denom = 1.0*(1-self.base[:,1,:,:])
        
        
        self.w0s = np.log(Pr0/Pr1)+ self.delt_t * np.sum(num/denom,axis=0)

        