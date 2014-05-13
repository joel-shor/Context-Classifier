import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from Data.Analysis.countCells import count_cells
from time import time

from ContextPredictors.GeneratePopulationVectors.ByTime import gpv
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByBin import gpv


def check_classifier(Classifier, good_clusters, label, K, bin_size, 
                     animal, session):
    room_shape = [[-55,55],[-55,55]]
    
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
    s=time()
    X, Y = gpv(vl, t_cells, label_l, K, bin_size, room_shape)
    logging.info('%i population vectors generated in %.3f.',X.shape[0],time()-s)
    Y = Y.reshape([-1])

    classifier = Classifier(X,Y, room_shape, bin_size)
    
    correct_dp = []
    
    for i in range(len(Y)):
        x = X[i,:]
        y = Y[i]
        result = classifier.classify(x)
        correct_dp.append(result[y])
    
    # Process
    correct_dp = np.array(correct_dp)
    
    return correct_dp