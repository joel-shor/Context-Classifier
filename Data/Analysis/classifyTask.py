'''
Created on Mar 23, 2014

@author: jshor
'''
import numpy as np

def get_orientation(vl, cntrx, cntry):
    ''' Returns an array classifying which task the rat
        is performing based on environment data. '''
    x = vl['xs']
    y = vl['ys']
    vx = vl['vxs']
    vy = vl['vys']
    cross_product = (x-cntrx)*vy - (y-cntry)*vx
    return cross_product > 0

def find_runs(task):
    '''Return an array of indices of when the
        runs start, and an array of the length of
        the array'''
    task_ip1 = np.concatenate([task,[task[-1]]])
    task_i = np.concatenate([[1+task[0]],task])
    
    # sgn are the indices of task_i where
    #  task_i[j] != task_i[j+1]
    sgn = np.nonzero(task_ip1 != task_i)[0]
    
    sgn_i = np.concatenate([[sgn[0]],sgn])
    sgn_ip1 = np.concatenate([sgn,[len(task)]])
    
    run_len = (sgn_ip1-sgn_i)[1:]
    
    return sgn, run_len

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from Data.readData import load_mux, load_vl
    num = 66
    session = 60
    
    fn, _= load_mux(num,session)
    vl = load_vl(num,fn)
    task = get_orientation(vl,0,0)
    sgn, run_len = find_runs(task)
    
    n,bins, _ = plt.hist(run_len,bins=range(1,np.max(run_len)+1))
    plt.title('Run length')
    
    import pdb; pdb.set_trace()

    plt.figure()
    plt.hist(run_len,bins=range(1,np.max(run_len)+1),cumulative=-1)
    plt.title('Reverse Cumulative run length')
    plt.show()