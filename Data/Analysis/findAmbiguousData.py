'''
Created on Apr 21, 2014

@author: jshor
'''
import numpy as np
import logging

from Data.Analysis.cache import try_cache, store_in_cache
from Data.readData import load_mux, load_vl
from Data.Analysis.classifyTask import get_orientation

cache_key = 'Find ambiguous data'

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
    
    # Fix animal
    animal = 66
    
    # Add to dictionary
    if animal not in amb:
        amb[animal] = {}
    
    for session in range(44,100):
        if animal in amb and session in amb[animal]:
            logging.info('Found (Animal %i, Session %i) in cache',animal,session)
            continue
        try:
            fn, _ = load_mux(animal, session)
            vl = load_vl(animal,fn)
        except:
            logging.info('No data found for (Animal %i, Session %i)',animal,session)
            amb[animal][session] = None
            continue
        
        logging.info('Checking ambiguous data for (Animal %i, Session %i)',animal,session)
        
        orientation = get_orientation(vl,cntrx,cntry)
        task = vl['Task']
        
        # Checks
        if np.setdiff1d(np.unique(orientation), np.unique(task)) != []:
            logging.ERROR('Orientation and task labels do not match')
            import pdb; pdb.set_trace()
            raise Exception('Orientation and task labels do not match')
        
        # Assume that orientation and task labels are matched correctly
        ambiguous_data = np.sum(task != orientation)   
        tot = len(vl['xs'])
        
        
        amb[animal][session] = (ambiguous_data,  tot)
    
    # Store to cache
    store_in_cache(cache_key, amb)
    
    return amb