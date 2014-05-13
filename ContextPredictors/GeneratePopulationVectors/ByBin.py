'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np
import logging
from scipy.stats import mode
from itertools import product
from Data.Analysis.Indicators import bin_indicator, spk_indicators, bin_id, cell_id, bin_index
from Data.Analysis.classifyTask import find_runs


def gpv(vl, t_cells, label_l, K,bin_size, room):
    ''' Returns a matrix of feature vectors.
    
    The feature vector is:
    [frac cell 1, frac cell 2, ..., frac cell n, mode X, mode Y]
    
    With labels [mode context1, mode context2,...]
    
    t_cells
    '''
    # Check data integrity
    assert len(label_l) == len(vl['xs'])
    assert (room[0][1]-room[0][0]) % bin_size == 0
    assert (room[1][1]-room[1][0]) % bin_size == 0
    
    #cache_key = (vl['xs'][::100],t_cells,label_l[::112],K,bin_size,room,'gpv by bin')
    #cache = try_cache(cache_key)
    #if cache is not None: return cache
    
    
    xbins = (room[0][1]-room[0][0]) / bin_size
    ybins = (room[1][1]-room[1][0]) / bin_size
    
    
    # Generate an indicator array for identity of spiking cell
    spks = spk_indicators(t_cells, len(label_l))
    
    
    labels = np.unique(label_l)
    lbl_is = {lbl:np.nonzero(label_l==lbl)[0] for lbl in labels}
    
    # Generate an indicator array for bin number
    bins = bin_indicator(vl['xs'],vl['ys'],xbins,ybins,bin_size,room)
    bin_is = {(xbin,ybin):np.nonzero(bins==bin_id(xbin,ybin,ybins))[0] for xbin,ybin in product(range(xbins),range(ybins))}
    

    # The main data structures
    Xs = []
    Ys = []
    
    # Debug structures
    all_accounted_for = 0   # Keep track of the moments in time
    thrown_away = 0
    
    for xbin,ybin,lbl in product(range(xbins),range(ybins),labels):
        cbin_id = bin_id(xbin,ybin,ybins)
        bin_i = bin_is[(xbin,ybin)]
        lbl_i = lbl_is[lbl]
        cur_i = np.intersect1d(bin_i, lbl_i)
        if len(cur_i)==0:continue   # Never in this bin with this context
        
        # Debug code
        all_accounted_for += len(cur_i)

        # Set up problem to use find_runs
        sgn2 = np.zeros([len(label_l),1])
        sgn2[cur_i] = 1
        sgn, run_len = find_runs(sgn2)
        run_start = np.intersect1d(sgn,cur_i)
        
        if len(run_start) == 0:
            import pdb; pdb.set_trace()
        
        for st in run_start:
            run_l = run_len[sgn==st]
            if run_l<K: 
                thrown_away += run_l
                continue

            delt = (run_l/K)*K  # Use rounding error to our advantage
            thrown_away += run_l-delt
            assert delt%K == 0
            X = np.zeros([delt/K,len(t_cells)+xbins*ybins])   # Extra vector space for x and y
            spks_tmp = spks[st:st+delt].reshape([K,-1])
            for tetrode,cell in t_cells:
                cur_cell_id = cell_id(tetrode,cell,t_cells)
                tmp = np.bitwise_and(spks_tmp.astype(int), np.ones(spks_tmp.shape).astype(int)*2**cur_cell_id)>0
                rt = np.sum(tmp,axis=0)

                X[:,cur_cell_id] = rt
            X /= 1.0*K
            X[:,len(t_cells)+bin_index(xbin,ybin,ybins)] = 1
            Xs.append(X)
            Ys.append(np.ones([delt/K])*lbl)
            
    
    assert all_accounted_for == len(label_l)
    Xs = np.concatenate(Xs)
    Ys = np.concatenate(Ys) 
    
    # Make sure bins were assigned correctly
    for xbin,ybin in product(range(xbins),range(ybins)):
        cbin_id = bin_id(xbin,ybin,ybins)
        cbin_index = bin_index(xbin,ybin,ybins)
        try:
            assert np.sum(bins==cbin_id)==np.sum(Xs[:,len(t_cells)+cbin_index])
        except:
            import pdb; pdb.set_trace()

    logging.warning('Threw away %i/%i points when generating PV by bin',thrown_away,len(label_l))

    #out = (Xs,Ys)
    #logging.warning('Storing ByBin gpv')
    #store_in_cache(cache_key,out)

    return Xs,Ys
            