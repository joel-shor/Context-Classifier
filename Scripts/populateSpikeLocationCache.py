'''
Created on May 4, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from Data.Analysis.cache import try_cache, store_in_cache
from Data.goodClusters import get_good_clusters
from Data.Analysis.getClusters import spike_loc

def run():
    logging.basicConfig(level=logging.INFO)
    
    good_trials = try_cache('Good trials')
    animal_sess_combs = [(animal,session) for animal in [66,70] 
                         for session in good_trials[animal]]
    
    _, good_clusters = get_good_clusters(0)
    
    for animal, session in animal_sess_combs:
        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)
        cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
        
        
        for tetrode,cl in cls.items():
            if tetrode not in good_clusters: 
                import pdb; pdb.set_trace()
                continue
            for cell in good_clusters[tetrode]:
                logging.info('Finding spike locations for animal %i, session %i, tetrode %i, cell %i',animal, session, tetrode,cell)
                cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,cell)
                spk_i = spike_loc(cl, vl, trigger_tm, cell, key=None)
                if spk_i is np.NAN: break
                store_in_cache(cache_key,spk_i)

if __name__ == '__main__':
    run()