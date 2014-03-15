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
    
    return [dt, np.array(tmp['clust'][0,0][0]), np.array(tmp['clust'][0,0][1])]



def load_cl2(path):
    ''' Returns the date as a datetime, a list of index numbers, and
        a list of classifications.
    
    A cluster file has an array of two elements.
        1) ? This is a jagged line thing ?
        2) The cluster that this spike was manually labeled as.
        
        ie [[1],[2],[3],...], [[1],[4],[3.4],...]
        the lengths are the same
     '''
    tmp = loadmat(path+'.cmb.mat')
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    
    return [dt, np.array(tmp['clust'][0,0][0]), np.array(tmp['clust'][0,0][1])]

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

    return [dt, nows, xs, ys, vxs, vys, iterations_col1, iterations_col2] 
 
def load_vl2(path):
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
    tmp = loadmat(path)
    dt = datetime.strptime(tmp['__header__'][50:],'%a %b %d %H:%M:%S %Y')
    nows = tmp['virmenLog'][0,0][0][0]
    xs = tmp['virmenLog'][0,0][1][0]
    ys = tmp['virmenLog'][0,0][1][1]
    vxs = tmp['virmenLog'][0,0][2][0]
    vys = tmp['virmenLog'][0,0][2][1]

    iterations_col1 =  tmp['virmenLog'][0,0][-1][0,0][0]
    iterations_col2 = tmp['virmenLog'][0,0][-1][0,0][1][0]

    return [dt, nows, xs, ys, vxs, vys, iterations_col1, iterations_col2] 

def load_wv(path):
    ''' A waveform file is a list of 4 data points corresponding to
        the 4 electrode recordings of the tetrode at a given time.
        
        [[1,2,3,4],
         [4,5,6,6],
         ...
        ]
        '''
    return loadmat(path)['waveforms']

def get_data_bundle(prefix, name):
    ''' Gets the waveform, virmenlog, and clusters for
        a particular bundle.
        Ex. prefix = 12, name =  20121129T171438'''
    '''path = join('Data Files','Waveforms','waveforms%s'%(prefix,))
    waveforms = []
    for filename in listdir(path):
        if filename.find(name) != -1:
            waveforms.append(join(path,filename))'''
    
    path = join(dat_base,'Data Files','VirmenLog','virmenLog%s'%(prefix,))
    virmenlog = []
    for filename in listdir(path):
        if filename.find(name) != -1:
            virmenlog.append(join(path,filename))
            
    path = join(dat_base,'Data Files','Clusters','clusters%s'%(prefix,))
    clusters = []
    for filename in listdir(path):
        if filename.find(name) != -1:
            clusters.append(join(path,filename))
    
    path = join(dat_base,'Data Files','Clusters','clusters%s'%(prefix,))
    clusters = []
    for filename in listdir(path):
        if filename.find(name) != -1:
            clusters.append(join(path,filename))
    
    return virmenlog, clusters
    #return waveforms, virmenlog, clusters


def reconstruct_bundles(prefix):
    ''' Returns an iterator that cycles through bundles. '''

    vlpath = join(dat_base,'Data Files','Waveforms','waveform%s'%(prefix,))

    for filename in listdir(vlpath):
        base = basename(filename).split('.')[0]
        print 'base', base
        #wvs, vls, cls = get_data_bundle(prefix,base)
        vls,cls = get_data_bundle(prefix,base)
        #wv = np.concatenate([load_wv(t) for t in wvs])# if len(wvs) > 1 else load_wv(wvs[0])
        
        #vl = np.concatenate([load_vl(t) for t in vls]) if len(vls) > 1 else load_vl(vls[0])
        vl = zip(*[load_vl(t) for t in vls])
        vl = [vl[0]] + [np.concatenate(x) for x in vl[1:]]

        # Cls could be split across multiple dfiles
        cl = zip(*([load_cl(t)for t in cls]))
        cl = [cl[0]] + [np.concatenate(x) for x in cl[1:]]
    
        yield vl,cl,prefix+'-'+base

import matplotlib.pyplot as plt
clrs = ['g','r','c','m','y','k']

