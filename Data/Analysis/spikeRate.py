'''
Created on Mar 29, 2014

@author: jshor
'''
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import logging

time_per_vl_pt = .02 #(seconds)

def spike_rate(room_shape, vl, spk_i, bin_size=4,valid=None):
    ''' Returns a matrix corresponding to the spike rate in the (i,j)th spatial bin. '''
    
    # Valid is a list of indices that are valid. We want an array with 1 in valid
    #  spots and 0 elsewhere, so do the conversion
    if valid == None:
        valid = np.array([True]*len(vl['Task']))
    else:
        valid_tmp = np.array([False]*len(vl['Task']))
        valid_tmp[valid] = True
        valid = valid_tmp
    
    
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
        
        x_strip_spks = (vl['xs'][spk_i] >= xstart) &  (vl['xs'][spk_i] < xend)
        
        x_strip_time = (vl['xs'] >= xstart) & (vl['xs'] < xend) & valid
        
        for ybin in range(spks.shape[1]):
            
            ystart = ymin+(ybin)*bin_size
            yend = ymin+(ybin+1)*bin_size
            
            y_strip_spks = (vl['ys'][spk_i] >= ystart) & (vl['ys'][spk_i] < yend)
            
            y_strip_time = (vl['ys'] >= ystart) & (vl['ys'] < yend) & valid
            
            pts = np.sum(np.logical_and(x_strip_time,y_strip_time))
            times_spent[xbin,ybin] = pts*time_per_vl_pt
            
            spk_cnt = np.sum(np.logical_and(x_strip_spks,y_strip_spks))
            spks[xbin,ybin] = 1.0*spk_cnt
            
            if spk_cnt > pts:
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
