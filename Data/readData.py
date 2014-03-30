'''
Created on Nov 10, 2013

@author: jshor
'''
from scipy.io import loadmat
from os.path import join, dirname, abspath
import numpy as np
from datetime import datetime
from matlabRound import matround

dat_base = dirname(abspath(__file__))


def load_cl(animal, fn, tetrode):
    ''' Returns the date as a datetime, a list of index numbers, and
        a list of classifications.
    
    A cluster file has an array of two elements.
        1) Time. The rate is 31250/sec
        2) The cluster that this spike was manually labeled as.
        
        ie [[1],[2],[3],...], [[1],[4],[3.4],...]
        the lengths are the same
     '''
    clpath = join(dat_base,'Data Files','Clusters','clusters%s'%(animal,),fn)
    tmp = loadmat(clpath+'.cmb.%i.mat'%(tetrode,))
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    
    return {'Datetime': dt, 
            'Time': np.array(tmp['clust'][0,0][0]), 
            'Label': np.array(tmp['clust'][0,0][1])}




def load_vl(animal, fn):
    ''' Returns a list with :
            0) the current datetime
            1) a list of 'nows'
            2) a list of xs
            3) a list of ys
            4) vxs
            5) vys
            6) Iterations
    
    A virmenlog file has is a numpy.void. 
        It has either no entry or a variable number
        of entries, corresponding to...? 
            now: [1x32993 double]
        position: [2x32993 double]
        velocity: [2x32993 double]
          cylPos: [2x32993 double]
    currentWorld: [1x32993 double]
           isITI: [1x32993 double]
        isReward: [1x32993 double]
           exper: [1x1 virmenExperiment]
        filename: [1x56 char]
         comment: ''
      iterations: np.void
          tmp['virmenLog'][0,0][-1][0,0][1]: 1x54561 ndarray

    '''
    vlpath = join(dat_base,'Data Files','VirmenLog','virmenLog%s'%(animal,),fn)

    tmp = loadmat(vlpath+'.cmb.mat')
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    nows = tmp['virmenLog'][0,0][0][0]
    xs = tmp['virmenLog'][0,0][1][0]
    ys = tmp['virmenLog'][0,0][1][1]
    vxs = tmp['virmenLog'][0,0][2][0]
    vys = tmp['virmenLog'][0,0][2][1]

    iteration_time = np.ravel(tmp['virmenLog'][0,0][-1][0,0][0])
    iteration_num = np.ravel(tmp['virmenLog'][0,0][-1][0,0][1])
    
    # Clean up the virmenLog iterations numbers by removing the
    #  nan ones and linearly interpolating between them
    f = np.nonzero(~np.isnan(iteration_num))[0]
    iteration_num = matround(np.interp(range(len(iteration_num)), f, iteration_num[f]),0)
    iteration_num = iteration_num.astype(int)
    
    return {'Datetime': dt,
            'Time': nows, 
            'xs': xs, 
            'ys': ys, 
            'vxs': vxs, 
            'vys': vys, 
            'Iter time': iteration_time,
            'Iter num': iteration_num}
 
def load_wv(animal, fn, tetrode):
    ''' A waveform file is a list of 4 data points corresponding to
        the 4 electrode recordings of the tetrode at a given time.
        
        returns an Xx4 ndarray
        ]
        '''
    clpath = join(dat_base,'Data Files','Waveforms','waveforms%s'%(animal,),fn)
    return loadmat(clpath+'.cmb.%i.mat'%(tetrode,))['waveforms']

def load_mux(animal, session):
    '''
    mux: np.void, len(mux) = 5
        [name of tetrode, 
        1x76 ndarray, 
        76x16 ndarray,
        76x16 ndarray,
        empty]
        
    mux[1][0,session]: np.void, len = 2
    mux[1][0,session][0]: NAME OF CORRESPONDING FILE
            Ex. 20130818T191517.cmb
    mux[1][0,session][1]: 1x1 ndarray
    mux[1][0,session][1][0,0]:  np.void, len = 5
    This is the good stuff
    mux[1][0,session][1][0,0][0]: 1x1 ndarray
    mux[1][0,session][1][0,0][0][0,0]: np.void, len = 36
    Now we're even closer to good data
    mux[1][0,session][1][0,0][0][0,0][6]: 1x5 ndarray
    -> to get to 'Start'
    mux[1][0,session][1][0,0][0][0,0][6][0,0]: np.void, len = 2
    mux[1][0,session][1][0,0][0][0,0][6][0,0][0] = 'Start'
    mux[1][0,session][1][0,0][0][0,0][6][0,0][1][0,0]: np.void, len 2
    mux[1][0,session][1][0,0][0][0,0][6][0,0][1][0,0][0]: 1x6 ndarray with date info
            ex array([[ 2013.,8.,18.,19.,
                       15.,17.76898909]])
    -> to get to 'Trigger'
    mux[1][0,session][1][0,0][0][0,0][6][0,1][0] = 'Trigger'
    mux[1][0,session][1][0,0][0][0,0][6][0,1][1][0,0][0]: np.void, len = 2
    '''
    
    session -= 1 # Session starts at 1, but array indices start at 0
    muxpath = join(dat_base,'Data Files', str(animal))
    mux = loadmat(muxpath+'.mat')['mux'][0][0]
    
    #import pdb; pdb.set_trace()
    # String the ending '.cmb'
    fn = mux[1][0][session][0][0].split('.')[0]
    
    # Get the start time - although I don't know what this is
    #  is used for
    sr = mux[1][0,session][1][0,0][0][0,0][6][0,0][1][0,0][0]
    start_dt = datetime(year=int(sr[0,0]), month=int(sr[0,1]),
                        day=int(sr[0,2]),hour=int(sr[0,3]),
                        minute=int(sr[0,4]),second=int(sr[0,5]),
                        microsecond=int( 10**6*(sr[0,5]-int(sr[0,5])) ) )
    
    # Get the trigger time - although I don't know what this is
    #  is used for
    tr = mux[1][0,session][1][0,0][0][0,0][6][0,1][1][0,0][0]
    trigger_dt = datetime(year=int(tr[0,0]), month=int(tr[0,1]),
                        day=int(tr[0,2]),hour=int(tr[0,3]),
                        minute=int(tr[0,4]),second=int(tr[0,5]),
                        microsecond=int( 1000*(tr[0,5]-int(tr[0,5])) ) )
    
    # Get the BackupInitialTime - this is the thing that corresponds
    #  to Matlab's mux.sessions(wanted_sess).info.ObjInfo.InitialTriggerTime
    # It is already given in 
    bt = mux[1][0,session][1][0,0][3][0,0][0][0,0]
    
    
    return fn, bt

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
