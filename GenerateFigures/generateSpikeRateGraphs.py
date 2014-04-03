'''
Created on Nov 10, 2013

@author: jshor
'''
import logging

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate, place_field

import numpy as np
clrs = ['b','g','r','c','m','k','b','g','r','c','m','k',]

def get_subplot_size(gs):
    sqr = int(np.ceil(np.sqrt(gs)))
    return sqr, sqr
    for x in range(sqr,2,-1):
        if gs%sqr == 0:
            return x, gs/x
    return sqr, int(np.ceil(1.0*gs/sqr))

def plot_rates(Xs, Ys, rates, cluster):
    cntr = plt.contourf(Ys,Xs,rates)
    plt.colorbar(cntr, extend='both')
    plt.title('Cluster %i'%(cluster,))
    plt.tick_params(\
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off') # labels along the bottom edge are off
    plt.tick_params(\
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelleft='off') # labels along the bottom edge are off

def generate_spike_rate_graphs():
    animal = 66
    session = 60 # This is August 7, 2013 run
    room_shape = [[-60,60],[-60,60]]
    bin_size = 2
    
    x = np.arange(room_shape[0][0],room_shape[0][1],bin_size)
    y = np.arange(room_shape[1][0],room_shape[1][1],bin_size)
    Xs, Ys = np.meshgrid(x, y)
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    
    for tetrode in range(1,2):
    #for tetrode in [7]:    
        fn, trigger_tm = load_mux(animal, session)
        cl = load_cl(animal,fn,tetrode)
        vl = load_vl(animal,fn)
    
        spk_is = []
        for wanted_cl in range(2,100):
            spk_i = spike_loc(cl, vl, trigger_tm, wanted_cl)
            if spk_i is np.NAN: break
            spk_is.append(spk_i)

        tot_spks = len(spk_is)
        subp_x, subp_y = get_subplot_size(tot_spks)

        plt.figure()
        for spk_i, i in zip(spk_is, range(tot_spks)):
            plt.subplot(subp_x,subp_y, i+1)
            rates = spike_rate(room_shape,vl,spk_i,bin_size)
            logging.info('Processed firing rates for cluster %i', i+2)
            #plot_rates(Xs,Ys,place_field(rates),i+2)
            plot_rates(Xs,Ys,rates,i+2)
            
        #plt.suptitle('Place Fields: Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
        #plt.show()
        #plt.savefig('GenerateFigures/Images/Place Fields/Animal %i, Tetrode %i, Session %i: Place Fields'%(animal,tetrode,session))
        
        plt.suptitle('Spike Rates: Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
        plt.show()
        #plt.savefig('GenerateFigures/Images/Spike Rate/Animal %i, Tetrode %i, Session %i: Spike Rate'%(animal,tetrode,session))
        
