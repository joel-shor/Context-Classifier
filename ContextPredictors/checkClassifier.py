import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.countCells import count_cells


def check_classifier(Classifier, good_clusters, label, K, bin_size, animal, session):
    room_shape = [[-60,60],[-60,60]]
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    
    if label == 'Task':
        label_l = vl['Task']
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    X, Y = gpv(vl, t_cells, room_shape, bin_size, label_l, K)
    
    classifier = Classifier(X,Y)
    
    correct_dp = []
    
    for i in range(len(Y)):
        sbin = X[i,-1]
        x = X[i,:-1]
        y = Y[i,0]
        result = classifier.classify(sbin,x)
        correct_dp.append(result[y])
    
    # Process
    correct_dp = np.array(correct_dp)
    
    return correct_dp