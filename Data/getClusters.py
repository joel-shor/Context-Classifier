'''
Created on Nov 10, 2013

@author: jshor
'''
from readData import load_cl, load_wv, load_mux, load_vl
import numpy as np
from datetime import datetime
import logging
from matplotlib import pyplot as plt

cl_rate = 31250.0

def _datenum(dt):
    ''' Takes a python datetime.datetime and converts it to
        a Matlab serial date number ie the number of (fractional)
        days since January 0,0000 '''
    reference = datetime(year=1,month=1,day=1)
    delt = dt-reference
    return delt.total_seconds()/(60.0*60*24) + 365 + 1 \
                + 1 # Need an extra 1 to match Matlab's output...?

def spike_loc(cl, vl, trigger_dt, wanted_cl):
    
    if wanted_cl == 1:
        logging.warning('Are you SURE you want to plot cluster 1?')
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN
    
    # Get the times when a cluster in label 'wanted_cl' occurs
    st = cl['Time'][cl['Label']==wanted_cl].astype(np.float)
    if st.shape == (0,):
        logging.warning('No clusters with label %i. Quitting...', wanted_cl)
        return np.NAN
    
    st /= (31250.0*24*60*60)
    st += _datenum(trigger_dt)
    
    # Clean up the virmenLog iterations numbers by removing the
    #  nan ones and linearly interpolating between them
    f = np.nonzero(~np.isnan(vl['Iter num']))[0]
    y = np.interp(range(len(vl['Iter num'])), f, vl['Iter num'][f])
    #y = np.round(y,0).astype(int)
    y = y.astype(int)
    
    
    logging.info('%i pts in cluster %i',len(st),wanted_cl)
    if 1.0*len(st)/len(cl['Label']) > .05:
        logging.warning('Are you SURE you want to proceed?')
        y = raw_input()
        if y in ['n', 'N']:
            return np.NAN

    # Determine the iteration number at which each spike occured
    spk_i = np.zeros(st.shape)
    for ndx in range(len(st)):
        try:
            # Find iteration preceeding spike
            f = np.nonzero(vl['Iter time'] < st[ndx])[0][-1] # Take the last one
            
            # Make sure there is an iteration following the spike
            np.nonzero(vl['Iter time'] > st[ndx])[0][0]
            
            spk_i[ndx] = y[f]
        except:
            # If nonzero is empty, the spike occurred before the first
            #  or after the last spike
            spk_i[ndx] = np.NAN
    
    # Delete NaN values
    spk_i = spk_i[~np.isnan(spk_i)].astype(int)
    
    # Determine speed
    speed = np.sqrt(vl['vxs']**2+vl['vys']**2)
    
    # Only leave spikes when rat is running faster than 2 in /sec
    spk_i = np.intersect1d(spk_i, np.nonzero(speed > 2)[0])

    return spk_i

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
    #tetrode = 5
    session = 59 # This is August 7, 2013 run
    
    # Filenames (fn) are named descriptively:
    # session 18:14:04 on day 10/25/2013
    # load virmenLog75\20131025T181404.cmb.mat
    
    for tetrode in range(1,17):
        clrs = ['b','g','r','c','m','k','b','g','r','c','m','k',]
        fn, trigger_dt, _ = load_mux(animal, session)
        cl = load_cl(animal,fn,tetrode)
        vl = load_vl(animal,fn)
    
        spk_is = []
        for wanted_cl in range(2,100):
            spk_i = spike_loc(cl, vl, trigger_dt, wanted_cl)
            if spk_i is np.NAN: break
            spk_is.append(spk_i)

        tot_spks = len(spk_is)
        subp_x, subp_y = get_subplot_size(tot_spks)
        print subp_x, subp_y
        plt.figure()
        for spk_i, i in zip(spk_is, range(tot_spks)):
            plt.subplot(subp_x,subp_y, i+1)
            plot_spks(vl, spk_i, i+1)
        plt.suptitle('Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
        #plt.show()
        plt.savefig('Animal %i, Tetrode %i, Session %i'%(animal,tetrode,session))
    
    