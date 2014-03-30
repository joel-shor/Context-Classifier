from pygasp.fft import fftFilters
from scipy.fftpack import fft, ifft

import numpy as np

def bandfilt(wv,cutoffLow=4,cutoffHigh=11,sampleFreq=31250):
    ft = fft(wv)
    fftFilters.bandpass(ft,samplingFreq=sampleFreq,
                        cutoffLow=cutoffLow,
                        cutoffHigh=cutoffHigh)
    wv = ifft(ft)
    return np.real(wv)

def fourierfilt(wv):
    ''' A hard cutoff in Fourier space. '''
    from matplotlib import pyplot as plt
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