'''
Created on Apr 11, 2014

@author: jshor
'''
import numpy as np
from itertools import product as pc

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from ContextPredictors.DotProduct import DotProduct as Classifier

def generate_dp_baseline_graphs():
    animal = 66
    session = 60 # This is August 7, 2013 run
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,16)}
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    
    # Actual Contexts
    labels = np.unique(vl['Task'])
    label_is = {contxt: np.nonzero(vl['Task']==contxt)[0] for contxt in labels}
    
    
    clsfr = Classifier(vl,cls,trigger_tm, label_is, room_shape, bin_size)
    baseline_similarity = np.zeros(clsfr.base_vec.shape[:2])
    for i,j in pc(range(clsfr.base_vec.shape[0]),range(clsfr.base_vec.shape[1])):
        baseline_similarity[i,j] = np.dot(clsfr.base_vec[i,j,0,:],clsfr.base_vec[i,j,1,:])
    
    if True:
        x = np.concatenate([np.arange(room_shape[0][0],room_shape[0][1],bin_size),[room_shape[0][1]]])
        y = np.concatenate([np.arange(room_shape[1][0],room_shape[1][1],bin_size),[room_shape[1][1]]])
        Xs, Ys = np.meshgrid(x, y)
        contour = plt.pcolor(Xs,Ys,baseline_similarity)
    else:
        x = np.arange(room_shape[0][0],room_shape[0][1],bin_size)
        y = np.arange(room_shape[1][0],room_shape[1][1],bin_size)
        Xs, Ys = np.meshgrid(x, y)
        contour = plt.contourf(Xs,Ys,baseline_similarity)
    plt.colorbar(contour, extend='both')
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
    plt.show()