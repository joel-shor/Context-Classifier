'''
Created on Apr 16, 2014

@author: jshor
'''
from matplotlib import pyplot as plt
import numpy as np

def plot_rates(room_shape, tot_spks, bin_size, rates, cluster):
    subp_x, subp_y = get_subplot_size(tot_spks)
    
    plt.figure('pcolor')
    plt.subplot(subp_x,subp_y,cluster-1)
    x = np.concatenate([np.arange(room_shape[0][0],room_shape[0][1],bin_size),[room_shape[0][1]]])
    y = np.concatenate([np.arange(room_shape[1][0],room_shape[1][1],bin_size),[room_shape[1][1]]])
    Xs, Ys = np.meshgrid(x, y)
    cntr = plt.pcolor(Ys,Xs,rates)
    
    plt.colorbar(cntr, extend='both')
    plt.title('Cluster %i'%(cluster,))
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
    
    plt.figure('contour')
    plt.subplot(subp_x,subp_y,cluster-1)
    x = np.arange(room_shape[0][0],room_shape[0][1],bin_size)
    y = np.arange(room_shape[1][0],room_shape[1][1],bin_size)
    Xs, Ys = np.meshgrid(x, y)
    cntr = plt.contourf(Ys,Xs,rates)
    
    plt.colorbar(cntr, extend='both')
    plt.title('Cluster %i'%(cluster,))
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