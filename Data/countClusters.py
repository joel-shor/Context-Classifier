'''
Created on Apr 27, 2014

@author: jshor

Prints a list of animal/session combinations in order of
the number of clusters that are found and tagged.
'''
import logging
import numpy as np

from readData import load_mux, load_cl, load_vl
from Analysis.cache import try_cache, store_in_cache


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    animals = range(65,74)
    sessions = range(1,100)
    tetrodes = range(1,17)
    
    good_trials = try_cache('Good trials')
    
    key = (animals,sessions,tetrodes,'count clusters')
    cache = try_cache(key)
    cache=None
    if cache is not None:
        cls = cache
    else:
        cls = []
        for animal in animals:
            print 'Animal ', animal
            for session in good_trials[animal]:
                print 'Session', session
                fn, _ = load_mux(animal, session)
                vl = load_vl(animal,fn)
                if len(np.unique(vl['Task'])) != 2:continue

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
        
                    