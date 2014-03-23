'''
Created on Nov 10, 2013

@author: jshor
'''
import numpy as np
from datetime import datetime
import logging
from matchClToVl import match_cl_to_vl
from matlabRound import matround

def _datenum(dt):
    ''' Takes a python datetime.datetime and converts it to
        a Matlab serial date number ie the number of (fractional)
        days since January 0,0000 
        
        No longer needed since initial trigger time is stored
        as a Matlab serial date number'''
    reference = datetime(year=1,month=1,day=1)
    delt = dt-reference
    return delt.total_seconds()/(60.0*60*24) + 365 + 1 \
                + 1 # Need an extra 1 to match Matlab's output...?

def spike_loc(cl, vl, trigger_tm, target_cl):
    
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
    logging.info('%i pts in cluster %i',len(st),target_cl)
    if 1.0*len(st)/len(cl['Label']) > .05:
        logging.warning('Are you SURE you want to proceed?')
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN
    
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

    return spk_i


if __name__ == '__main__':
    animal = 66
    session = 60 # This is August 7, 2013 run
    tetrode = 4
    
    from readData import load_mux, load_cl, load_vl
    fn, trigger_tm = load_mux(animal, session)
    cl = load_cl(animal,fn,tetrode)
    vl = load_vl(animal,fn)
    
    print spike_loc(cl, vl, trigger_tm, target_cl=2)
    import pdb; pdb.set_trace()