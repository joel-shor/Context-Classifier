'''
Created on Mar 29, 2014

@author: jshor
'''
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import logging

def spike_rate(room_shape, vl, spk_i, bin_size=2):
    [[xmin,xmax],[ymin,ymax]] = room_shape
    if (xmax-xmin)%bin_size != 0 or (ymax-ymin)%bin_size != 0:
        raise Exception('Bin size is not compatible with room size.')
    
    spks = np.zeros([(xmax-xmin)/bin_size,
                      (ymax-ymin)/bin_size])
    times_spent = np.zeros([(xmax-xmin)/bin_size,
                           (ymax-ymin)/bin_size])
    
    
    for xbin in range(spks.shape[0]):
        
        xstart = xmin+xbin*bin_size
        xend = xmin+(xbin+1)*bin_size
        
        x_strip_spks = np.logical_and(vl['xs'][spk_i] >= xstart, 
                            vl['xs'][spk_i] < xend)
        
        x_strip_time = np.logical_and(vl['xs'] >= xstart,
                            vl['xs'] < xend)
        
        for ybin in range(spks.shape[1]):
            
            ystart = ymin+(ybin)*bin_size
            yend = ymin+(ybin+1)*bin_size
            
            y_strip_spks = np.logical_and(vl['ys'][spk_i] >= ystart, 
                            vl['ys'][spk_i] < yend)
            
            y_strip_time = np.logical_and(vl['ys'] >= ystart, 
                            vl['ys'] < yend)
            
            time_spent = np.sum(np.logical_and(x_strip_time,y_strip_time))
            times_spent[xbin,ybin] = time_spent
            
            spk_cnt = np.sum(np.logical_and(x_strip_spks,y_strip_spks))
            spks[xbin,ybin] = 1.0*spk_cnt
            
            if spk_cnt > time_spent:
                raise Exception('Spike miscount')
    
    # Smooth
    #spks = gaussian_filter(spks,2)
    #times_spent = gaussian_filter(times_spent,2)
    times_spent[np.nonzero(times_spent == 0)] = np.Infinity

    return spks/times_spent

def place_field(firing_rate,std_devs=5):
    mn = np.average(firing_rate)
    std = np.std(firing_rate)
    return firing_rate > mn+std_devs*std
