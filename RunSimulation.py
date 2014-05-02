'''
Created on Apr 28, 2014

@author: jshor
'''

import logging
import numpy as np
from itertools import product

from ContextPredictors.checkClassifier import check_classifier
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.MultinomialOptimum import MultinomialOptimum as CL6
from Data.goodClusters import get_good_clusters
from Data.Analysis.cache import try_cache, store_in_cache, add

def run():
    logging.basicConfig(level=logging.WARNING)
    
    CLs = [CL6]
    
    # Good trials is a dictionary
    #  good_trials[animal] = [list of sessions that are task trials
    #                         and have at least one labeled cluster]
    good_trials = try_cache('Good trials')
    animal_sess_combs = [(animal,session) for animal in range(65,74) 
                         for session in good_trials[animal]]
    animal_sess_combs = [(66,60)]

    bin_sizes = [4,8]
    Ks = np.arange(10,300,20) # Segment length used to calculate firing rates
    cl_profs = [0,1]
    label = 'Task'
    exceptions = []
    
    cache = try_cache('One big data structure')
    adat = ({} if cache is None else cache)
    
    for animal,session in animal_sess_combs:
        try: # This is if the animal/session combo has no cells
            for CL, cluster_profile in product(CLs, cl_profs):
                if (CL,cluster_profile) in exceptions: continue
                cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
                name = CL.name+','+cl_prof_name
                for bin_size in bin_sizes:
                    for K in Ks:
                        CL6.delt_t = K
                        logging.warning('%s, bin size:%i, K:%i',name, bin_size,K)
                        cache_key = (name, K, label, bin_size, animal, session,'accuracy comparison')
                        cache = try_cache(cache_key)
                        if cache is not None and len(cache) != 0:
                            correct_dp = cache
                        else:
                            correct_dp = check_classifier(CL, good_clusters, label, K, 
                                                          bin_size, animal, session)
                            store_in_cache(cache_key,correct_dp)
        
                        if np.sum(correct_dp) == 0:
                            logging.warning('Everything was zero on animal %i session %i',animal,session)
                            break
                        add(adat, CL.name, animal, session, cl_prof_name, bin_size, label, K, correct_dp)
        except Exception as e:
            logging.warning(e)
            continue
    store_in_cache('One big data structure', adat)

if __name__=='__main__':
    run()