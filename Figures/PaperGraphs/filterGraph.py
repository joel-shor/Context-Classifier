'''
Created on May 14, 2014
Updated on May 25, 2014

@author: jshor

A graph for the paper showing the environment mask and the discrete Gaussian
that is used for firing rate smoothing.
'''
import numpy as np
from Data.findInside import cache_inside_mask
from Cache.cache import try_cache
import logging
from matplotlib import pyplot as plt

def inside(bin_size, room_shape):
    ''' The environment is split into NxN bins. '''
    cache_key = (bin_size, room_shape, 'Inside mask')
    mask = try_cache(cache_key)
    if mask is None:
        logging.info('Inside mask for bin side %i not cached. Computing...',bin_size)
        mask = cache_inside_mask(bin_size, room_shape)
        mask = try_cache(cache_key)

    return mask

def gauss_kernel(*args):
    return np.array([[.0025,.0125,.0200,.0125,.0025],
                     [.0125,.0625,.1000,.0625,.0125],
                     [.0200,.1000,.1600,.1000,.0200],
                     [.0125,.0625,.1000,.0625,.0125],
                     [.0025,.0125,.0200,.0125,.0025]])

def filter_graph():
    ins_mask = inside(5,[[-55,55],[-55,55]])
    plt.figure()
    plt.pcolor(ins_mask)
    plt.axis('off')
    plt.autoscale(tight=True)
    
    filt = gauss_kernel().astype(np.complex)
    plt.figure()
    plt.pcolor(filt)
    plt.axis('off')
    plt.autoscale(tight=True)
    plt.show()
    
    plt.show()