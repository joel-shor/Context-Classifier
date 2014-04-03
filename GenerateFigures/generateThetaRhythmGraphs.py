from matplotlib import pyplot as plt
from Data.readData import load_mux, load_wv
from Data.Analysis.filter import bandfilt
#from scipy.ndimage.filters import gaussian_filter as gf
from scipy.ndimage.filters import maximum_filter1d as gf
import numpy as np

def find_min_indices(signal):
    arr1 = np.concatenate([[True],signal[1:] < signal[:-1]])
    arr2 = np.concatenate([signal[:-1] < signal[1:],[True]])
    arr = np.logical_and(arr1,arr2)
    inds = np.nonzero(arr)[0]
    return inds

def generate_theta_rhythm_graphs():
    animal = 66
    session = 60
    tetrode = 4
    
    fn, _= load_mux(animal,session)
    wv = load_wv(animal,fn, tetrode)
    
    # Get theta rhythm
    #  Smooth to get rid of sub oscillations
    #thet = [gf(bandfilt(wv[:,i]),150) for i in range(4)]
    
    
    # Find local mins
    thet = [gf(bandfilt(wv[:,i]),5) for i in range(4)]
    mins= [find_min_indices(thet[i]) for i in range(4)]
    
    # Find local maxes
    thet = [gf(bandfilt(-1*wv[:,i]),5) for i in range(4)]
    maxs = [find_min_indices(thet[i]) for i in range(4)]
    
    for i_s in [mins,maxs]:
        for arr in i_s:
            arr = np.array(arr)
            if np.sum(arr[1:]-arr[:-1] < 5) > 0:
                print 'Min/max too close'
                import pdb; pdb.set_trace()
                #raise Exception('Min max calculation wrong')
    
    plt.figure()
    plt.subplot(4,1,1)

    for i in range(4):
        print 'plt %i has %i pts min, %i pts max'%(i, len(mins[i]),len(maxs[i]))
        plt.subplot(4,1,i+1)
        plt.plot(thet[i])
        plt.vlines(mins[i],np.min(thet[i]),np.max(thet[i]),color='r')
        plt.vlines(maxs[i],np.min(thet[i]),np.max(thet[i]),color='g')
        plt.xlim(0,len(thet[i]))
    plt.suptitle('Theta rhythm for Animal:%i, Session:%i, Tetrode:%i'%(animal,session,tetrode))
    #plt.tight_layout()
    plt.show()