def cmpr(cl_time, vl_time, cl_base):
    ''' Returns 1 (-1) if the cluster event happens after (before)
        the virmenlog event.
        
        cl_time is an index number
        vl_time is ?
        cl_offset'''
    # Compare in seconds since cl_base
    cl_event = cl_time/cl_rate
    vl_event = vl_time*(24*60*60)-(cl_base-vl_base_date).total_seconds()
    
    print 'cl_event:%3f\tvl_event:%.3f'%(cl_event,vl_event)

    #print 'cl_event:%.7f\tvl_event:%.7f'%(vl_time,cl_event,vl_event)
    if cl_event < vl_event:
        return -1
    elif cl_event == vl_event:
        return 0
    else:
        return 1

def match(lst1, lst2a, *lst2bs):
    ''' Matches lst1 to it's location in lst2a and returns
        an array of the lst2b element(s) that correspond
        to that location in lst2a. 
        '''
    # Check that lengths match
    for lst in lst2bs:
        if len(lst) != len(lst2a): raise Exception
    
    
    outs = [[] for _ in range(len(lst2bs))]
    lwr = 0; uppr = 1
    for indx in lst1:
        while uppr < len(lst2a) and not (lst2a[uppr] > indx):
            if lst2a[uppr] >= 0:    # If it is not nan
                lwr = uppr
            uppr += 1

        if uppr == len(lst2a):
            break
        
        ratio = 1.0*(indx-lst2a[lwr])/(lst2a[uppr]-lst2a[lwr])
        for i in range(len(lst2bs)):
            lst2b = lst2bs[i]
            outsky = ratio*(lst2b[uppr]-lst2b[lwr])+lst2b[lwr]
            outs[i].append(outsky)
    return outs

def load_mux(path):
    return loadmat(path)['mux']

def plot_clusters(cl,vl):
    ''''''

    cur_clr = 0

    for clust_num in range(np.min(cl[2]),np.max(cl[2])+1):
        if clust_num in [1]: continue
        if clust_num > 5: break
        
        logging.info('About to weed for clust:%i', clust_num)
        this_clust = []
        for i in range(len(cl[1])):
            if cl[2][i] == clust_num:
                this_clust.append(cl[1][i])
        
        logging.info('About to sort %i indices for cluster %i',len(this_clust),clust_num)
        this_clust.sort()
        
        logging.info('About to determine timestamps for clustered points.')
        tmstmps, = match(this_clust, vl[5], vl[4])


        logging.info('About to sort timestamps')
        tmstmps.sort()
        
        logging.info('About to determine xs and ys.')
        xs,ys = match(tmstmps, vl[1],vl[2],vl[3])

        print 'cluster is len %i'%(len(xs))
        plt.scatter(xs,ys,c=clrs[cur_clr%len(clrs)],label='Cluster %i'%(clust_num,))
        cur_clr+=1

def check_vl(vl):
    if len(vl) != 8: raise Exception('vl0')
    if len(vl[1]) != len(vl[2]): raise Exception
    if len(vl[2]) != len(vl[3]): raise Exception

def check_cl(cl):
    if len(cl) != 3: raise Exception('vl0')
    if len(cl[1]) != len(cl[2]): raise Exception('cl2')

def load_bundle(num, name):
    muxpath = join(dat_base,'Data Files')
    wvpath = join(dat_base,'Data Files','Waveforms','waveform%s'%(num,))
    clpath = join(dat_base,'Data Files','Clusters','clusters%s'%(num,))
    vlpath = join(dat_base,'Data Files','VirmenLog','virmenLog%s'%(num,))
    dat_bundle = [load_mux(join(muxpath,num))]
    
    for path,reader_func in [(wvpath,load_wv),(clpath,load_cl),(vlpath,load_vl)]:
        dat = []
        for filename in listdir(path):
            if filename.find(name) != -1:
                dat.append(reader_func(join(path,filename)))
        dat_bundle.append(dat)
    print 'her'
    return dat_bundle

def get_spikes():
    num = 66
    fn = '20130610T170549'
    tetrode = 1
    
    
    muxpath = join(dat_base,'Data Files')
    
    cl = load_cl(num,fn,tetrode)
    vl = load_vl(num,fn)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    get_spikes()
    import sys; sys.exit()
    
    
    mux,wv,cl,vl = load_bundle('66','20130610T170549')
    import pdb; pdb.set_trace()
    print 'now'
    import sys; sys.exit()
    
    cnt = 0
    for vl,cl2, fn in reconstruct_bundles('66'):

        check_vl(vl)
        check_cl(cl2)
        if np.sum(cl2[2] != 1) == 0:
            print 'continued on:', fn
            continue

        #plt.plot(vl[2],vl[3])
        plot_clusters(cl2, vl)
        plt.legend()
        plt.show()
