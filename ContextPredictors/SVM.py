'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
import itertools
from sklearn import svm

from ContextPredictors.Predictor import ContextPredictor
from Data.Analysis.spikeRate import smooth

class SVM(ContextPredictor):
    name = 'SVM'
    
    def __init__(self, X,Y, room_shape, bin_size):
        self.bin_size=bin_size
        self.room_shape=room_shape
        self.train(X,Y,room_shape, bin_size)
        
    def classify(self,X):
        x,y = X[-2:]
        xbin,ybin = pos_to_xybin(x,y)
        
        try:
            svm = self.svms[xbin][ybin]
            guess = svm.predict(np.ravel(X[:-2]))
        except:
            guess = self.svms[xbin][ybin]
        if guess == self.labels[0]:
            return {self.labels[0]: 1,
                    self.labels[1]: 0}
        elif guess == self.labels[1]:
            return {self.labels[0]: 0,
                    self.labels[1]: 1}
        else:
            return {self.labels[0]: .5,
                    self.labels[1]: .5}
    
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
                
                bin_id = bin_id(xbin,ybin,yblen)
                
                indicator[in_bin] = bin_id
        return indicator
    def train(self, X,Y, room, bin_size):
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
        
        self.svms = np.zeros([xblen,yblen]).tolist()
        
        
        self.labels = np.unique(Y)
        
        # Make reverse mappings
        self.l_rev = {self.labels[i]:i for i in range(len(self.labels))}
        
        bind =  self._bin_indicator(X[:,-2],X[:,-1],self.xblen,self.yblen,bin_size,room)
        for cxbin, cybin in itertools.product(range(xblen),range(yblen)):
            cursvm = svm.SVC()
            curid = bin_id(cxbin,cybin,yblen)
            in_bin = np.nonzero(bind==curid)[0]
            if len(in_bin) == 0: continue
            if len(np.unique(Y[in_bin])) < 2:
                #import pdb; pdb.set_trace()
                self.svms[cxbin][cybin] = np.unique(Y[in_bin])
            else:
                cursvm.fit(X[in_bin,:-2],np.ravel(Y[in_bin]))
                self.svms[cxbin][cybin]=cursvm
            

        
                