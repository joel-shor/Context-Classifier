from Data.readData import load_mux, load_wv
from matplotlib import pyplot as plt
from SignalProcessing.filter import bandfilt

import numpy as np

num = 66
session = 60
tetrode = 1

fn, _ = load_mux(num,session)
wv = load_wv(num,fn,tetrode)

for i in range(wv.shape[1]):
    plt.figure()
    plt.plot(wv[:,1])
    shower = bandfilt(wv[:,i])
    plt.figure()
    plt.plot(shower)
    
    wideband = bandfilt(wv[:,i],10**-5,125)
    wideb_mean = np.mean(wideband)
    print wideb_mean
    shower[np.nonzero(shower < 5*wideb_mean)[0]] = 0
    plt.figure()
    plt.plot(shower)


    plt.show()