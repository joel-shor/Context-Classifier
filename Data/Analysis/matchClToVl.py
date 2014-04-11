'''
Created on Mar 22, 2014

@author: jshor
'''
import numpy as np
from matlabRound import matround

cl_rate = 31250.0

def match_cl_to_vl(times, vl, trigger_tm):
    ''' Return a generator with the iteration for each
        element in array 'times' '''
    times = times.astype(np.float64)
    times /= (cl_rate*24*60*60)
    times += trigger_tm
    
    import pdb; pdb.set_trace()
    
    # Clean up the virmenLog iterations numbers by removing the
    #  nan ones and linearly interpolating between them
    f = np.nonzero(~np.isnan(vl['Iter num']))[0]
    y = matround(np.interp(range(len(vl['Iter num'])), f, vl['Iter num'][f]),0)
    y = y.astype(int)
    
    # Iterations are Matlab indices, so they begin at 1
    #  Adjust them to fit Python
    y -= 1

    # Determine the iteration number at which each spike occurred
    for ndx in range(len(times)):
        try:
            # Find iteration preceeding spike
            f = np.nonzero(vl['Iter time'] < times[ndx])[0][-1] # Take the latimes one
            # Make sure there is an iteration following the spike
            np.nonzero(vl['Iter time'] > times[ndx])[0][0]
            
            yield y[f]
        except:
            # If nonzero is empty, the spike occurred before the first
            #  or after the last spike
            yield np.NAN
