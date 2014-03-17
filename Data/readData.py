'''
Created on Nov 10, 2013

@author: jshor
'''
from scipy.io import loadmat
from os.path import join, basename, dirname, abspath
from os import listdir
import numpy as np
from datetime import datetime
import logging
from matplotlib import pyplot as plt
from matplotlib import cm

cl_rate = 31250.0
clrs = ['b','g','r','c','m','k','y']
#clrs = ['b','g','r']
dat_base = dirname(abspath(__file__))


def load_cl(num, fn, tetrode):
    ''' Returns the date as a datetime, a list of index numbers, and
        a list of classifications.
    
    A cluster file has an array of two elements.
        1) Time. The rate is 31250/sec
        2) The cluster that this spike was manually labeled as.
        
        ie [[1],[2],[3],...], [[1],[4],[3.4],...]
        the lengths are the same
     '''
    clpath = join(dat_base,'Data Files','Clusters','clusters%s'%(num,),fn)
    tmp = loadmat(clpath+'.cmb.%i.mat'%(tetrode,))
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    
    return {'Datetime': dt, 
            'Time': np.array(tmp['clust'][0,0][0]), 
            'Label': np.array(tmp['clust'][0,0][1])}




def load_vl(num, fn):
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
    vlpath = join(dat_base,'Data Files','VirmenLog','virmenLog%s'%(num,),fn)

    tmp = loadmat(vlpath+'.cmb.mat')
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    nows = tmp['virmenLog'][0,0][0][0]
    xs = tmp['virmenLog'][0,0][1][0]
    ys = tmp['virmenLog'][0,0][1][1]
    vxs = tmp['virmenLog'][0,0][2][0]
    vys = tmp['virmenLog'][0,0][2][1]

    iteration_time = np.ravel(tmp['virmenLog'][0,0][-1][0,0][0])
    iteration_num = np.ravel(tmp['virmenLog'][0,0][-1][0,0][1])
    
    return {'Datetime': dt,
            'Time': nows, 
            'xs': xs, 
            'ys': ys, 
            'vxs': vxs, 
            'vys': vys, 
            'Iter time': iteration_time,
            'Iter num': iteration_num}
 
def load_wv(path):
    ''' A waveform file is a list of 4 data points corresponding to
        the 4 electrode recordings of the tetrode at a given time.
        
        [[1,2,3,4],
         [4,5,6,6],
         ...
        ]
        '''
    return loadmat(path)['waveforms']

def load_mux(num, session):
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
    
    muxpath = join(dat_base,'Data Files', str(num))
    mux = loadmat(muxpath+'.mat')['mux'][0][0]
    
    # String the ending '.cmb'
    fn = mux[1][0][session][0][0].split('.')[0]
    
    # Get the start time - although I don't know what this is
    #  is used for
    sr = mux[1][0,session][1][0,0][0][0,0][6][0,0][1][0,0][0]
    start_dt = datetime(year=int(sr[0,0]), month=int(sr[0,1]),
                        day=int(sr[0,2]),hour=int(sr[0,3]),
                        minute=int(sr[0,4]),second=int(sr[0,5]),
                        microsecond=int( 10**6*(sr[0,5]-int(sr[0,5])) ) )
    
    tr = mux[1][0,session][1][0,0][0][0,0][6][0,1][1][0,0][0]
    trigger_dt = datetime(year=int(tr[0,0]), month=int(tr[0,1]),
                        day=int(tr[0,2]),hour=int(tr[0,3]),
                        minute=int(tr[0,4]),second=int(tr[0,5]),
                        microsecond=int( 1000*(tr[0,5]-int(tr[0,5])) ) )
    
    return fn, trigger_dt, start_dt

def _datenum(dt):
    ''' Takes a python datetime.datetime and converts it to
        a Matlab serial date number ie the number of (fractional)
        days since January 0,0000 '''
    reference = datetime(year=1,month=1,day=1)
    delt = dt-reference
    return delt.total_seconds()/(60.0*60*24) + 365 + 1 \
                + 1 # Need an extra 1 to match Matlab's output...?

def get_spikes(cl,vl, trigger_dt, wanted_cl):
    
    if wanted_cl == 1:
        logging.warning('Are you SURE you want to plot cluster 1?')
        import pdb; pdb.set_trace()
    
    # Get the times when a cluster in label 'wanted_cl' occurs
    st = cl['Time'][cl['Label']==wanted_cl].astype(np.float)
    if st.shape == (0,):
        logging.warning('No clusters with label %i. Quitting...', wanted_cl)
        raise Exception()
    st /= (31250.0*24*60*60)
    st += _datenum(trigger_dt)
    
    # Clean up the virmenLog iterations numbers by removing the
    #  nan ones and linearly interpolating between them
    f = np.nonzero(~np.isnan(vl['Iter num']))[0]
    y = np.interp(range(len(vl['Iter num'])), f, vl['Iter num'][f])
    #y = np.round(y,0).astype(int)
    y = y.astype(int)
    
    
    logging.info('%i pts in cluster %i',len(st),wanted_cl)
    if 1.0*len(st)/len(cl['Label']) > .1:
        logging.warning('Are you SURE you want to proceed?')
        y = raw_input()
        if y in ['n', 'N']:
            return

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
    
    if clrs == []:
        logging.warning('Ran out of colors!!')
        raise Exception()
    plt.scatter(vl['xs'][spk_i],vl['ys'][spk_i],zorder=2,color=clrs.pop())
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    tetrode = 5
    session = 59 # This is August 7, 2013 run
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    fn, trigger_dt, _ = load_mux(animal, session)
    cl = load_cl(animal,fn,tetrode)
    vl = load_vl(animal,fn)

    plt.plot(vl['xs'],vl['ys'],clrs.pop(),zorder=1)    
    try:
        for wanted_cl in range(2,15):
            get_spikes(cl, vl, trigger_dt, wanted_cl)
        raise Exception()
    except:
        plt.show()
    
    