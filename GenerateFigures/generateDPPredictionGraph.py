'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np
from matplotlib import pyplot as plt

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as Classifier
from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.countCells import count_cells

good_clusters = {1:range(2,8),
                 2:range(2,8),
                 3:range(2,14),
                 4:range(2,7),
                 5:range(2,12),
                 6:[2],
                 7:[2,3,4],
                 11:[2],
                 12:[2,3]}

time_per_vl_pt = .02 #(seconds)


def generate_DP_prediction_graph():
    
    animal = 66
    session = 60 
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    K = 32 # Segment length used to calculate firing rates
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}

    ''''''
    # Label with task
    label_l = vl['Task']
    
    # Label with orientation
    '''
    label_l = get_orientation(vl,cntrx=0,cntry=0)'''
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    X, Y = gpv(vl, t_cells, room_shape, bin_size, label_l, K)
    
    classifier = Classifier(X,Y)
    
    conf = []
    
    for i in range(len(Y)):
        sbin = X[i,-1]
        x = X[i,:-1]
        y = Y[i,0]
        result = classifier.classify(sbin,x)
        cntxt0 = result.values()[0]*2-1
        conf.append(cntxt0)
    conf=np.array(conf)
    
    
    
    # Accuracy meter
    plt.figure()
    plt.hist(conf,normed=True)
    plt.xlabel('Accuracy')
    plt.title(classifier.name)  

    msg = []
    for i in [-50,0,50]:
        perc = 1.0*np.sum(conf > i/100.0)/len(conf)*100.0
        import pdb; pdb.set_trace()
        print perc
        msg.append('>%i%%:  %.1f%%'%(i,perc))
    msg = '\n'.join(msg)
    plt.xlim([-1,1])
    xcoord = plt.xlim()[0] + (plt.xlim()[1]-plt.xlim()[0])*.1
    ycoord = plt.ylim()[0] + (plt.ylim()[1]-plt.ylim()[0])*.5
    plt.text(xcoord,ycoord,msg)
    plt.show()
    