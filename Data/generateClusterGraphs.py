'''
Created on Nov 10, 2013

@author: jshor
'''
from readData import load_cl, load_wv, load_mux, load_vl
import numpy as np
import logging
from matplotlib import pyplot as plt
from getClusters import spike_loc

def get_subplot_size(gs):
    sqr = int(np.ceil(np.sqrt(gs)))
    return sqr, sqr
    for x in range(sqr,2,-1):
        if gs%sqr == 0:
            return x, gs/x
    return sqr, int(np.ceil(1.0*gs/sqr))

def plot_spks(vl, spk_i, wanted_cl):
    plt.plot(vl['xs'],vl['ys'],zorder=1,color='y')
    plt.scatter(vl['xs'][spk_i],vl['ys'][spk_i],zorder=2,color=clrs.pop())
    plt.title('Cluster %i'%(wanted_cl,))
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    session = 60 # This is August 7, 2013 run

    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    
    for tetrode in range(1,17):
        clrs = ['b','g','r','c','m','k','b','g','r','c','m','k',]
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
        print subp_x, subp_y
        plt.figure()
        for spk_i, i in zip(spk_is, range(tot_spks)):
            plt.subplot(subp_x,subp_y, i+1)
            plot_spks(vl, spk_i, i+2)
        plt.suptitle('Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
        #plt.show()
        plt.savefig('Images/Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
    
    