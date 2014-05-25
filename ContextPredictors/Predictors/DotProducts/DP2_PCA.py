'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from sklearn.decomposition import PCA
import logging

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct

class DotProduct(DotProduct):
    name = 'DP Profile 2 w PCA'
    
    PCA_components = 15
    
    def __init__(self, X,Y, room, bin_size):
        assert (room[0][1]-room[0][0])%bin_size == 0
        assert (room[1][1]-room[1][0])%bin_size == 0
        self.bin_size=bin_size
        self.room=room
        self.xblen = (room[0][1]-room[0][0])/bin_size
        self.yblen = (room[1][1]-room[1][0])/bin_size
        self.bins = self.xblen*self.yblen
        self.labels = np.unique(Y)
        
        newX = np.zeros([X.shape[0],self.PCA_components+self.bins])
        newX[:,-self.bins:] = X[:,-self.bins:]
        
        self.pca = PCA(n_components=self.PCA_components)
        newX[:,:self.PCA_components] = self.pca.fit_transform(X[:,:-self.bins])
        
        # This is if X = [cell1, cell2, ..., celln, binfrac1,...,binfrac k^2]
        self.train(newX,Y,room, bin_size)
    def classify(self,X):
        bin_frac = X[-self.bins:].reshape([self.xblen,self.yblen])
        X = X[:-self.bins]
        
        X = np.squeeze(self.pca.transform(X))

        
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

        super(DotProduct,self).train(X, Y,room,bin_size)
        #self.base[cell id, lbl, xbin, ybin] = rate
        means = 1.0*np.mean(self.base,axis=1)
        means[means==0] = 1 # If it's 0, then it doesn't matter anyways
        for i in range(self.base.shape[1]):
            self.base[:,i,:,:] = self.base[:,i,:,:]/means
        