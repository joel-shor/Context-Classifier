'''
Created on May 4, 2014

@author: jshor
'''
from sklearn.decomposition import PCA

from Data.readData import load_mux, load_vl, load_cl
import numpy as np
from Data.goodClusters import get_good_clusters
from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
from Data.Analysis.countCells import count_cells
from cache import try_cache
import logging

from matplotlib import pyplot as plt

def view_PCA():
    animal=66
    session=60

    K = 50 # Segment length used to calculate firing rates
    cl_prof = 0
    label = 'Task'

    _, good_clusters = get_good_clusters(cl_prof)
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    
    if label == 'Task':
        label_l = vl['Task']
    else:
        raise Exception('Not implemented yet.')
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    logging.info('About to generate population vector.')
    X, Y = gpv(vl, t_cells, label_l, K)
    
    pca = PCA(n_components=4)
    X = pca.fit_transform(X[:,:-2])
    import pdb; pdb.set_trace()
    
    plt.plot(pca.explained_variance_ratio_)
    print pca.components_
    plt.show()