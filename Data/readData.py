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


cl_rate = 31250.0
vl_base_date = datetime(year=1980,month=1,day=1)

dat_base = dirname(abspath(__file__))


def load_cl(num, fn, tetrode):
    ''' Returns the date as a datetime, a list of index numbers, and
        a list of classifications.
    
    A cluster file has an array of two elements.
        1) ? This is a jagged line thing ?
        2) The cluster that this spike was manually labeled as.
        
        ie [[1],[2],[3],...], [[1],[4],[3.4],...]
        the lengths are the same
     '''
    clpath = join(dat_base,'Data Files','Clusters','clusters%s'%(num,),fn)
    tmp = loadmat(clpath+'.cmb.%i.mat'%(tetrode,))
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    
    return {'Datetime': dt, 
            '"': np.array(tmp['clust'][0,0][0]), 
            'Label': np.array(tmp['clust'][0,0][1])}




def load_vl(num, fn):
    ''' Returns a list with :
            0) the current datetime
            1) a list of 'nows'
            2) a list of xs
            3) a list of ys
            4) vxs
            5) vys
            6) iterations column 1 (timestamps?)
            7) iterations column 2 (indices?)
    
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
      iterations: []

    '''
    vlpath = join(dat_base,'Data Files','VirmenLog','virmenLog%s'%(num,),fn)

    tmp = loadmat(vlpath+'.cmb.mat')
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    nows = tmp['virmenLog'][0,0][0][0]
    xs = tmp['virmenLog'][0,0][1][0]
    ys = tmp['virmenLog'][0,0][1][1]
    vxs = tmp['virmenLog'][0,0][2][0]
    vys = tmp['virmenLog'][0,0][2][1]

    iterations_col1 =  tmp['virmenLog'][0,0][-1][0,0][0]
    iterations_col2 = tmp['virmenLog'][0,0][-1][0,0][1][0]

    return {'Datetime': dt,
            'Time': nows, 
            'xs': xs, 
            'ys': ys, 
            'vxs': vxs, 
            'vys': vys, 
            '?1': iterations_col1, 
            '?2': iterations_col2}
 
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
    ''' [name, ?, ?, ?, empty] '''
    muxpath = join(dat_base,'Data Files', str(num))
    mux = loadmat(muxpath+'.mat')['mux'][0][0]
    
    # String the ending '.cmb'
    fn = mux[1][0][session][0][0].split('.')[0]
    
    first = mux[1][0][session]
    second = mux[2][session]
    third = mux[3][session]
    
    return [first,second,third], fn

def get_spikes():
    num = 66
    fn = '20130610T170549'
    tetrode = 5
    session = 70
    
    [first, second, third], fn = load_mux(num, session)
    import pdb; pdb.set_trace()
    cnt = 0
    for x in np.ravel(first):
        stack = [x]
        while len(stack) != 0:
            x = stack.pop()
            print x
            if type(x) == type():
                print 'THE SAME'
            try:
                if type(x) != type(np.ndarray([])):
                    print x
                    print type(x)
                    cnt += 1
                    continue
                for i in range(len(x)):
                    stack.append(x[i])
            except:
                print x
                cnt += 1
                
    print cnt
    
    'ex: fn=20130818T191517.cmb'
    
    cl = load_cl(num,fn,tetrode)
    vl = load_vl(num,fn)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    get_spikes()
    import sys; sys.exit()
    