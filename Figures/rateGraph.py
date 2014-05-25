'''
Created on Nov 10, 2013

@author: jshor
'''
from matplotlib import pyplot as plt
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from Analysis.spikeRate import get_fracs
from Data.goodClusters import get_good_clusters
from Analysis.countCells import count_cells
from Figures.rateGraphLib import plot_rates


def rate_graph():
    animal = 66
    session = 60 # This is August 7, 2013 run
    room_shape = [[-55,55],[-55,55]]
    tetrodes = range(1,17)
    cluster_profile = 0
    bin_size = 5
    
    
    _, good_clusters = get_good_clusters(cluster_profile)
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in tetrodes}
    tpp = 1.0*np.mean(vl['Time'][1:]-vl['Time'][:-1])
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    label_l = vl['Task']
    
    # rates[cell, lbl, xbin, ybin] = firing rate
    rates = get_fracs(vl['xs'], vl['ys'], label_l, room_shape, bin_size, t_cells)
    rates /= tpp
    
    plot_rates(rates,label_l,t_cells)
        
    plt.show()
    #plt.savefig('GenerateFigures/Images/Spike Rate Diffs/Type 2/Spike Rate Diff: Animal %i, Tetrode %i, Session %i,2'%(animal,tetrode,session))
