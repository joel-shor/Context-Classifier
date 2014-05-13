'''
Created on Mar 29, 2014

@author: jshor
'''
import numpy as np
from itertools import product
from scipy.signal import hamming as hamm
from scipy.signal import convolve2d
import logging

from Data.findInside import cache_inside_mask
from cache import try_cache
from Data.Analysis.Indicators import bin_indicator, bin_id, cell_id, bin_index

tpp = .02 #Time per point (seconds) 

def rates_from_pv_old(X,Y,bin_size,room,smooth_flag=True):
    ''' Convert population vectors to firing rates.
        rates[cell id, lbl, xbin, ybin] = rate
        
        ***DIFFERENCE
        This is if the Xs are  [cell1,...,cell2,xbin,ybin]
        instead of             [cell1,...,cell2,bin1frac,bin2frac,...,zbinfrac]
        '''
    assert (room[0][1]-room[0][0])%bin_size == 0
    assert (room[1][1]-room[1][0])%bin_size == 0
    
    x = X[:,-2]
    y = X[:,-1]
    X = X[:,:-2]
    
    xbins = (room[0][1]-room[0][0])/bin_size
    ybins = (room[1][1]-room[1][0])/bin_size
    
    labels = np.unique(Y)
    lbl_is = {lbl:np.nonzero(Y==lbl)[0] for lbl in labels}
    
    bins = bin_indicator(x,y,xbins,ybins,bin_size,room)
    bin_is = {(xbin,ybin):np.nonzero(bins==bin_id(xbin,ybin,ybins))[0] for xbin,ybin in product(range(xbins),range(ybins))}
    
    spks = np.zeros([X.shape[1],len(labels),xbins,ybins])
    time_spent = np.zeros([X.shape[1],len(labels),xbins,ybins])

    for xbin,ybin,lbl in product(range(xbins),range(ybins),range(len(labels))):
        bin_i = bin_is[(xbin,ybin)]
        lbl_i = lbl_is[labels[lbl]]
        cur = np.intersect1d(bin_i, lbl_i)
        if len(cur) == 0: continue
        time_spent[:,lbl,xbin,ybin] = len(cur)
        spks[:,lbl,xbin,ybin] = np.sum(X[cur,:],axis=0)
    
    if smooth_flag:
        for cell,lbl in product(range(spks.shape[0]),range(spks.shape[1])):
            spks[cell,lbl] = smooth(spks[cell,lbl], bin_size, room)
            time_spent[cell,lbl] = smooth(time_spent[cell,lbl], bin_size, room)
    
    # Prevent divide by 0
    time_spent[time_spent==0]=1
    
    rates = 1.0*spks/time_spent/tpp
    
    return rates

def rates_from_pv(X,Y,bin_size,room,smooth_flag=True):
    ''' Convert population vectors to firing rates.
        rates[cell id, lbl, xbin, ybin] = rate
        
        ***DIFFERENCE
        This is if the Xs are [[cell1,...,cell2,bin1frac,bin2frac,...,zbinfrac],...]
        instead of            [cell1,...,cell2,xbin,ybin]
        '''
    assert (room[0][1]-room[0][0])%bin_size == 0
    assert (room[1][1]-room[1][0])%bin_size == 0
    
    xbins = (room[0][1]-room[0][0])/bin_size
    ybins = (room[1][1]-room[1][0])/bin_size
    
    # Add an extra dimension for the einsum
    bin_frac = X[:,-xbins*ybins:].reshape([X.shape[0],xbins*ybins,1])
    X = X[:,:-xbins*ybins].reshape([X.shape[0],X.shape[1]-xbins*ybins,1])
    
    # Generate an array [cells,xbins*ybins,# examples]
    #  where the value is the ith cell's contribute to
    #  firing in bin j on example k
    import time
    print 'starting'
    s = time.time()
    cell_firings = np.einsum('ncs,nbs->cbn',X,bin_frac)
    print 'Took time %.3f'%(time.time()-s,)
    import pdb; pdb.set_trace()
    
    labels = np.unique(Y)
    bin_frac = bin_frac.reshape(bin_frac.shape[:-1])
    
    # Cell, label, xbin, ybin
    spks = np.zeros([X.shape[1],len(labels),xbins,ybins])
    time_spent = np.zeros([len(labels),xbins,ybins])

    for lbl in range(len(labels)):
        lbl_is = (Y==labels[lbl])
        sp = np.sum(cell_firings[:,:,lbl_is],axis=2)
        tm = np.sum(bin_frac[lbl_is,:],axis=0)
        
        # Load spikes into matrix
        spks[:,lbl,:,:] = sp.reshape([-1,xbins,ybins])
        
        #Load times into time_spent
        time_spent[lbl,:,:] = tm.reshape([-1,xbins,ybins])
    
    ''' There is not check that x and y axes are not messed up,
        but it worked in trial code and it will be seen in classifier
        accuracy. '''
    
    if smooth_flag:
        for cell,lbl in product(range(spks.shape[0]),range(spks.shape[1])):
            spks[cell,lbl] = smooth(spks[cell,lbl], bin_size, room)
        for lbl in range(time_spent.shape[0]):
            time_spent[lbl,:,:] = smooth(time_spent[lbl], bin_size, room)
    
    # Prevent divide by 0
    time_spent[time_spent==0]=1
    
    for cell in range(spks.shape[0]):
        spks[cell] = 1.0*spks[cell]/time_spent/tpp
    
    return spks

