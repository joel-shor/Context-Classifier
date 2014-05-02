'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging

from ContextPredictors.DotProducts.DotProduct1 import DotProduct

class MultinomialOptimum(DotProduct):
    name = 'Multinomial Optimum'
    
    # This needs to be input for the classifier to compute the
    #  bias properly
    delt_t = None
        
    def classify(self,sbin,X):
        
        # First check if there are any spikes in cells that didn't appear
        #  in the training data
        not_in_0 = np.sum(X[self.zero_i0[sbin,:]])>0
        not_in_1 = np.sum(X[self.zero_i1[sbin,:]])>0
        
        if not_in_0 and not not_in_1:
            logging.warning('Definitely is not in context 0')
            return {self.labels[0]: 0,
                self.labels[1]: 1}
        elif not_in_1 and not not_in_0:
            logging.warning('Definitely not in context 1')
            return {self.labels[0]: 1,
                self.labels[1]: 0}
        
        margin = self.w0s[sbin] + np.dot(X,self.ws[sbin,:])
        
        cntxt0 = (margin+1)/2.0
        cntxt1 = 1-cntxt0
        
        assert (round(cntxt0 + cntxt1,5) in [0,1])
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}
    
    def train(self, X,Y, k, delt_t):
        ''' Generate self.base_vec, where
            base_vec[bin,context,:] is vector of firing rates.
            
            k is the number of points sampled for each population
            vector
            
            delt_t is the total time spanned by a single population
            vector
            
            Assume that X is a [# examples, # cells + 1] array, where
            X[:,-1] is the bin.'''
        
        super(DotProduct,self).train(X,Y)
        # What happens if the base firing rate for a particular cell
        #  is 0? We want to make sure things don't blow up
        self.zero_i0 = (self.base_vec[:,0,:] == 0)
        self.zero_i1 = (self.base_vec[:,1,:]==0)
        
        self.base_vec[:,0,:][self.zero_i0] = 1
        self.base_vec[:,1,:][self.zero_i1] = 1


        self.ws = np.log(1.0*self.base_vec[:,0,:]/self.base_vec[:,1,:])
        
        self.w0s = np.zeros([self.base_vec.shape[0],1])
        for cbin in range(self.base_vec.shape[0]):
            in_bin = (X[:,-1]==cbin)
            Pr0 = np.sum(Y[in_bin]==0)
            Pr1 = np.sum(Y[in_bin]==1)
            self.w0s[bin] = np.log(1.0*Pr0/Pr1)/self.delt_t
        