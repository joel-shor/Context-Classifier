'''
Created on Nov 10, 2013

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from Data.Analysis.spikeRate import get_rates
from Data.Analysis.countCells import count_cells
from Data.goodClusters import get_good_clusters

import matplotlib as mpl


def rate_graph():
    #mpl.rcParams['axes.titlesize'] = 18
    #mpl.rcParams['axes.labelsize'] = 18
    mpl.rcParams['font.size'] = 26
    
    
    animal = 66
    session = 60 # This is August 7, 2013 run
    room_shape = [[-55,55],[-55,55]]
    tetrodes = [1]
    cluster_profile = 0
    bin_size = 5
    
    
    _, good_clusters = get_good_clusters(cluster_profile)
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in tetrodes}
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    label_l = vl['Task']
    
    # rates[cell, lbl, xbin, ybin] = firing rate
    rates = get_rates(vl['xs'], vl['ys'], label_l, room_shape, bin_size, t_cells)


        
    for lbl in np.unique(label_l):
        
        plt.figure(figsize=(10,10))
        x = np.concatenate([np.arange(room_shape[0][0],room_shape[0][1],bin_size),[room_shape[0][1]]])
        y = np.concatenate([np.arange(room_shape[1][0],room_shape[1][1],bin_size),[room_shape[1][1]]])
        Xs, Ys = np.meshgrid(x, y)
        cntr = plt.pcolor(Ys,Xs,rates[2,lbl])
        
        t=plt.colorbar(cntr, extend='both')
        t.set_label('Frequency (Hz)')
        plt.xlabel('Position (in)')
        plt.ylabel('Position (in)')
        if lbl == 1: plt.title('Clockwise')
        else: plt.title('Counterclockwise')
        
        #plt.axis('equal')
        plt.xlim(room_shape[0])
        plt.ylim(room_shape[1])

        '''
        plt.figure()
        x = np.arange(room_shape[0][0],room_shape[0][1],bin_size)
        y = np.arange(room_shape[1][0],room_shape[1][1],bin_size)
        Xs, Ys = np.meshgrid(x, y)
        cntr = plt.contourf(Ys,Xs,rate_dict[contxt][2])
        t = plt.colorbar(cntr, extend='both')
        t.set_label('Frequency (Hz)')
        plt.xlabel('Position (in)')
        plt.ylabel('Position (in)')'''
    plt.show()
    