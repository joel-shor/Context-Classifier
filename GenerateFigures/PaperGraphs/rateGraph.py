'''
Created on Nov 10, 2013

@author: jshor
'''
import logging

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.spikeRate import spike_rate

import numpy as np

import matplotlib as mpl


def rate_graph():
    #mpl.rcParams['axes.titlesize'] = 18
    #mpl.rcParams['axes.labelsize'] = 18
    mpl.rcParams['font.size'] = 26
    
    
    animal = 66
    session = 60
    room_shape = [[-55,55],[-55,55]]
    
    # Jezek uses 2cm x 2cm
    bin_size = 5
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    
    contxt_is = {cntxt:np.nonzero(vl['Task']==cntxt)[0] for cntxt in np.unique(vl['Task'])}
    
    #for tetrode in range(1,17):
    for tetrode in [1]:
        spks = {}
        cl = load_cl(animal,fn,tetrode)
        
        #for wanted_cl in range(2,100):
        for wanted_cl in range(2,9):
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
            
            plt.figure(figsize=(10,10))
            x = np.concatenate([np.arange(room_shape[0][0],room_shape[0][1],bin_size),[room_shape[0][1]]])
            y = np.concatenate([np.arange(room_shape[1][0],room_shape[1][1],bin_size),[room_shape[1][1]]])
            Xs, Ys = np.meshgrid(x, y)
            cntr = plt.pcolor(Ys,Xs,rate_dict[contxt][2])
            
            t=plt.colorbar(cntr, extend='both')
            t.set_label('Frequency (Hz)')
            plt.xlabel('Position (in)')
            plt.ylabel('Position (in)')
            if contxt == 1: plt.title('Clockwise')
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
        