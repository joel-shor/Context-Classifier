'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from scipy.stats import mode
import logging

def _spk_indicators(t_cells,n):
    ''' t_cells is a dictionary of {(tetrode, cell): spk_i} '''
    
    indicator = np.zeros([n,1])
    for spk_i, j in zip(t_cells.values(),range(len(t_cells))):
        indicator[spk_i] = j+1
    return indicator

def generate_population_vectors(vl, t_cells, label_l, K=32):
    ''' Returns a matrix of feature vectors.
    
    The feature vector is:
    [frac cell 1, frac cell 2, ..., frac cell n, mode X, mode Y]
    
    The label is the mode bin #.
    
    With labels [mode context1, mode context2,...]
    
    K is the length of the subvector that will be used to calculate firing rate
    t_cells
    '''
    
    # Check data integrity
    assert len(label_l) == len(vl['xs'])
    
    X = np.zeros([len(label_l)/K,len(t_cells)+2]) #Need x y coordinates at the end
    Y = np.zeros([len(label_l)/K,1])

    # Generate an indicator array for identity of spiking cell
    spks = _spk_indicators(t_cells, len(label_l))
    
    # Generate an indicator array for bin number
    #bins = _bin_indicator(vl['xs'],vl['ys'],xbins,ybins,bin_size)

    # Make sure that the length of the info vectors are a multiple
    #  of K
    
    label_l2 = label_l[len(label_l)%K:].reshape([-1,K])
    spks2 = spks[len(label_l)%K:].reshape([-1,K])
    #bins2 = bins[len(label_l)%K:].reshape([-1,K])
    
    # Put in cell firing rates
    for cell in range(1,len(t_cells)+1): # Don't include silence
        X[:,cell-1] = np.sum(spks2 == cell,axis=1)
    
    # Normalize
    X /= 1.0*K
    
    #import pdb; pdb.set_trace()
    # Now add mean 
    blocks = []
    for block in [vl['xs'],vl['ys']]:
        tmp = block[len(label_l)%K:].reshape([-1,K])
        tmp = np.mean(tmp,axis=1)
        blocks.append(tmp)
    X[:,-2] = blocks[0]
    X[:,-1] = blocks[1]
    
    # Put in label
    Y[:] = mode(label_l2,axis=1)[0].reshape([-1,1])
    
    return X,Y
            