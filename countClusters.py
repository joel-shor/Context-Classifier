'''
Created on Apr 27, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_cl
from Data.Analysis.cache import try_cache, store_in_cache


if __name__ == '__main__':
    cls = []
    animals = range(65,74)
    sessions = range(1,100)
    tetrodes = range(1,17)
    
    key = (animals,sessions,tetrodes,'count clusters')
    cache = try_cache(key)
    if cache is not None:
        cls = cache
    else:
        for animal in animals:
            print 'Animal ', animal
            for session in sessions:
                print 'Session', session
                try:
                    fn, _ = load_mux(animal, session)
                except:
                    logging.info('Animal %i has no sessions greater than %i',animal,session-1)
                    break
                cells = 0
                for tetrode in tetrodes:
                    cl = load_cl(animal, fn, tetrode)
                    cells += len(np.unique(cl['Label']))-1
                cls.append((animal, session, cells))
        store_in_cache(key,cls)
    
    cls.sort(key=lambda x:x[2])
    txt = '%i    %i    %i'
    print 'Animal    Session    Cells'
    for animal,session,cells in cls:
        print txt%(animal,session,cells)
        
                    