'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
import itertools

from ContextPredictors.Predictor import ContextPredictor
from Data.Analysis.spikeRate import smooth

class DotProduct(ContextPredictor):
    name = 'Jezek'
    
    def __init__(self, X,Y, room_shape, bin_size):
        self.bin_size=bin_size
        self.room_shape=room_shape
        XLocs = X[:,-1]
        YLocs = X[:,-2]
        X = X[:,:-2]
        self.train(X,XLocs,YLocs, Y,room_shape, bin_size)
        
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = self.pos_to_xybin(x,y)
        
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
    
    def bin_id(self,xbin,ybin,y_bin_len):
        return xbin*y_bin_len + ybin + 1
    
    def pos_to_xybin(self,x,y):
        ''' Convert from position to bin coordinates '''
        room_shape=self.room_shape
        bin_size=self.bin_size
        xblen=self.xblen; yblen=self.yblen
        left_edge = room_shape[0][0]
        bottom_edge = room_shape[1][0]
        
        for xbin in range(xblen):
            minx = xbin*bin_size+left_edge
            maxx = (xbin+1)*bin_size+left_edge
            if not (x>=minx)&(x<maxx): continue
            
            for ybin in range(yblen):
                miny = ybin*bin_size+bottom_edge
                maxy = (ybin+1)*bin_size+bottom_edge
                if not (y>=miny)&(y<maxy): continue
                return (xbin,ybin)
        print 'Position not in a bin'
        import pdb; pdb.set_trace()
        raise Exception('Position is not in a bin')
    
    def _bin_indicator(self,x,y,xblen,yblen,bin_size,room_shape):
        indicator = np.zeros([len(x),1])
        left_edge = room_shape[0][0]
        bottom_edge = room_shape[1][0]
        
        for xbin in range(xblen):
            minx = xbin*bin_size+left_edge
            maxx = (xbin+1)*bin_size+left_edge
            in_x_strip = (x>=minx)&(x<maxx)
            
            for ybin in range(yblen):
                miny = ybin*bin_size+bottom_edge
                maxy = (ybin+1)*bin_size+bottom_edge
                in_y_strip = (y>=miny)&(y<maxy)
                
                in_bin = in_x_strip & in_y_strip
                
                bin_id = self.bin_id(xbin,ybin,yblen)
                
                indicator[in_bin] = bin_id
        return indicator
    def train(self, X,XLocs, YLocs, Y, room, bin_size):
        ''' Generate self.base_vec, where
            base_vec[xbin,ybin,context,:] is vector of firing rates.
            
            Assume that X is a [# examples, # cells + 2] array, where
            X[:,-2] is the x loc and X[:,-1] is y loc.
            
            room is [[xmin,xmax],[ymin,ymax]]'''
        assert (room[0][1]-room[0][0])%bin_size==0
        assert (room[1][1]-room[1][0])%bin_size==0
        xblen = (room[0][1]-room[0][0])/bin_size    # x bin length
        yblen = (room[1][1]-room[1][0])/bin_size    # y bin length
        self.xblen=xblen
        self.yblen=yblen
        
        self.labels = np.unique(Y)

        # Make reverse mappings
        self.l_rev = {self.labels[i]:i for i in range(len(self.labels))}
        
        # Find the spikes, the time, and do a smoothing
        spks = np.zeros([xblen,yblen,len(self.labels),X.shape[1]])
        time_spent = np.zeros([xblen,yblen,len(self.labels)])
        
        bin_labels = self._bin_indicator(XLocs,YLocs, xblen,yblen,bin_size, room)

        for cxbin, cybin, label in itertools.product(range(xblen),range(yblen),self.labels):
            correct_label = np.nonzero(Y==label)[0]
            cbin_l = self.bin_id(cxbin, cybin, yblen)
            tm = np.sum(bin_labels[correct_label]==cbin_l)

            time_spent[cxbin,cybin,self.l_rev[label]] = tm

            correct_bin = np.nonzero(bin_labels==cbin_l)[0]
            cur_bin_and_label = np.intersect1d(correct_label,correct_bin)
            
            curX = X[cur_bin_and_label,:]
            cur_spks = np.sum(curX,axis=0)
            
            spks[cxbin,cybin,self.l_rev[label],:] = cur_spks
        
        assert np.all(  (np.sum(X,axis=0) - np.sum(spks,axis=(0,1,2))) < 10**-8)
        
        time_spent[time_spent==0] = np.Inf
        for cell, context in itertools.product(range(spks.shape[3]),
                                               range(len(self.labels))):
            spks[:,:,context,cell] = smooth(spks[:,:,context,cell],bin_size, room)
            spks[:,:,context,cell] /= time_spent[:,:,context]
        
        self.base = spks