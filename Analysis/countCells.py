'''
Created on Apr 28, 2014

@author: jshor
'''
import logging
import numpy as np

from Analysis.getClusters import spike_loc

def count_cells(vl,cls,trigger_tm,good_clusters):
    ''' Returns a dictionary of tracked cells of the form
    t_cells[(tetrode,cell)] = indices of spikes of this cell '''
    
    t_cells = {}
    for tetrode,cl in cls.items():
        if tetrode not in good_clusters: continue
        for cell in good_clusters[tetrode]:
            logging.info('Finding spike locations for tetrode %i, cell %i',tetrode,cell)
            cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,cell)
            spk_i = spike_loc(cl, vl, trigger_tm, cell, cache_key)
            if spk_i is np.NAN: break
            t_cells[(tetrode,cell)] = spk_i
    if len(t_cells) == 0: raise Exception('No cells found')
    return t_cells