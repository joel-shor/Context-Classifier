'''
Created on Nov 10, 2013

@author: jshor
'''
from Data.readData import load_cl, load_mux, load_vl
import numpy as np
from matplotlib import pyplot as plt
from Analysis.getClusters import spike_loc

clrs = ['b','g','r','c','m','k','b','g','r','c','m','b']

def get_subplot_size(gs):
    sqr = int(np.ceil(np.sqrt(gs)))
    return sqr, sqr
    for x in range(sqr,2,-1):
        if gs%sqr == 0:
            return x, gs/x
    return sqr, int(np.ceil(1.0*gs/sqr))

def plot_spks(vl, spk_i, wanted_cl,clr):
    plt.plot(vl['xs'],vl['ys'],zorder=1,color='k')
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

def cluster_graphs():
    animal = 70
    session = 8
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    
    #for tetrode in range(1,17):  
    for tetrode in [13]:  
        for context in [1,-1]:
            global clrs
            clrs = ['b','g','r','c','m','k','b','g','r','c','m','k']
            
            fn, trigger_tm = load_mux(animal, session)
            cl = load_cl(animal,fn,tetrode)
            vl = load_vl(animal,fn)
        
            spk_is = []
            #for cell in range(2,100):
            for cell in [3]:
                cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,cell)
                spk_i = spike_loc(cl, vl, trigger_tm, cell,cache_key)
                if spk_i is np.NAN: break
                cntx_is = np.nonzero(vl['Task']==context)[0]
                spk_i = np.intersect1d(cntx_is, spk_i)
                spk_is.append(spk_i)
    
            tot_spks = len(spk_is)
            if tot_spks == 0: continue
            subp_x, subp_y = get_subplot_size(tot_spks)
            #plt.figure()
            for spk_i, i in zip(spk_is, range(tot_spks)):
                plt.subplot(subp_x,subp_y, i+1)
                if context==1: 
                    plt.plot(vl['xs'],vl['ys'],zorder=1,color='k')
                    plt.scatter(vl['xs'][spk_i],vl['ys'][spk_i],zorder=2,color='b',
                                label='Clockwise')
                else:
                    plt.scatter(vl['xs'][spk_i],vl['ys'][spk_i],zorder=2,color='r',
                                label='Counterclockwise')
    
                #plot_spks(vl, spk_i, i+2)
            #plt.suptitle('Animal %i, Tetrode %i, Session %i, Context:%i'%(animal,tetrode,session,context))
            
            plt.xlim([-60,60])
            plt.ylim([-60,60])
            plt.xlabel('Position (in)')
            plt.ylabel('Position (in)')
        plt.show()
            #plt.savefig('GenerateFigures/Images/Context Spike Location/Animal %i, Tetrode %i, Session %i, Context:%i'%(animal,tetrode,session,context))

    