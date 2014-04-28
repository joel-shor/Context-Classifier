'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np
from matplotlib import pyplot as plt
from itertools import product

from ContextPredictors.checkClassifier import check_classifier
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.DotProduct5 import DotProduct as CL5
from ContextPredictors.GeneratePopulationVectors.goodClusters import get_good_clusters
from Data.Analysis.cache import try_cache, store_in_cache, add

def generate_accuracy_vs_k_graphs():
    
    CLs = [CL1, CL2, CL5]
    animal = 66
    session = 60 
    bin_size = 8
    Ks = np.arange(10,2000,5) # Segment length used to calculate firing rates
    cl_profs = [0,1]
    label = 'Task'
    
    exceptions = [(CL5.name,0),(CL1.name,0)]
    
    cache = try_cache('One big data structure')
    adat = ({} if cache is None else cache)
    
    for CL, cluster_profile in product(CLs, cl_profs):
        if (CL.name,cluster_profile) in exceptions: continue
        cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
        name = CL.name+','+cl_prof_name
        for K in Ks:
            logging.warning('%s, %i',name, K)
            cache_key = (name, K, label, bin_size, animal, session,'accuracy comparison')
            cache = try_cache(cache_key)
            if CL.name == 'DP Profile 4': cache = None
            if cache is not None:
                correct_dp = cache
            else:
                correct_dp = check_classifier(CL, good_clusters, label, K, 
                                              bin_size, animal, session)
                store_in_cache(cache_key,correct_dp)
            add(adat, CL.name, animal, session, cl_prof_name, bin_size, label, K, correct_dp)
    store_in_cache('One big data structure', adat)
    
    
    # Actually draw
    plt.figure()
    for CL, cluster_profile in product(CLs, cl_profs):
        if (CL.name,cluster_profile) in exceptions: continue
        cl_prof_name, _ = get_good_clusters(cluster_profile)
        name = CL.name+','+cl_prof_name
        pts = []
        for K, correct_dp in adat[CL.name][animal][session][cl_prof_name][bin_size][label].items():
            y = 100.0*np.sum(correct_dp>.5)/len(correct_dp)
            pts.append((K,y))
        pts.sort(key=lambda x: x[0])
        
        xs,ys = zip(*pts)
        plt.plot(xs,ys,label=name)
    
    plt.legend(fontsize='x-small',loc='lower right')
    plt.xlabel('Segment Length')
    plt.ylabel('Percent Correct')
    plt.title('Accuracy vs Segment Size')
    plt.show()
            