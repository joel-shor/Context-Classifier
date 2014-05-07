'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging

from ContextPredictors.DotProducts.DotProduct1 import DotProduct

class MultinomialOptimum(DotProduct):
    name = 'Multinomial Optimum Harsh2'
    
    # This needs to be input for the classifier to compute the
    #  bias properly
    delt_t = None
        
    def classify(self,sbin,X):
        if sbin not in self.b_rev:
            return {self.labels[0]: .5,
                    self.labels[1]: .5}
        # Harsh on P0,P1
        '''
        if sbin in self.auto_label: 
            logging.warning('Sbin %i is always decided!',sbin)
            return self.auto_label[sbin]'''
        
        # Harsh on absence of spike
        has_zero_0 = (np.dot(X,self.zero_0[self.b_rev[sbin]]) > 0)
        has_zero_1 = (np.dot(X,self.zero_1[self.b_rev[sbin]]) > 0)  
        if has_zero_0 and not has_zero_1:
            return {self.labels[0]: 0,
                    self.labels[1]: 1}
        elif not has_zero_0 and has_zero_1:
            return {self.labels[0]: 1,
                    self.labels[1]: 0}             
        
        w0 = self.w0s[self.b_rev[sbin]]
        w = self.ws[self.b_rev[sbin],:]
        margin = w0 + np.dot(X,w)
        
        # Scale margin
        tot_wt = np. concatenate([w0,w])
        if np.max(np.abs(tot_wt)) > 0:
            margin /= 2.0*np.max(np.abs(tot_wt))
        
        cntxt0 = (margin+1)/2.0
        cntxt1 = 1-cntxt0
        
        if not (round(cntxt0 + cntxt1,5) in [0,1]):
            print 'problem'
            import pdb; pdb.set_trace()
        
        assert (round(cntxt0 + cntxt1,5) in [0,1])
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}

    def train(self, X,Y):
        ''' Generate self.base, where
            base[bin,context,:] is vector of firing rates.
            
            k is the number of points sampled for each population
            vector
            
            delt_t is the total time spanned by a single population
            vector
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-1] is the bin.'''

        super(MultinomialOptimum,self).train(X,Y)
        K = self.delt_t
        
        # Find zeros
        self.zero_0 = (self.base[:,0,:]==0)
        self.zero_1 = (self.base[:,1,:]==0)
        
        self.base[:,0,:][self.zero_0] = 1
        self.base[:,1,:][self.zero_0] = 1
        self.base[:,0,:][self.zero_1] = 1
        self.base[:,1,:][self.zero_1] = 1

        self.ws = np.log(1.0*self.base[:,0,:]/self.base[:,1,:])
        
        self.w0s = np.zeros([self.base.shape[0],1])

        self.auto_label={}
        for cbin in range(self.base.shape[0]):
            in_bin = (X[:,-1]==cbin)
            Pr0 = np.sum(Y[in_bin]==0)
            Pr1 = np.sum(Y[in_bin]==1)
            
            if Pr0==0 and Pr1!=0:
                self.auto_label[cbin] = {self.labels[0]: 0,
                                         self.labels[1]: 1}
                Pr0=Pr1=.5
            elif Pr0!=0 and Pr1==0:
                self.auto_label[cbin] = {self.labels[0]: 1,
                                         self.labels[1]: 0}
                Pr0=Pr1=.5
            elif Pr0==0 and Pr1==0:
                self.auto_label[cbin] = {self.labels[0]: .5,
                                         self.labels[1]: .5}
                Pr0=Pr1=.5

            
            self.w0s[cbin] = np.log(1.0*Pr0/Pr1)/self.delt_t

        
        