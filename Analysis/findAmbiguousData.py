'''
Created on Apr 21, 2014

@author: jshor
'''
import numpy as np
import logging
import traceback

from Cache.cache import try_cache, store_in_cache
from Data.readData import load_mux, load_vl
from Analysis.classifyTask import get_orientation

cache_key = 'Find ambiguous data'

# Error on 
# 65, 40

def find_ambiguous_data():
    # Final data structure will be a dictionary:
    #  amb[animal][session] = (#ambig, total)
    
    # First load cache
    
    cache = try_cache(cache_key)
    if cache is not None:
        amb = cache
    else:
        amb = {}

    # Fix center
    cntrx = cntry = 0
    
    # Animal range
    animals = range(65,74)
    
    not_task_trials = []
    for animal in animals:
    
        # Add to dictionary
        if animal not in amb:
            amb[animal] = {}
        
        for session in range(1,100):
            if animal in amb and session in amb[animal]: #and amb[animal][session]:
                logging.info('Found (Animal %i, Session %i) in cache',animal,session)
                continue
            try:
                fn, _ = load_mux(animal, session)
            except:
                logging.info('Animal %i has no sessions greater than %i',animal,session-1)
                break
            try:
                vl = load_vl(animal,fn)
            except:
                traceback.print_exc()
                logging.info('No data found for (Animal %i, Session %i)',animal,session)
                amb[animal][session] = None
                not_task_trials.append([animal,session])
                continue
            
            logging.info('Checking ambiguous data for (Animal %i, Session %i)',animal,session)
            
            orientation = get_orientation(vl,cntrx,cntry)
            
            # Assume that orientation and task labels are matched correctly
            radial = np.sum(0 == orientation)
            discrepency = np.sum(vl['Task'] != orientation)
            tot = len(vl['xs'])
            
            
            amb[animal][session] = (radial, discrepency,  tot)
        
    # Store to cache
    store_in_cache(cache_key, amb)
    
    return amb