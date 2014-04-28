'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
from scipy.stats import mode
import logging

time_per_vl_pt = .02

def _spk_indicators(t_cells,n):
    ''' t_cells is a dictionary of {(tetrode, cell): spk_i} '''
    
    indicator = np.zeros([n,1])
    for spk_i, j in zip(t_cells.values(),range(len(t_cells))):
        indicator[spk_i] = j+1
    return indicator

def _bin_indicator(x,y,xbins,ybins,bin_size):
    indicator = np.zeros([len(x),1])
    for xbin in range(xbins):
        minx = xbin*bin_size
        maxx = (xbin+1)*bin_size
        in_x_strip = (x>=minx)&(x<maxx)
        
        for ybin in range(ybins):
            miny = ybin*bin_size
            maxy = (ybin+1)*bin_size
            in_y_strip = (y>=miny)&(y<maxy)
            
            in_bin = in_x_strip & in_y_strip
            
            bin_id = xbin*ybins + ybin
            
            indicator[in_bin] = bin_id
    return indicator

def generate_population_vectors(vl, t_cells, room_shape, bin_size, label_l, K=32):
    ''' Returns a matrix of feature vectors.
    
    The feature vector is:
    [fr cell 1, fr cell 2, ..., fr cell n, mode bin #]
    
    The label is the mode bin #.
    
    With labels [mode context1, mode context2,...]
    
    K is the length of the subvector that will be used to calculate firing rate
    t_cells
    '''
    
    # Check data integrity
    assert len(label_l) == len(vl['xs'])
    
    xbins = (room_shape[0][1]-room_shape[0][0])/bin_size
    ybins = (room_shape[1][1]-room_shape[1][0])/bin_size
    
    X = np.zeros([len(label_l)/K,len(t_cells)+1+1]) #One for silence, one for bin
    Y = np.zeros([len(label_l)/K,1])

    # Generate an indicator array for identity of spiking cell
    spks = _spk_indicators(t_cells, len(label_l))
    
    # Generate an indicator array for bin number
    bins = _bin_indicator(vl['xs'],vl['ys'],xbins,ybins,bin_size)

    # Make sure that the length of the info vectors are a multiple
    #  of K
    
    
    label_l2 = label_l[len(label_l)%K:].reshape([-1,K])
    spks2 = spks[len(label_l)%K:].reshape([-1,K])
    bins2 = bins[len(label_l)%K:].reshape([-1,K])
    
    #import pdb; pdb.set_trace()
    # Put in cell firing rates
    for cell in range(len(t_cells)+1):
        X[:,cell] = np.sum(spks2 == cell,axis=1)
    
    # Normalize
    X /= 1.0*K
    
    #import pdb; pdb.set_trace()
    # Put in mode bin location
    X[:,-1] = mode(bins2,axis=1)[0].reshape([-1])
    
    # Put in label
    
    Y[:] = mode(label_l2,axis=1)[0].reshape([-1,1])
    
    assert np.all(np.sum(X[:,:-1],axis=1) == 1)
    
    return X,Y
            


def generate_population_vectors2(vl, t_cells, room_shape, bin_size, label_l):
    ''' Returns a matrix of feature vectors.
    
    The feature vector is:
    [fr cell 1, fr cell 2, ..., fr cell n, mode bin #]
    
    The label is the mode bin #.
    
    With labels [mode context1, mode context2,...]
    '''
    
    xbins = (room_shape[0][1]-room_shape[0][0])/bin_size
    ybins = (room_shape[1][1]-room_shape[1][0])/bin_size
    
    X = []
    y = []

    pts_accounted_for = 0
    for x in range(xbins):
        xmin = room_shape[0][0]+x*bin_size
        xmax = room_shape[0][0]+(x+1)*bin_size
        in_x_strip = (vl['xs'] >= xmin) & (vl['xs'] < xmax)
        for y in range(ybins):
            logging.info('Generating population vector for bin (%i,%i) of %i',x,y, xbins)
            
            ymin = room_shape[1][0]+y*bin_size
            ymax = room_shape[1][0]+(y+1)*bin_size
            in_y_strip = (vl['ys'] >= ymin) & (vl['ys'] < ymax)
            
            # in_sqr is 1 iff that point is in the current bin
            in_sqr = in_x_strip & in_y_strip
            
            # Find transitions from 0 -> 1
            start_i = 1+np.nonzero(in_sqr[1:]>in_sqr[:-1])[0]
            
            # Find transitions from 1 -> 0
            end_i = 1+np.nonzero(in_sqr[:-1]>in_sqr[1:])[0]
            
            if in_sqr[0] == 1: start_i = np.concatenate([[0],start_i])
            if in_sqr[-1] == 1: end_i = np.concatenate([end_i,[len(in_sqr)]])
            
            if len(start_i) != len(end_i): 
                raise Exception('Indices don\'t align')
    
            #Xs[(x,y)] = np.zeros([len(start_i),len(t_cells)])
            #Ys[(x,y)] = np.zeros([len(start_i),1])
    
            for st, end, k in zip(start_i,end_i,range(len(start_i))):
                tm = time_per_vl_pt*(end-st)
                rate_vec = np.array([np.sum((spks>=st) & (spks<end))/tm for spks in t_cells.values()])
                
                #Normalize
                
                nm = np.linalg.norm(rate_vec)
                if nm != 0:
                    rate_vec /= nm

                fnl_vec = np.concatenate([rate_vec,[(x,y)]])
    
                pts_accounted_for += end-st
    if pts_accounted_for != len(vl['xs']):
        raise Exception('Some points went missing in ')
    return Xs, Ys
            