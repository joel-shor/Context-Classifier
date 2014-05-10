import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
#from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.ByBin import gpv as gpv

from ContextPredictors.GeneratePopulationVectors.countCells import count_cells2


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
    
    t_cells = count_cells2(vl,cls,trigger_tm,good_clusters)
    
    if len(t_cells) == 0: raise Exception('No cells found')
    
    logging.info('About to generate population vector.')
    #X, Y = gpv(vl, t_cells, label_l, K)
    X, Y = gpv(vl, t_cells, label_l, K, bin_size, room_shape)
    logging.info('%i population vectors generated.',X.shape[0])
    Y = Y.reshape([-1])
    
    from GenerateFigures.checkGPV import check_gpv
    print t_cells.keys()[:9]
    check_gpv(X,Y,bin_size,room_shape,t_cells)
    import sys; sys.exit()
    
    
    classifier = Classifier(X,Y, room_shape, bin_size)
    
    from GenerateFigures.checkDP import check_dp
    check_dp(classifier)
    import sys; sys.exit()
    
    correct_dp = []
    
    for i in range(len(Y)):
        x = X[i,:]
        y = Y[i]
        result = classifier.classify(x)
        correct_dp.append(result[y])
    
    # Process
    correct_dp = np.array(correct_dp)
    
    return correct_dp