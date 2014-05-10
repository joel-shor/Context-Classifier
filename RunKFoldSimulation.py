'''
Created on Apr 28, 2014

@author: jshor
'''

import logging
import numpy as np
from itertools import product
from sklearn import cross_validation

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.countCells import count_cells
from ContextPredictors.checkClassifierFold import check_classifier

#from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
#from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.MultinomialOptimum import MultinomialOptimum as CL6
#from ContextPredictors.DotProducts.PoissonOptimum import PoissonOptimum as CL6
#from ContextPredictors.SVM import SVM as CL5

#from ContextPredictors.DotProducts.MultinomialOptimumSmoothed import MultinomialOptimum as CL7
#from ContextPredictors.DotProducts.MultinomialHarsh import MultinomialOptimum as CL8
#from ContextPredictors.DotProducts.MultinomialHarsh2 import MultinomialOptimum as CL9


from Data.goodClusters import get_good_clusters
from cache import try_cache, store_in_cache, add

def run():
    logging.basicConfig(level=logging.INFO)
    
    #CLs = [CL2,CL6,CL5]
    CLs = [CL6]
    
    # Good trials is a dictionary
    #  good_trials[animal] = [list of sessions that are task trials
    #                         and have at least one labeled cluster]
    good_trials = try_cache('Good trials')
    animal_sess_combs = [(animal,session) for animal in range(65,74) 
                         for session in good_trials[animal]]
    animal_sess_combs = [(66,60)]
    Folds = 6
    bin_sizes = [5]
    Ks = np.arange(50,150,25) # Segment length used to calculate firing rates
    cl_profs = [0]
    label = 'Task'
    exceptions = []
    
    room = [[-55,55],[-55,55]]
    
    cache = try_cache('One big data structure for %i folds'%(Folds,))
    adat = ({} if cache is None else cache)

    for animal,session in animal_sess_combs:
        for cluster_profile, bin_size,K in product(cl_profs,bin_sizes,Ks):
            cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
    
            dps = {k:[] for k in CLs}
            cached = {x:False for x in CLs}
            for CL in CLs:
                cache_key = (CL.name, K, label, bin_size, animal, session,Folds,'accuracy comparison')
                cache = try_cache(cache_key)
                if cache is not None:
                    logging.warning('%s, %i bins, %s cl prof, %i seg, (%i, %i) WAS CACHED!',CL.name, bin_size,
                                    cl_prof_name, K, animal, session)
                    cached[CL] = True
                    dps[CL] = cache
            if np.all(cached.values()): continue
    
    
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
            
            kf = cross_validation.KFold(len(Y),n_folds=Folds,shuffle=True)
            
            for train_index, test_index in kf:
                logging.warning('Training/testing: %i/%i',len(train_index),len(test_index))
                for CL in CLs:
                    if cached[CL]: continue
                    logging.warning('%s, %i bins, %s cl prof, %i seg, (%i, %i)',CL.name, bin_size,
                                    cl_prof_name, K, animal, session)
                    if (CL,cluster_profile) in exceptions: continue
                    CL.delt_t = K
                    correct_dp = check_classifier(train_index,test_index,X,Y,CL, room, bin_size)
                    dps[CL].extend(correct_dp.tolist())
            for CL in CLs:
                if cached[CL]: continue
                to_add = np.array(dps[CL]).reshape([-1])
                cache_key = (CL.name, K, label, bin_size, animal, session,Folds,'accuracy comparison')
                store_in_cache(cache_key,to_add)
                add(adat, CL.name, animal, session, cl_prof_name, bin_size, label, K, to_add)

    store_in_cache('One big data structure for %i folds'%(Folds,),adat)

if __name__=='__main__':
    run()