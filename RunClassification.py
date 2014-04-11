'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_wv, load_cl
from ContextPredictors.PiecewiseHMM import PiecewiseHMM
from ContextPredictors.DotProduct import DotProduct as Classifier

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    session = 60 # This is August 7, 2013 run
    tetrode=3
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = [load_cl(animal,fn,tetrode) for tetrode in range(1,3)]
    
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    cls = Classifier(vl,cls, trigger_tm, room_shape, bin_size)
    baseline_similarity = np.zeros(cls.base_vec.shape[:2])
    for i,j in zip(range(cls.base_vec.shape[0]),range(cls.base_vec.shape[1])):
        baseline_similarity[i,j] = np.sum(cls.base_vec[i,j,0,:]*cls.base_vec[i,j,1,:])
    
    from matplotlib import pyplot as plt
    
    x = np.arange(room_shape[0][0],room_shape[0][1],bin_size)
    y = np.arange(room_shape[1][0],room_shape[1][1],bin_size)
    Xs, Ys = np.meshgrid(x, y)
    plt.contourf(Xs,Ys,baseline_similarity)
    plt.show()