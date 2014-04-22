'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from scipy import stats
import logging
from itertools import product as pr

from ContextPredictors.Predictor import ContextPredictor
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate
from Data.Analysis.cache import try_cache,store_in_cache

class DotProductTimeSeg(ContextPredictor):
    name = 'DP Time Seg Profile 1'
    time_per_vl_pt = .02 #(seconds)
    '''good_clusters = {1:range(2,8),
                     2:range(2,8),
                     3:range(2,14),
                     4:range(2,7),
                     5:range(2,12),
                     6:[2],
                     7:[2,3,4],
                     11:[2],
                     12:[2,3]}'''
    good_clusters = {1:range(2,4)} #Temp
    min_population_time = 1 #(seconds)
    
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
        
        '''
        cached = try_cache(vl,cls,trigger_tm,label_is,room_shape,bin_size,self.name,
                           self.time_per_vl_pt,self.good_clusters)'''
        cached = None
        if cached is not None and False:
            self.base_vec, self.t_cells, self.means = cached
            logging.info('Got base vectors from cache.')
        else:
            self.base_vec, self.t_cells, self.means = self._calculate_base_vectors(label_is, trigger_tm)
            store_in_cache(vl,cls,trigger_tm,label_is,room_shape,bin_size,self.name,
                           self.time_per_vl_pt,self.good_clusters,
                           [self.base_vec,self.t_cells, self.means])
    
    def generate_population_vectors(self, label_l):
        ''' Return three arrays: One with the population vectors, one with
            the breakdown of which bin they are in, and the other
            with the percent of the labels.
            
            Xs[vec num, cell] = [vec1,vec2,..., veci]
            Bins[vec, binx, biny] = [# of pts in bin]
            Labels[vec, lbl] = [perc of vec that is labeled by lbl]'''
        
        min_i_len = int(self.min_population_time/self.time_per_vl_pt)
        num_vecs = len(self.vl['xs'])/min_i_len
        
        Xs = np.zeros([num_vecs,len(self.t_cells)]) # Activity vectors
        Bins = np.zeros([num_vecs, self.xbins, self.ybins]) # Number of points in a given bin
        Labels = np.zeros([num_vecs]) # Percent of first label
        pts_accounted_for = 0
        pts_tossed = 0
        
        # Give points bin labels
        xbin = np.zeros([len(self.vl['xs'])])
        ybin = np.zeros([len(self.vl['ys'])])
        
        x_check = 0
        for x in range(self.xbins):
            xmin = self.room_shape[0][0]+x*self.bin_size
            xmax = self.room_shape[0][0]+(x+1)*self.bin_size
            in_x_strip = (self.vl['xs'] >= xmin) & (self.vl['xs'] < xmax)
            xbin[in_x_strip] = x
            x_check += np.sum(in_x_strip)
        if x_check != len(self.vl['xs']):
            raise Exception('Xs do not align.')
        
        y_check = 0
        for y in range(self.ybins):
            logging.info('Generating population vector for bin (%i,%i) of %i',x,y, self.xbins)
            ymin = self.room_shape[1][0]+y*self.bin_size
            ymax = self.room_shape[1][0]+(y+1)*self.bin_size
            in_y_strip = (self.vl['ys'] >= ymin) & (self.vl['ys'] < ymax)
            ybin[in_y_strip] = y
            y_check += np.sum(in_y_strip)
        if y_check != len(self.vl['ys']):
            raise Exception('Ys do not align.')
        
        # Find proportion of time in a particular bin
        tm_per_seg = min_i_len*self.time_per_vl_pt
        for i in range(num_vecs):
            mini = i*min_i_len
            maxi = (i+1)*min_i_len
            cur_is = range(mini,maxi)
            
            logging.info('Generating population vector %i/%i',i+1,num_vecs)
            rate_vec = np.array([np.sum((spks>=mini) & (spks<maxi))/tm_per_seg
                                 for spks in self.t_cells.values()])
            nm = np.linalg.norm(rate_vec)
            if nm != 0:
                rate_vec /= nm
            Xs[i,:] = rate_vec
            
            # Label
            tru_cntxt = int(stats.mode(label_l[mini:maxi])[0][0])
            tru_lbl = self.reverse_lbls[tru_cntxt]
            Labels[i] = tru_lbl
            
            logging.info('Finding time spent in each bin for %i/%i',i+1,num_vecs)
            for x in range(self.xbins):
                in_cur_x = (xbin[cur_is]==x)
                if np.sum(in_cur_x) == 0: continue
                for y in range(self.ybins):
                    in_cur_y = (ybin[cur_is]==y)
                    in_cur_cell = (in_cur_x & in_cur_y)
                    if np.sum(in_cur_cell) == 0: continue
                    tm = np.sum(in_cur_cell)
                    Bins[i,x,y] = 1.0*tm/min_i_len
                    
        return Xs, Bins, Labels
    
    
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
        means = np.zeros([len(self.labels),len(t_cells)])
        for lbl, cell in pr(range(base_vec.shape[2]),range(base_vec.shape[3])):
            means[lbl,cell] = np.mean(base_vec[:,:,:,cell])
        means[means==0] = np.inf
        
        return base_vec, t_cells, means
                