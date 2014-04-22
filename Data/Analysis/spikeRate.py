'''
Created on Mar 29, 2014

@author: jshor
'''
import numpy as np
from scipy.signal import hamming as hamm
from scipy.signal import convolve2d
import logging

filt_win_size = 5   # Make it odd!
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
    pre_smooth_rates = spks/times_spent
    post_smooth_rates = smooth(pre_smooth_rates)

    return post_smooth_rates

def place_field(firing_rate,std_devs=5):
    mn = np.average(firing_rate)
    std = np.std(firing_rate)
    return firing_rate > mn+std_devs*std

def hamm_kernel(N):
    left = hamm(N).reshape([-1,1])
    right = np.transpose(left)
    pre_normalized = np.dot(left,right)
    kern = pre_normalized/np.sum(pre_normalized)
    return kern
def inside():
    corner = np.ones([15,15])
    for i in range(6):
        corner[0,i] = 0
    for i in range(3):
        corner[1,i] = 0
    for i in range(2):
        corner[2,i] = 0
    for i in range(6):
        corner[i,0] = 0
    
    # Now repeat the corner in all 4 corners
    mask = corner*np.fliplr(corner)*np.flipud(corner)* \
            np.fliplr(np.flipud(corner))

    return mask
def smooth(rates):
    ''' Apply a filter to smooth rates.
    
        Convolve with the filters, then adjust 
        by the appropriate weight.'''
    
    if np.sum(( 1-inside())*rates) != 0:
        print 'Something is going on outside!'
        import pdb; pdb.set_trace()
        import matplotlib.pyplot as plt
        plt.figure()
        plt.pcolor((1-inside())*rates)
        plt.figure()
        plt.pcolor(inside())
        plt.show()
        raise Exception('Something is going on outside!')
    
    filt = hamm_kernel(filt_win_size)
    pre_adjusted_rates = np.real(convolve2d(rates,filt,mode='same'))
    weight_adjustment = np.real(convolve2d(inside(),filt,mode='same'))
    
    # Adjust weight_adjustment so we don't get any division by 0 errors
    weight_adjustment += 1-inside()
    
    adjusted_rates = pre_adjusted_rates*inside()/weight_adjustment
    
    '''
    if np.sum(adjusted_rates) != np.sum(rates):
        import pdb; pdb.set_trace()
        print 'Smoothing did not work properly.'
        #raise Exception('Smoothing did not work properly.')
    
    import matplotlib.pyplot as plt
    plt.figure()
    plt.pcolor(rates)
    plt.colorbar()
    
    plt.figure()
    plt.pcolor(weight_adjustment*inside())
    plt.colorbar()
    
    plt.figure()
    plt.pcolor(pre_adjusted_rates)
    plt.colorbar()
    plt.figure()
    plt.pcolor(adjusted_rates)
    plt.colorbar()
    plt.show()'''
    return np.real(adjusted_rates)
