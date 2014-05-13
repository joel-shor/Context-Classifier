'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from scipy.stats import mode
import logging
from itertools import product


from Data.Analysis.Indicators import bin_indicator, spk_indicators, bin_id, cell_id, bin_index

def gpv(vl, t_cells, label_l, K,bin_size, room):
    ''' Returns a matrix of feature vectors.
    
    The feature vector is:
    [frac cell 1, frac cell 2, ..., frac cell n, frac in bin1, frac in bin2,...]
    
    The matrix dimension is [# of vectors, # cells + # bins]
    
    With labels [mode context1, mode context2,...]
    
    K is the length of the subvector that will be used to calculate firing rate
    '''
    
    # Check data integrity
    assert len(label_l) == len(vl['xs'])
    assert (room[0][1]-room[0][0]) % bin_size == 0
    assert (room[1][1]-room[1][0]) % bin_size == 0
    
    xbins = (room[0][1]-room[0][0]) / bin_size
    ybins = (room[1][1]-room[1][0]) / bin_size
    
    end = (len(label_l)/K)*K    # Use integer roundoff to our advantage
    logging.warning('Threw away %i/%i points.',len(label_l)-end, len(label_l))

    # Generate an indicator array for identity of spiking cell
    spks = spk_indicators(t_cells, len(label_l))
    spks = spks[:end].reshape([K,-1]).astype(int)   # make the right size
    
    label_l = label_l[:end].reshape([K,-1])
    
    # Generate an indicator array for bin number
    bins = bin_indicator(vl['xs'],vl['ys'],xbins,ybins,bin_size,room)
    bins = bins[:end].reshape([K,-1])   # Make the right size
    
    # The main data structures
    Xs = np.zeros([len(t_cells)+xbins*ybins,end/K])
    
    # Put in cell firing rates
    for tetrode,cell in t_cells:
        cur_cell_id = cell_id(tetrode,cell,t_cells)
        cur_cell_spk = np.bitwise_and(spks, np.ones(spks.shape).astype(int)*2**cur_cell_id)>0
        Xs[cur_cell_id,:] = np.mean(cur_cell_spk,axis=0)
        
        # Make sure spikes don't disappear
        assert np.sum(cur_cell_spk)==len(np.unique(t_cells[(tetrode,cell)]))
        
    # Put bin fractions in 
    for xbin, ybin in product(range(xbins),range(ybins)):
        cbin_id = bin_id(xbin,ybin,ybins)
        cbin_index = bin_index(xbin,ybin,ybins)
        Xs[len(t_cells)+cbin_index,:] = np.mean(bins==cbin_id,axis=0)
    
    Ys = mode(label_l,axis=0)[0]
    
    # All Ys are still valid labels
    labels = np.unique(label_l)
    assert np.sum(label_l==labels[0])+np.sum(label_l==labels[1]) == label_l.size

    # Fractions add up to 1
    assert np.allclose(np.ones(end/K),np.sum(Xs[len(t_cells):,:],axis=0))
    
    # Bin time is right
    
    
    # Everything is between 0 and 1
    assert np.all(Xs>=0) and np.all(Xs<=1)
    
    # Check that no spikes are missing
    for tetrode,cell in t_cells:
        actual_spks = len(np.unique(t_cells[(tetrode,cell)]))
        iid = cell_id(tetrode,cell,t_cells)
        Xs_spks = K*np.sum(Xs[iid,:])
        assert np.allclose(Xs_spks,actual_spks)
    
    return Xs,Ys
            