'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging

from ContextPredictors.Predictor import ContextPredictor
from Data.Analysis.spikeRate import rates_from_pv
from Data.Analysis.Indicators import pos_to_xybin

class DotProduct(ContextPredictor):
    name = 'Jezek'
    
    def __init__(self, X,Y, room, bin_size):
        assert (room[0][1]-room[0][0])%bin_size == 0
        assert (room[1][1]-room[1][0])%bin_size == 0
        self.bin_size=bin_size
        self.room=room
        self.xblen = (room[0][1]-room[0][0])/bin_size
        self.yblen = (room[1][1]-room[1][0])/bin_size
        self.bins = self.xblen*self.yblen
        self.labels = np.unique(Y)
        
        
        # This is if X = [cell1, cell2, ..., celln, binfrac1,...,binfrac k^2]
        self.train(X,Y,room, bin_size)
        
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = pos_to_xybin(x,y, self.xblen,self.yblen,self.bin_size,self.room)

        cntxt0 = np.dot(self.base[xbin,ybin,0,:],X[:-2])
        cntxt1 = np.dot(self.base[xbin,ybin,1,:],X[:-2])

        
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
    
    def train(self, X, Y, room, bin_size):
        ''' Generate self.base_vec, where
            base_vec[xbin,ybin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-2] is the x loc and X[:,-1] is y loc.
            
            room is [[xmin,xmax],[ymin,ymax]]'''
        assert (room[0][1]-room[0][0])%bin_size==0
        assert (room[1][1]-room[1][0])%bin_size==0
        
        # rates[cell id, lbl, xbin, ybin] = rate
        rates = rates_from_pv(X,Y,bin_size,room)
        
        # Pass the rates stuff to draw before reorder indices
        if logging.getLogger().level == logging.INFO:
            import matplotlib.pyplot as plt
            from GenerateFigures.rateGraphLib import plot_rates
            fake_t_cells = {(-1,k):0 for k in range(rates.shape[0])}
            plot_rates(rates,Y,fake_t_cells)
            plt.show()
        
        # format it better
        # rates[xbin, lbl, cell id, ybin] = rate
        rates = np.swapaxes(rates, 0, 2)
        
        # rates[xbin, ybin, cell id, lbl] = rate
        rates = np.swapaxes(rates, 1, 3)
        
        # rates[xbin, ybin, lbl, cell id] = rate
        self.base = np.swapaxes(rates, 2, 3)
        
        
