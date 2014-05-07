import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.countCells import count_cells


def check_classifier(Classifier, good_clusters, label, K, bin_size, 
                     animal, session):
    room_shape = [[-60,60],[-60,60]]
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    
    if label == 'Task':
        label_l = vl['Task']
    else:
        raise Exception('Not implemented yet.')
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    if len(t_cells) == 0: raise Exception('No cells found')
    
    logging.info('About to generate population vector.')
    X, Y = gpv(vl, t_cells, label_l, K)
    
    classifier = Classifier(X,Y, room_shape, bin_size)
    
    correct_dp = []
    
    for i in range(len(Y)):
        x = X[i,:]
        y = Y[i,0]
        result = classifier.classify(x)
        correct_dp.append(result[y])
    
    # Process
    correct_dp = np.array(correct_dp)
    
    return correct_dp