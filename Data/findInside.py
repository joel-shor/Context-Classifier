'''
Created on Apr 28, 2014

@author: jshor

A script that stores an indicator mask in the cache.
The mask is 1 if a rat could be in that cell, 0 if
that cell is outside of the environment.

The cache key is of the form (bin_size, room_shape, 'Inside mask')
'''
import logging
import numpy as np

from cache import try_cache,store_in_cache
from readData import load_mux, load_vl

def cache_inside_mask(bin_size, room_shape):
    xlen = room_shape[0][1]-room_shape[0][0]
    ylen = room_shape[1][1]-room_shape[1][0]
    assert xlen%bin_size==0
    assert ylen%bin_size==0
    
    N = xlen/bin_size
    xleft = room_shape[0][0]
    ydown = room_shape[1][0]
    
    inside = np.zeros([N,N])
    good_trials = try_cache('Good trials')
    
    for animal in [66,70]:
        for session in good_trials[animal]:
            logging.info('Checking animal %i, session %i',animal,session)
            fn, _ = load_mux(animal, session)
            vl = load_vl(animal,fn)

            for xbin in range(N):
                xmin = xbin*bin_size+xleft
                xmax = (xbin+1)*bin_size+xleft
                in_x = (vl['xs']>=xmin)&(vl['xs']<xmax)

                for ybin in range(N):
                    ymin = ybin*bin_size+ydown
                    ymax = (ybin+1)*bin_size+ydown

                    if np.any(in_x&(vl['ys']>=ymin)&(vl['ys']<ymax)):
                        inside[xbin,ybin]=1
    
    # 4 way Symmetric check
    for xbin in range(N/2):
        for ybin in range(N/2):
            assert inside[xbin,ybin] == inside[xbin,ybin]
            assert inside[xbin,ybin] == inside[N-xbin-1,ybin]
            assert inside[xbin,ybin] == inside[xbin,N-ybin-1]
            assert inside[xbin,ybin] == inside[N-xbin-1,N-ybin-1]
         
    cache_key = (bin_size, room_shape, 'Inside mask')
    store_in_cache(cache_key, inside)
    
    return inside

    