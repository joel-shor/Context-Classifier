'''
Created on Nov 10, 2013

@author: jshor
'''
import numpy as np
from datetime import datetime
import logging

cl_rate = 31250.0

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
    st = cl['Time'][cl['Label']==target_cl].astype(np.float64)
    if st.shape == (0,):
        logging.warning('No clusters with label %i. Quitting...', target_cl)
        return np.NAN
    
    st /= (cl_rate*24*60*60)
    st += trigger_tm
    
    # Clean up the virmenLog iterations numbers by removing the
    #  nan ones and linearly interpolating between them
    f = np.nonzero(~np.isnan(vl['Iter num']))[0]
    y = np.round(np.interp(range(len(vl['Iter num'])), f, vl['Iter num'][f]),0)
    #y = np.round(y,0).astype(int)
    y = y.astype(int)
    
    
    with open('y tester')
    
    print y
    import pdb; pdb.set_trace()
    
    logging.info('%i pts in cluster %i',len(st),target_cl)
    if 1.0*len(st)/len(cl['Label']) > .05:
        logging.warning('Are you SURE you want to proceed?')
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN

    # Determine the iteration number at which each spike occured
    spk_i = np.zeros(st.shape)
    for ndx in range(len(st)):
        try:
            # Find iteration preceeding spike
            f = np.nonzero(vl['Iter time'] < st[ndx])[0][-1] # Take the last one
            
            # Make sure there is an iteration following the spike
            np.nonzero(vl['Iter time'] > st[ndx])[0][0]
            
            spk_i[ndx] = y[f]
        except:
            # If nonzero is empty, the spike occurred before the first
            #  or after the last spike
            spk_i[ndx] = np.NAN
    
    # Delete NaN values
    spk_i = spk_i[~np.isnan(spk_i)].astype(int)
    
    # Determine speed
    speed = np.sqrt(vl['vxs']**2+vl['vys']**2)
    
    # Only leave spikes when rat is running faster than 2 in /sec
    spk_i = np.intersect1d(spk_i, np.nonzero(speed > 2)[0])

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