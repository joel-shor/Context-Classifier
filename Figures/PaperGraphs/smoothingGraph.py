'''
Created on Mar 29, 2014
Updated on May 25, 2014

@author: jshor

A graph for the paper showing firing rates before and after smoothing.

'''
import logging

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
mpl.rcParams['font.size'] = 28

from Data.readData import load_mux, load_vl, load_cl
from Analysis.countCells import count_cells
from Data.goodClusters import get_good_clusters
from Analysis.spikeRate import get_fracs


def smoothing():
    logging.basicConfig(level=logging.INFO)
    room = [[-55,55],[-55,55]]
    bin_size = 5
    xs = range(room[0][0],room[0][1],bin_size)
    ys = range(room[1][0],room[1][1],bin_size)
    X,Y = np.meshgrid(xs,ys)
    
    session = 60
    animal=66
    _, good_clusters = get_good_clusters(0)
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    x = vl['xs']
    y = vl['ys']
    tpp = np.mean(vl['Time'][1:]-vl['Time'][:-1])*24*60*60
    label_l = vl['Task']
    
    # rates[cell id, lbl, xbin, ybin] = rate
    rates1 = get_fracs(x,y,label_l, room, bin_size, t_cells, smooth_flag=True)
    rates1 /= tpp
    logging.info('Got smoothed rates')
    
    rates2 = get_fracs(x,y,label_l, room, bin_size, t_cells, smooth_flag=False)
    rates2 /= tpp
    logging.info('Got unsmoothed rates')
    
    for i in range(5): # or rates1.shape[0]
        logging.info('Cell %i',i)
        plt.figure()
        plt.pcolor(X,Y,rates1[i,0])
        plt.colorbar()
        plt.autoscale(tight=True)
        plt.xlabel('Position (in)')
        plt.ylabel('Position (in)')


        plt.figure()
        plt.pcolor(rates2[i,0])
        plt.autoscale(tight=True)
        plt.xlabel('Position (in)')
        plt.ylabel('Position (in)')
        plt.show()
        
        


    
