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
    name = 'DP Profile 1'
    
    def __init__(self, X,Y, room_shape, bin_size):
        self.bin_size=bin_size
        self.room_shape=room_shape
        self.train(X,Y,room_shape, bin_size)
        
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
        
        
        self.labels = np.unique(Y)
        
        # Make reverse mappings
        self.l_rev = {self.labels[i]:i for i in range(len(self.labels))}
        
        # Find the spikes, the time, and do a smoothing
        spks = np.zeros([xblen,yblen,len(self.labels),X.shape[1]-2])
        spks2 = np.zeros([xblen,yblen,len(self.labels),X.shape[1]-2])
        time_spent = np.zeros([xblen,yblen,len(self.labels)])
        
        bin_labels = self._bin_indicator(X[:,-2],X[:,-1],
                                         xblen,yblen,bin_size, room)
        #import pdb; pdb.set_trace()
        for cxbin, cybin, label in itertools.product(range(xblen),range(yblen),self.labels):
            iss1 = np.nonzero(Y==label)[0]
            cbin_l = self.bin_id(cxbin, cybin, yblen)
            tm = np.sum(bin_labels[iss1]==cbin_l)
            #print 'time spent in (%i,%i)=%i'%(cxbin,cybin,tm)
            time_spent[cxbin,cybin,self.l_rev[label]] = tm
            #print cxbin,cybin,label,tm, time_spent[cxbin,cybin,self.l_rev[label]]
            iss2 = np.nonzero(bin_labels==cbin_l)[0]
            iss3 = np.intersect1d(iss1,iss2)
            
            curX = X[iss3,:-2]
            cur_spks = np.sum(curX,axis=0)
            #print cxbin,cybin,label,tm,cur_spks
            #if tm != 0 and cur_spks!=0:
            #    import pdb; pdb.set_trace()
            
            
            spks[cxbin,cybin,self.l_rev[label],:] = cur_spks
        
        try:
            assert np.all(  (np.sum(X[:,:-2],axis=0) - np.sum(spks,axis=(0,1,2))) < 10**-8)
        except:
            import pdb; pdb.set_trace()
            raise
        
        #import matplotlib.pyplot as plt
        '''
        import pdb; pdb.set_trace()
        plt.figure()
        plt.pcolor(time_spent[:,:,0])
        for cntxt in range(len(self.labels)):
            time_spent[:,:,cntxt] = smooth(time_spent[:,:,cntxt],bin_size, room)
        plt.figure()
        plt.pcolor(time_spent[:,:,0])
        plt.show()
        
        for i in range(3):
            plt.figure()
            plt.pcolor(spks[:,:,0,i])
        plt.show()'''
        
        time_spent[time_spent==0] = np.Inf
        for cell, context in itertools.product(range(spks.shape[3]),
                                               range(len(self.labels))):
            '''if np.sum(spks[:,:,context,cell]) !=0:
                plt.figure()
                plt.pcolor(spks[:,:,context,cell])'''
            spks[:,:,context,cell] = smooth(spks[:,:,context,cell],bin_size, room)
            '''if np.sum(spks[:,:,context,cell]) !=0:
                plt.figure()
                plt.pcolor(spks[:,:,context,cell])
                plt.show()'''
            
            spks[:,:,context,cell] /= time_spent[:,:,context]
        
        self.base = spks
            

        
                