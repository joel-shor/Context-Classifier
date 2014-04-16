'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
from itertools import product as pr

from Predictor import ContextPredictor
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate

class DotProduct(ContextPredictor):
    time_per_vl_pt = .02 #(seconds)
    good_clusters = {1:range(2,8),
                     2:range(2,8),
                     3:range(2,14),
                     4:range(2,7),
                     5:range(2,12),
                     6:[2],
                     7:[2,3,4],
                     11:[2],
                     12:[2,3]}
    
    def __init__(self, vl, cls,trigger_tm,label_is, room_shape=[[-60,60],[-60,60]], bin_size=8):
        self.vl = vl
        self.cls = cls  # A dictionary of {tetrode: [cluster1,cluster2,...]}
        self.room_shape = room_shape
        self.bin_size = bin_size
        self.xbins = (self.room_shape[0][1]-self.room_shape[0][0])/self.bin_size
        self.ybins = (self.room_shape[1][1]-self.room_shape[1][0])/self.bin_size
        self.labels = label_is.keys()
        self.reverse_lbs = {lbl:i for i,lbl in zip(range(len(self.labels)),self.labels)}
        
        # base_vec[x grid cell, y grid cell, context, cell number]
        # t_cells = [(tetrode, cluster label)]
        # t_cells_spks = [spk_is, spk_is,...]
        self.base_vec, self.t_cells = self._calculate_base_vectors(label_is, trigger_tm)
    
    def generate_population_vectors(self):
        ''' Return two dictionaries: One with the population vectors, the other
            with the labels.
            
            Xs[(xbin,ybin)] = [vec1,vec2,...]
            Ys[(xbin,ybin)] = [lbl1,lbl2,...] '''
        # Slice by time in a particular bin
        Xs = {}
        Ys = {}
        pts_accounted_for = 0
        for x in range(self.xbins):
            xmin = self.room_shape[0][0]+x*self.bin_size
            xmax = self.room_shape[0][0]+(x+1)*self.bin_size
            in_x_strip = (self.vl['xs'] >= xmin) & (self.vl['xs'] < xmax)
            for y in range(self.ybins):
                logging.info('Generating population vector for bin (%i,%i) of %i',x,y, self.xbins)
                ymin = self.room_shape[1][0]+y*self.bin_size
                ymax = self.room_shape[1][0]+(y+1)*self.bin_size
                in_y_strip = (self.vl['ys'] >= ymin) & (self.vl['ys'] < ymax)
                
                in_sqr = in_x_strip & in_y_strip
                start_i = 1+np.nonzero(in_sqr[1:]>in_sqr[:-1])[0]
                end_i = 1+np.nonzero(in_sqr[:-1]>in_sqr[1:])[0]
                
                if in_sqr[0] == 1: start_i = np.concatenate([[0],start_i])
                if in_sqr[-1] == 1: end_i = np.concatenate([end_i,[len(in_sqr)]])
                
                if len(start_i) != len(end_i): 
                    raise Exception('Indices don\'t align')

                Xs[(x,y)] = np.zeros([len(start_i),len(self.t_cells)])
                Ys[(x,y)] = np.zeros([len(start_i),1])

                for st, end, k in zip(start_i,end_i,range(len(start_i))):
                    tm = self.time_per_vl_pt*(end-st)
                    rate_vec = np.array([np.sum((spks>=st) & (spks<end))/tm for spks in self.t_cells.values()])
                    
                    #Normalize
                    
                    nm = np.linalg.norm(rate_vec)
                    if nm != 0:
                        rate_vec /= nm
                    
                    Xs[(x,y)][k,:] = rate_vec
                    try:
                        Ys[(x,y)][k] = self.reverse_lbls[np.sign(np.sum(self.vl['Task'][st:end]))]
                    except:
                        Ys[(x,y)][k] = np.random.random_integers(0,1)
                    pts_accounted_for += end-st
        if pts_accounted_for != len(self.vl['xs']):
            raise Exception('Some points went missing in ')
        return Xs, Ys
    
    
    def classifiy(self,xbin,ybin,X):
        cntxt0 = np.dot(self.base_vec[xbin,ybin,0,:]/self.means[0],X/self.means[0])
        cntxt1 = np.dot(self.base_vec[xbin,ybin,1,:]/self.means[1],X/self.means[1])    
        
        return (cntxt0, cntxt1)
    
    def _calculate_base_vectors(self, label_is, trigger_tm):
        
        # Find the firing rates of each cell in each context. This must be done
        #  before we can put them in an array so we know how many cells we actually
        #  have.
        rates = {}    # A dict of firing rates
        t_cells = {}  # A dict of cells that are included in the baseline in the form
                            #  {(tetrode, cluster): spk_i}
        for tetrode,cl in self.cls.items():
            if tetrode not in self.good_clusters: continue
            for cell in self.good_clusters[tetrode]:
                logging.info('Finding spike locations for tetrode %i, cell %i',tetrode,cell)
                spk_i = spike_loc(cl, self.vl, trigger_tm, cell)
                if spk_i is np.NAN: break
                t_cells[(tetrode,cell)] = spk_i
                rates[(tetrode,cell)] = {}
                for context,context_i in label_is.items():
                    spks_in_context = np.intersect1d(spk_i, context_i)
                    rate = spike_rate(self.room_shape,self.vl,spks_in_context,self.bin_size,valid=context_i)
                    logging.info('Processed firing rates for tetrode %i, cell %i, context %i',tetrode,cell,context)
                    rates[(tetrode,cell)][context]=rate
        
        if len(rates) != len(t_cells): raise Exception('Length of arrays not right.')
        
        # Put the firing rates from  the rates array in a matrix

        # Final matrix structure
        base_vec = np.zeros([self.xbins,self.ybins,len(self.labels),len(rates)])
        
        for key, cell in zip(t_cells.keys(),range(len(t_cells))):
            for cntxt, rate in rates[key].items():
                base_vec[:,:,self.reverse_lbs[cntxt],cell] = rate
        
        # Calculate mean vector
        self.means = np.zeros([len(self.labels),len(t_cells)])
        for lbl, cell in pr(range(base_vec.shape[2]),range(base_vec.shape[3])):
            self.means[lbl,cell] = np.mean(base_vec[:,:,lbl,cell])
        self.means[self.means==0] = np.inf
        
        return base_vec, t_cells
                