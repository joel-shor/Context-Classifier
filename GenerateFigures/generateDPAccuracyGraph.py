'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np
from matplotlib import pyplot as plt

from ContextPredictors.checkClassifier import check_classifier
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.Jezek_PCA import DotProduct as CL11
from ContextPredictors.DotProducts.MultinomialOptimum import MultinomialOptimum as CL6
from ContextPredictors.DotProducts.PoissonOptimum import PoissonOptimum as CL10
from ContextPredictors.SVM import SVM


from Data.goodClusters import get_good_clusters
from cache import try_cache

def generate_DP_accuracy_graph():
    CL = CL1
    animal = 66
    session = 60 
    
    bin_size = 5
    K =  1# Segment length used to calculate firing rates
    cluster_profile = 0
    label = 'Task'
    
    cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
    try:
        raise Exception
        adat = try_cache('One big data structure')
        correct_dp = adat[CL.name][animal][session][cl_prof_name][bin_size][label][K]
        logging.info('Got data from cache.')
    except:
        logging.info('Calculating classifications...')
        CL.delt_t=K
        correct_dp = check_classifier(CL, good_clusters, label, K, 
                                      bin_size, animal, session)

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
    