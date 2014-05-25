'''
Created on Apr 11, 2014

@author: jshor

Runs a single Classifier through a training and testing phase. The training
and testing sets are the same. Shows a histogram of the correct output. Assumes
that classifier outputs a confidence rating between the two contexts.

'''
import logging
import numpy as np
from matplotlib import pyplot as plt
from time import time

from Analysis.countCells import count_cells
from ContextPredictors.GeneratePopulationVectors.ByTime import gpv
from ContextPredictors.checkClassifier import check_classifier


from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.Predictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.Predictors.DotProducts.DotProduct3 import DotProduct as CL3
from ContextPredictors.Predictors.DotProducts.Jezek_PCA import DotProduct as CL4
from ContextPredictors.Predictors.DotProducts.DP2_PCA import DotProduct as CL5

from ContextPredictors.Predictors.DotProducts.PoissonOptimum import PoissonOptimum as CL6
#from ContextPredictors.SVM import SVM as CL7

from Data.readData import load_mux, load_vl, load_cl

from Data.goodClusters import get_good_clusters
from Cache.cache import try_cache

def dp_accuracy():
    logging.basicConfig(level=10) # 5 for more stuff
    CL = CL3
    animal = 66
    session = 60 
    
    room =[[-55,55],[-55,55]]
    bin_size = 5
    K =  50      # Segment length used to calculate firing rates
    CL.delt_t = K*.02
    cluster_profile = 0
    label = 'Task'
    
    cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
    try:
        adat = try_cache('One big data structure')
        correct_dp = adat[CL.name][animal][session][cl_prof_name][bin_size][label][K]
        logging.info('Got data from Cache.cache.')
    except:
        logging.info('Calculating classifications...')
        CL.delt_t=K
        
        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)
        cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
        label_l = vl['Task']
        
        t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
        logging.info('About to generate population vector.')
        #X, Y = gpv(vl, t_cells, label_l, K)
        s=time()
        X, Y = gpv(vl, t_cells, label_l, K, bin_size, room)
        logging.info('%i population vectors generated in %.3f.',X.shape[0],time()-s)
        Y = Y.reshape([-1])
        
        correct_dp = check_classifier(range(X.shape[0]),range(X.shape[0]), 
                                      X, Y, CL, room, bin_size) 

    # Accuracy meter
    plt.figure()
    plt.hist(correct_dp,normed=True)
    plt.xlabel('Accuracy')
    tt = '%s,  K: %i, ClPr: %s, Label:%s'%(CL.name,K,cl_prof_name,
                                                   label)
    plt.title(tt)

    msg = []
    for i in [1,50,75,90,95,99]:
        perc = 1.0*np.sum(correct_dp > i/100.0)/len(correct_dp)*100.0
        msg.append('>%i%%:  %.1f%%'%(i,perc))
    msg = '\n'.join(msg)
    plt.xlim([0,1])
    xcoord = plt.xlim()[0] + (plt.xlim()[1]-plt.xlim()[0])*.1
    ycoord = plt.ylim()[0] + (plt.ylim()[1]-plt.ylim()[0])*.5
    plt.text(xcoord,ycoord,msg)
    plt.show()
    