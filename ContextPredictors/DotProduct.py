'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging

from Predictor import ContextPredictor
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate

class DotProduct(ContextPredictor):
    
    def __init__(self, vl, cls, trigger_tm,room_shape=[[-60,60],[-60,60]], bin_size=10):
        self.vl = vl
        self.cls = cls  # An array of a bunch of cluster objects
        self.trigger_tm = trigger_tm
        self.room_shape = room_shape
        self.bin_size = bin_size
        
        self.base_vec = self._calculate_base_vectors()
    
    def _calculate_base_vectors(self):
        tracked_cells = []  # An array of cells that are included in the baseline in the form
                            #  (tetrode, cluster label)
        rates = []
        
        contexts = np.unique(self.vl['Task'])
        
        for context in contexts:
            context_is = np.nonzero(self.vl['Task']==context)[0]
            for cl, tetrode in zip(self.cls,range(len(self.cls))):
                for wanted_cl in range(2,7):
                    logging.info('Finding spike locations for tetrode %i, cell %i',tetrode,wanted_cl)
                    spk_i = spike_loc(cl, self.vl, self.trigger_tm, wanted_cl)
                    if spk_i is np.NAN: break
                    tracked_cells.append((tetrode,wanted_cl))
                    spks_in_context = np.intersect1d(spk_i, context_is)
                    rate = spike_rate(self.room_shape,self.vl,spks_in_context,self.bin_size,valid=(self.vl['Task']==context))
                    logging.info('Processed firing rates for tetrode %i, cell %i, context %i',tetrode,wanted_cl,context)
                    rates.append(rate)
        
        xlen = (self.room_shape[0][1]-self.room_shape[0][0])/self.bin_size
        ylen = (self.room_shape[1][1]-self.room_shape[1][0])/self.bin_size
        base_vec = np.zeros([xlen,ylen,len(contexts),len(rates)/len(contexts)])
        cell_num = len(rates)/len(contexts)
        for rate, i in zip(rates,range(len(rates))):
            context = i / cell_num
            cell = i % cell_num
            logging.info('Tetrode: %i, Cell:%i, Context:%i',tracked_cells[cell][0],
                         tracked_cells[cell][1],context)
            '''plt.figure()
            Xs,Ys = np.meshgrid(np.arange(-60,60,self.bin_size),np.arange(-60,60,self.bin_size))
            ss=plt.contourf(Xs,Ys,rate)
            plt.colorbar(ss, extend='both')
            plt.show()'''
            base_vec[:,:,context,cell] = rate
        return base_vec
                