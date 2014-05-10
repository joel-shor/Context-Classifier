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

def generate_diff_spike_rate_graphs():
    animal = 66
    session = 60 # This is August 7, 2013 run
    room_shape = [[-55,55],[-55,55]]
    
    # Jezek uses 2cm x 2cm
    bin_size = 5
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    
    contxt_is = {cntxt:np.nonzero(vl['Task']==cntxt)[0] for cntxt in np.unique(vl['Task'])}
    
    for tetrode in range(1,2):
        spks = {}
        cl = load_cl(animal,fn,tetrode)
        
        for wanted_cl in range(2,20):
            logging.info('Finding spike locations for cell %i, tetrode %i',wanted_cl,tetrode)
            cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,wanted_cl)
            spk_i = spike_loc(cl, vl, trigger_tm, wanted_cl,key=cache_key)
            if spk_i is np.NAN: break
            spks[wanted_cl] = {}
            for contxt in contxt_is.keys():
                spk_i_cur = np.intersect1d(contxt_is[contxt], spk_i)
                spks[wanted_cl][contxt] = spk_i_cur
            
        tot_spks = len(spks)
    
        plt.figure('contour')
        plt.clf()
        plt.suptitle('Spike Rate Diff: Animal %i, Tetrode %i, Session %i,1'%(animal,tetrode,session))
        plt.figure('pcolor')
        plt.clf()
        plt.suptitle('Spike Rate Diff: Animal %i, Tetrode %i, Session %i,2'%(animal,tetrode,session))

        for wanted_cl, i in zip(spks.keys(), range(tot_spks)):
            tmp  = []
            for contxt in contxt_is.keys():
                rates = spike_rate(room_shape,vl,spks[wanted_cl][contxt],
                                   bin_size,valid=contxt_is[contxt])
                tmp.append(rates)
            rate_diff = np.absolute(tmp[0]-tmp[1])
            logging.info('Processed firing rates for cluster %i', i+2)
            #plot_rates(Xs,Ys,place_field(rates),i+2)
            plot_rates(room_shape, tot_spks, bin_size, rate_diff,i+2)

        plt.show()
        
        plt.figure('contour')
        #plt.savefig('GenerateFigures/Images/Spike Rate Diffs/Type 1/Spike Rate Diff: Animal %i, Tetrode %i, Session %i,1'%(animal,tetrode,session))
        plt.figure('pcolor')
        #plt.savefig('GenerateFigures/Images/Spike Rate Diffs/Type 2/Spike Rate Diff: Animal %i, Tetrode %i, Session %i,2'%(animal,tetrode,session))
