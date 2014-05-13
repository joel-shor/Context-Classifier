'''
Created on Apr 16, 2014

@author: jshor
'''
from matplotlib import pyplot as plt
import numpy as np

def plot_rates(rates,Y,t_cells):
    labels = np.unique(Y)
    grd = 2
    for lbl in range(len(labels)):
        plt.figure()
        plt.subplot(grd,grd,0)
        for i in range(grd**2):
            plt.subplot(grd,grd,i)
            plt.pcolor(rates[i,lbl,:,:])
            tetrode,cell = t_cells.keys()[i]
            plt.title('(%i,%i,%i)'%(tetrode,cell,labels[lbl]))
            plt.colorbar()
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
    
def get_subplot_size(gs):
    sqr = int(np.ceil(np.sqrt(gs)))
    return sqr, sqr
    for x in range(sqr,2,-1):
        if gs%sqr == 0:
            return x, gs/x
    return sqr, int(np.ceil(1.0*gs/sqr))