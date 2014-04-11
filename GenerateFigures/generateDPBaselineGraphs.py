'''
Created on Apr 11, 2014

@author: jshor
'''
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from matplotlib import pyplot as plt
from ContextPredictors.DotProduct import DotProduct as Classifier

def generate_dp_baseline_graphs():
    animal = 66
    session = 60 # This is August 7, 2013 run
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = [load_cl(animal,fn,tetrode) for tetrode in range(1,3)]
    
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 10
    cls = Classifier(vl,cls, trigger_tm, room_shape, bin_size)
    baseline_similarity = np.zeros(cls.base_vec.shape[:2])
    for i,j in zip(range(cls.base_vec.shape[0]),range(cls.base_vec.shape[1])):
        print cls.base_vec[i,j,0,:]
        print 'times'
        print cls.base_vec[i,j,1,:]
        baseline_similarity[i,j] = np.sum(cls.base_vec[i,j,0,:]*cls.base_vec[i,j,1,:])
    
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