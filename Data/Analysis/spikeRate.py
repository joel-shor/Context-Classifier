'''
Created on Mar 29, 2014

@author: jshor
'''
import numpy as np
from scipy.signal import hamming as hamm
from scipy.signal import convolve2d
import logging

from Data.findInside import cache_inside_mask
from Data.Analysis.cache import try_cache

filt_win_ratio = 1.0/3   # Make it odd!
time_per_vl_pt = .02 #(seconds)

def spike_rate(room_shape, vl, spk_i, bin_size,valid=None):
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
    xbinsz = (xmax-xmin)/bin_size
    ybinsz = (ymax-ymin)/bin_size
    spks = np.zeros([xbinsz,ybinsz])
    times_spent = np.zeros([xbinsz,ybinsz])
    
    for xbin in range(xbinsz):
        
        xstart = xmin+xbin*bin_size
        xend = xmin+(xbin+1)*bin_size
        
        x_strip_spks = (vl['xs'][spk_i] >= xstart) &  (vl['xs'][spk_i] < xend)
        
        x_strip_time = (vl['xs'] >= xstart) & (vl['xs'] < xend) & valid
        
        for ybin in range(ybinsz):
            
            ystart = ymin+(ybin)*bin_size
            yend = ymin+(ybin+1)*bin_size
            
            y_strip_spks = (vl['ys'][spk_i] >= ystart) & (vl['ys'][spk_i] < yend)
            
            y_strip_time = (vl['ys'] >= ystart) & (vl['ys'] < yend) & valid
            
            pts = np.sum(x_strip_time & y_strip_time)
            times_spent[xbin,ybin] = pts*time_per_vl_pt
            
            spk_cnt = np.sum(x_strip_spks & y_strip_spks)
            spks[xbin,ybin] = 1.0*spk_cnt
            
            if spk_cnt > pts:
                raise Exception('Spike miscount')
    
    # Smooth
    spks = smooth(spks, bin_size, room_shape)
    times_spent = smooth(times_spent, bin_size, room_shape)
    
    times_spent[(times_spent == 0)] = np.Infinity
    return spks/times_spent

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

def gauss_kernel(*args):
    return np.array([[.0025,.0125,.0200,.0125,.0025],
                     [.0125,.0625,.1000,.0625,.0125],
                     [.0200,.1000,.1600,.1000,.0200],
                     [.0125,.0625,.1000,.0625,.0125],
                     [.0025,.0125,.0200,.0125,.0025]])

def inside(bin_size, room_shape):
    ''' The environment is split into NxN bins. '''
    cache_key = (bin_size, room_shape, 'Inside mask')
    mask = try_cache(cache_key)
    if mask is None:
        logging.info('Inside mask for bin side %i not cached. Computing...',bin_size)
        mask = cache_inside_mask(bin_size, room_shape)
        mask = try_cache(bin_size, room_shape, 'Inside mask')

    return mask

def smooth(array,bin_size, room_shape):
    ''' Apply a filter to smooth rates.
    
        Convolve with the filters, then adjust 
        by the appropriate weight.'''
    
    assert (room_shape[0][1]-room_shape[0][0])/bin_size==array.shape[0]
    assert (room_shape[1][1]-room_shape[1][0])/bin_size==array.shape[1]
    
    bin_len = (room_shape[0][1]-room_shape[0][0])/bin_size
    
    ins_mask = inside(bin_size,room_shape)
    
    if np.sum(( 1-ins_mask)*array) != 0:
        print 'Something is going on outside!'
        import pdb; pdb.set_trace()
        import matplotlib.pyplot as plt
        plt.figure()
        plt.pcolor((1-ins_mask)*array)
        plt.figure()
        plt.pcolor(ins_mask)
        plt.show()
        import pdb; pdb.set_trace()
        raise Exception('Something is going on outside!')
    
    filt = gauss_kernel(int(round(filt_win_ratio*bin_len,0)))
    pre_adjusted_rates = np.real(convolve2d(array,filt,mode='same'))
    weight_adjustment = np.real(convolve2d(ins_mask,filt,mode='same'))
    
    # Adjust weight_adjustment so we don't get any division by 0 errors
    weight_adjustment += 1-ins_mask
    
    adjusted_rates = pre_adjusted_rates*ins_mask/weight_adjustment
    
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
    plt.pcolor(weight_adjustment*inside(binsz))
    plt.colorbar()
    
    plt.figure()
    plt.pcolor(pre_adjusted_rates)
    plt.colorbar()
    plt.figure()
    plt.pcolor(adjusted_rates)
    plt.colorbar()
    plt.show()'''
    return np.real(adjusted_rates)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    #import pdb; pdb.set_trace()
    plt.pcolor(inside(120/8))
    plt.show()
