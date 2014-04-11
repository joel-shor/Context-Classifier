'''
Created on Nov 10, 2013

@author: jshor
'''
import numpy as np
import logging
from matchClToVl import match_cl_to_vl
from matlabRound import matround


def spike_loc(cl, vl, trigger_tm, target_cl):
    ''' Return the indices of vl['xs'] and vl['ys']
        that correspond to spikes with cluster label
        target_cl.
        
        Note: vl['xs'] and vl['ys'] have repeated values.
            We must return exactly one index for each unique
            location.'''
    
    if target_cl == 1:
        logging.warning('Are you SURE you want to find cluster 1?')
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN
    
    # Get the times when a cluster in label 'target_cl' occurs
    # If target_cl is None, then find the iterations for everything
    st = cl['Time'][cl['Label']==target_cl]
    if st.shape == (0,):
        logging.warning('No clusters with label %i. Quitting...', target_cl)
        return np.NAN
    
    # Ask user if he wants to waste time on an excessively large dataset
    '''
    logging.info('%i pts in cluster %i',len(st),target_cl)
    if 1.0*len(st)/len(cl['Label']) > .05:
        logging.warning('Are you SURE you want to proceed?')
        return np.NAN
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN'''
    
    # Get the vl indices corresponding to times in st
    spk_i = np.array(list(match_cl_to_vl(st, vl, trigger_tm)))
    
    #import pdb; pdb.set_trace()
    
    # Delete NaN values
    spk_i = spk_i[~np.isnan(spk_i)].astype(int)
    
    # Determine speed
    # Matlab rounds speed to 6 or 7 decimals, so do the same for consistency
    speed = matround(np.sqrt(vl['vxs']**2+vl['vys']**2),decimals=6)[spk_i]
    
    # Only leave spikes when rat is running faster than 2 in /sec
    spk_i = spk_i[np.nonzero(speed > 2)[0]]

    return np.unique(spk_i)

if __name__ == '__main__':
    import timeit
