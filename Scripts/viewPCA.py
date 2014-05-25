'''
Created on May 4, 2014

@author: jshor
'''
from sklearn.decomposition import PCA
from itertools import product

from Data.readData import load_mux, load_vl, load_cl
import numpy as np
from Data.goodClusters import get_good_clusters
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.ByTime import gpv
from Analysis.countCells import count_cells
from Cache.cache import try_cache
import logging

from matplotlib import pyplot as plt

def view_PCA():
    animal=66
    session=60
    bin_size=5
    
    K = 50 # Segment length used to calculate firing rates
    label = 'Task'
    room = [[-55,55],[-55,55]]
    _, good_clusters = get_good_clusters(0)
    xbins = (room[0][1]-[0][0])/bin_size
    ybins = (room[1][1]-[1][0])/bin_size
    
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    
    if label == 'Task':
        label_l = vl['Task']
    else:
        raise Exception('Not implemented yet.')
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    logging.info('About to generate population vector.')
    #X, Y = gpv(vl, t_cells, label_l, K)
    X, Y = gpv(vl, t_cells, label_l, K, bin_size, room)
    
    pcas = np.zeros([xbins,ybins])
    for xbin,ybin in product(xbins,ybins):
        pca = PCA()
        Xtmp = np.zeros([X.shape[0],])
        X = pca.fit_transform(X[:,:len(t_cells)])
        pcas[xbin,ybin] = pca
    
        plt.plot(pca.explained_variance_ratio_)
        print pca.components_
        plt.show()