def get_rates(x,y,label_l, room, bin_size, t_cells, smooth_flag=True):
    
    assert (room[0][1]-room[0][0])%bin_size == 0
    assert (room[1][1]-room[1][0])%bin_size == 0
    
    xbins = (room[0][1]-room[0][0])/bin_size
    ybins = (room[1][1]-room[1][0])/bin_size
    
    labels = np.unique(label_l)
    lbl_is = {lbl:np.nonzero(label_l==lbl)[0] for lbl in labels}
    
    bins = bin_indicator(x,y,xbins,ybins,bin_size,room)
    bin_is = {(xbin,ybin):np.nonzero(bins==bin_id(xbin,ybin,ybins))[0] for xbin,ybin in product(range(xbins),range(ybins))}
    
    spks = np.zeros([len(t_cells),len(labels),xbins,ybins])
    time_spent = np.zeros([len(labels),xbins,ybins])
    
    logging.info('Calculating firing rates')
    for xbin,ybin,lbl in product(range(xbins),range(ybins),labels):

        bin_i = bin_is[(xbin,ybin)]
    
        lbl_i = lbl_is[lbl]
        
        time_i = np.intersect1d(bin_i,lbl_i)
        if len(time_i)==0:continue # no time spent in bin
        cur_lbl_id = np.where(labels==lbl)
        time_spent[cur_lbl_id,xbin,ybin] = len(time_i)
        
        for key in t_cells.keys():
            
            cell_i = t_cells[key]
            cur_i = np.intersect1d(time_i,cell_i)
            
            tetrode,cell = key
            cur_cell_id = cell_id(tetrode,cell,t_cells)
            
            spks[cur_cell_id, cur_lbl_id, xbin, ybin] = len(cur_i)
    
    
    if smooth_flag:
        for cell,lbl in product(range(spks.shape[0]),range(spks.shape[1])):
            spks[cell,lbl] = smooth(spks[cell,lbl], bin_size, room)
        for lbl in range(time_spent.shape[0]):
            time_spent[lbl,:,:] = smooth(time_spent[lbl], bin_size, room)
    
    # Prevent divide by 0
    time_spent[time_spent==0]=1
    
    for cell in range(spks.shape[0]):
        spks[cell] = 1.0*spks[cell]/time_spent/tpp
    
    return spks


def hamm_kernel(N):
    ''' Depreciated. '''
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
        mask = try_cache(cache_key)

    return mask

def smooth(array,bin_size, room_shape):
    ''' Apply a filter to smooth rates.
    
        Convolve with the filters, then adjust 
        by the appropriate weight.'''
    
    assert (room_shape[0][1]-room_shape[0][0])/bin_size==array.shape[0]
    assert (room_shape[1][1]-room_shape[1][0])/bin_size==array.shape[1]
    
    ins_mask = inside(bin_size,room_shape)
    
    #assert np.sum(( 1-ins_mask)*array) == 0
    ''''''
    # Debug code
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
    
    filt = gauss_kernel()
    #array = array + 0j
    #ins_mask = ins_mask + 0j
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
    # Test the einsum command
    
    bin_frac = np.arange(8).reshape(4,2,1)
    X = np.arange(0,30,5).reshape(2,2,1)
    
    # Generate an array [cells,xbins*ybins,# examples]
    #  where the value is the ith cell's contribute to
    #  firing in bin j on example k
    cell_firings = np.einsum('ncs,nbs->cbn',X,bin_frac)
    print X
    print bin_frac
    print cell_firings

