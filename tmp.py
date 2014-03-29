from Data.readData import load_mux, load_wv
from matplotlib import pyplot as plt
from pygasp.fft import fftFilters
from scipy.fftpack import fft, ifft

import numpy as np

#freq = 31250.0
freq=100.0

def bandfilt(wv):
    ft = fft(wv)
    #plt.plot(np.absolute(ft))
    #plt.show()
    fftFilters.bandpass(ft,samplingFreq=freq,cutoffLow=4,cutoffHigh=11)
    #plt.plot(np.absolute(ft))
    #plt.show()
    wv = ifft(ft)
    return wv

def fourierfilt(wv):
    ft = fft(wv)
    start = 4.0*len(wv)/100
    stop = 11.0*len(wv)/100

    tmper = np.copy(ft)
    plt.plot(tmper)
    plt.show()

    ft = np.concatenate([np.zeros(start),ft[start:stop],np.zeros(len(wv)/2-stop)])
    import pdb; pdb.set_trace()
    ft = np.concatenate([ft,ft[::-1]-2*np.imag(ft[::-1])])

    plt.figure()
    plt.plot(tmper-ft)
    plt.plot(ft)
    
    plt.show()

    wv = ifft(ft)
    return np.real(wv)

def tmp():
    x = np.arange(0,100,1/freq)
    wv1 = np.cos(2*np.pi*x) # Freq = 1
    wv2 = np.cos(2*np.pi*x*7.0) # Freq = 7
    wv = wv1+wv2
    #wv = wv1
    
    
    plt.plot(x,wv1)
    
    out = np.real(bandfilt(wv))
    plt.plot(x,out,label='filtered')
    print np.sum(out-wv1)
    #plt.figure()
    #plt.plot(x,fourierfilt(wv)) 
    
    plt.legend()
    plt.show()
    import sys; sys.exit()

tmp()
num = 66
session = 60
tetrode = 1

fn, _ = load_mux(num,session)
wv = load_wv(num,fn,tetrode)

for i in range(wv.shape[1]):
    plt.figure()
    plt.plot(wv[:,1])
    shower = np.absolute(bandfilt(wv[:,i]))
    plt.figure()
    plt.plot(shower)
    plt.show()