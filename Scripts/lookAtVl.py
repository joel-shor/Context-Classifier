'''
Created on May 14, 2014

@author: jshor
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from Data.readData import load_mux, load_vl, load_cl
from Analysis.countCells import count_cells
from Data.goodClusters import get_good_clusters

def vl_look():
    mpl.rcParams['font.size'] = 26
    animal=66
    session=60
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    print 'npw'
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    _, good_clusters = get_good_clusters(0)
    print 'kw'
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    print 'w'
    
    L1 = 59
    L2 = 70
    clusters = [[] for _ in range(L2-L1)]
    for cell, spk_i in t_cells.items():
        spk_i = np.unique(spk_i)
        for spk in np.nonzero((spk_i<L2) & (spk_i>=L1))[0]:
            clusters[spk_i[spk]-L1].append(cell)
    
    out = zip(clusters,
              vl['xs'][L1:L2],
              vl['ys'][L1:L2],
              vl['vxs'][L1:L2],
              vl['vys'][L1:L2])
    
    for tt in out:
        print '%s, (%.1f,%.1f), (%.1f,%.1f)'%(  (str(tt[0]),) + tt[1:])
    import pdb; pdb.set_trace()
