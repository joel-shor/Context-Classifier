'''
Created on Nov 10, 2013

@author: jshor
'''
import logging

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate, place_field
from spikeRateGraph import plot_rates

import numpy as np

def generate_spike_rate_graphs():
    animal = 70
    session = 8
    room_shape = [[-60,60],[-60,60]]
    
    # Jezek uses 2cm x 2cm
    bin_size = 8
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    
    contxt_is = {cntxt:np.nonzero(vl['Task']==cntxt)[0] for cntxt in np.unique(vl['Task'])}
    
    for tetrode in range(1,17):
        spks = {}
        cl = load_cl(animal,fn,tetrode)
        
        for wanted_cl in range(2,100):
            logging.info('Finding spike locations for cell %i, tetrode %i',wanted_cl,tetrode)
            cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,wanted_cl, animal, session)
            spk_i = spike_loc(cl, vl, trigger_tm, wanted_cl,cache_key)
            if spk_i is np.NAN: break
            spks[wanted_cl] = {}
            for contxt in contxt_is.keys():
                spk_i_cur = np.intersect1d(contxt_is[contxt], spk_i)
                spks[wanted_cl][contxt] = spk_i_cur
            
        tot_spks = len(spks)
    
        rate_dict = {contxt:{} for contxt in contxt_is.keys()}

        for wanted_cl, i in zip(spks.keys(), range(tot_spks)):
            for contxt in contxt_is.keys():
                rates = spike_rate(room_shape,vl,spks[wanted_cl][contxt],
                                   bin_size,valid=contxt_is[contxt])
                rate_dict[contxt][i+2] = rates
            logging.info('Processed firing rates for cluster %i', i+2)
            #plot_rates(Xs,Ys,place_field(rates),i+2)

        for contxt in contxt_is.keys():
            if len(rate_dict[contxt]) == 0: continue
            plt.figure('contour')
            plt.clf()
            plt.suptitle('Spike Rate: Animal %i, Tetrode %i, Bin size %i, Session %i, Context %i,1'%(animal,tetrode,bin_size,session,contxt))
            plt.figure('pcolor')
            plt.clf()
            plt.suptitle('Spike Rate: Animal %i, Tetrode %i, Bin size %i, Session %i, Context %i,2'%(animal,tetrode,bin_size,session,contxt))
     
            for clusters, rates in rate_dict[contxt].items():
                plot_rates(room_shape, tot_spks, bin_size, rates,clusters)
    
            #plt.show()
            ''''''
            plt.figure('contour')
            plt.savefig('GenerateFigures/Images/Context Spike Rates/Animal %i/Bin size %i/Type 1/Tetrode %i, Session %i, Context %i'%(animal,bin_size,tetrode,session,contxt))
            plt.figure('pcolor')
            plt.savefig('GenerateFigures/Images/Context Spike Rates/Animal %i/Bin size %i/Type 2/Tetrode %i, Session %i, Context %i'%(animal,bin_size,tetrode,session,contxt))