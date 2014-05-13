'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from sklearn.decomposition import PCA

from ContextPredictors.DotProducts.DotProduct1 import DotProduct as DP1
from Data.Analysis.Indicators import pos_to_xybin

class DotProduct(DP1):
    name = 'Jezek_PCA'
    PCA_components = 4
    
    def __init__(self, X,Y, room_shape, bin_size):
        self.bin_size=bin_size
        self.room_shape=room_shape
        XLocs = X[:,-1]
        YLocs = X[:,-2]
        # Use PCA
        self.pca = PCA(n_components=self.PCA_components)
        X = self.pca.fit_transform(X[:,:-2])
        super(DotProduct,self).train(X,XLocs, YLocs, Y,room_shape,bin_size)
        
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = pos_to_xybin(x,y)
        
        X = self.pca.transform(X[:-2])
        
        #import pdb; pdb.set_trace()
        cntxt0 = np.dot(self.base[xbin,ybin,0,:],X.T)
        cntxt1 = np.dot(self.base[xbin,ybin,1,:],X.T)
        
        if cntxt0 > cntxt1:
            return {self.labels[0]: 1,
                    self.labels[1]: 0}
        else:
            return {self.labels[0]: 0,
                    self.labels[1]: 1}
        
        # Normalize
        if cntxt0 != 0 or cntxt1 != 0:
            mag = cntxt0+cntxt1
        else:
            mag = 1
        
        cntxt0 /= mag
        cntxt1 /= mag
        
        assert (round(cntxt0 + cntxt1,5) in [0,1])
        
        return {self.labels[0]: cntxt0,
                self.labels[1]: cntxt1}