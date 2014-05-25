'''
Created on Apr 27, 2014

@author: jshor

Prints a list of animal/session combinations in order of
the number of clusters that are found and tagged.
'''
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from Data.readData import load_mux, load_vl
from Cache.cache import try_cache

mpl.rcParams['font.size'] = 26
def count_vl():
    logging.basicConfig(level=logging.INFO)
    
    llist = []
    good_trials = try_cache('Good trials').items()
    for animal, sessions in good_trials:
        print 'Animal', animal
        for session in sessions:
            print 'Session', session
            fn, _ = load_mux(animal, session)
            vl = load_vl(animal,fn)
            llist.append(len(vl['xs']))
            
    print np.mean(llist)
    print len(llist)
    plt.hist(llist)
    plt.xlabel('Number of recorded points')
    plt.ylabel('Count')
    plt.title('Recorded Points per Session')
    plt.show()
    import pdb; pdb.set_trace()   
