'''
Created on Apr 28, 2014

@author: jshor

A script to store the task trials in the cache. The object
is a dictionary of the form good_trials[animal] = [good_sess1, ...]

The key is of the form ('Good trials')

Good trials have task labels and at least 1 labeled cell.
'''

from Cache.cache import try_cache, store_in_cache
from Data.readData import load_mux, load_vl, load_cl
import logging

from Analysis.countCells import count_cells
from Data import goodClusters



def run():
    logging.basicConfig(level=logging.INFO)
    cache_key = 'Good trials'
    animals = [66,73]
    sessions = range(100)
    _, good_clusters = goodClusters.get_good_clusters(0)
    
    good_trials = try_cache(cache_key)
    
    if good_trials is None: good_trials = {}
    
    for animal in animals:
        if animal not in good_trials: good_trials[animal] = []
        for session in sessions:
            if session in good_trials[animal]: continue
            try:
                fn, trigger_tm = load_mux(animal, session)
            except:
                logging.info('Animal %i has no sessions greater than %i',animal,session+1)
                break
            
            try:
                vl = load_vl(animal,fn)
            except:
                logging.info('Animal %i session %i is not a task trial',animal,session+1)
                continue
            
            cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
            
            try:
                count_cells(vl,cls,trigger_tm, good_clusters)
            except:
                # No cells found
                continue
            
            if session not in good_trials[animal]:
                good_trials[animal].append(session)
    store_in_cache(cache_key,good_trials)