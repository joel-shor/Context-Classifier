'''
Created on Apr 28, 2014

@author: jshor
'''

import logging
import numpy as np
from itertools import product
from sklearn import cross_validation
import argparse

from Data.readData import load_mux, load_vl, load_cl
from Data.Analysis.countCells import count_cells
from ContextPredictors.checkClassifierFold import check_classifier
from Data.goodClusters import get_good_clusters
from cache import try_cache, store_in_cache, add

# Take your pick of how to generate population vecors
from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTime import generate_population_vectors as gpv

# Take your pick of Context Predictors
#from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
#from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.MultinomialOptimum import MultinomialOptimum as CL6
#from ContextPredictors.DotProducts.PoissonOptimum import PoissonOptimum as CL6
#from ContextPredictors.SVM import SVM as CL5
#from ContextPredictors.DotProducts.MultinomialOptimumSmoothed import MultinomialOptimum as CL7
#from ContextPredictors.DotProducts.MultinomialHarsh import MultinomialOptimum as CL8
#from ContextPredictors.DotProducts.MultinomialHarsh2 import MultinomialOptimum as CL9


def run(Folds):
    # Toggle-able parameters
    #CLs = [CL2,CL6,CL5]
    CLs = [CL6]
    Ks = np.arange(50,150,25) # Segment length used to calculate firing rates
    cl_profs = [0]

    # Sort of toggle-able parameters
    animal_sess_combs = [(66,60)]
    #good_trials = try_cache('Good trials')
    #animal_sess_combs = [(animal,session) for animal in range(65,74) 
    #                     for session in good_trials[animal]]
    bin_sizes = [5]
    label = 'Task'
    exceptions = []
    
    # Not really toggle-able parameters
    room = [[-55,55],[-55,55]]
    
    
    
    cache = try_cache('One big data structure for %i folds'%(Folds,))
    adat = ({} if cache is None else cache)

    for comb, clust_prof, bin_size, K in product(animal_sess_combs,cl_profs,bin_sizes,Ks):
        animal, session = comb
        cl_prof_name, good_clusters = get_good_clusters(clust_prof)
        cache_key = [K,label,bin_size,animal,session,Folds,'accuracy comparison']
        
        cached = {CL:try_cache([CL.name]+cache_key) for CL in CLs}
        cached = {k:cached[k] for k in cached if cached[k] is not None}
        
        if len(cached) == len(CLs): 
            print 'Everything laready cached'
            continue # Everything is already cached!

        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)
        cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
        
        if label == 'Task': label_l = vl['Task']
        else: raise Exception('Not implemented yet.')
        
        t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
        
        logging.info('About to generate population vector.')
        X, Y = gpv(vl, t_cells, label_l, K)
        
        # The main data stricture
        dps = {CL:[] for CL in CLs if CL not in cached}
        
        if folds >0: kf = cross_validation.KFold(len(Y),n_folds=Folds,shuffle=True)
        else: kf = [(range(len(Y)),range(len(Y)))]
        for train_index, test_index in kf:
            logging.warning('Training/testing: %i/%i',len(train_index),len(test_index))
            for CL in CLs:
                if cached[CL]: continue
                logging.warning('%s, %i bins, %s cl prof, %i seg, (%i, %i)',CL.name, bin_size,
                                cl_prof_name, K, animal, session)
                if (CL,clust_prof) in exceptions: continue
                CL.delt_t = K
                correct_dp = check_classifier(train_index,test_index,X,Y,CL, room, bin_size)
                dps[CL].extend(correct_dp.tolist())
        for CL in CLs:
            if cached[CL]: continue
            to_add = np.array(dps[CL]).reshape([-1])
            store_in_cache([CL.name]+cache_key,to_add)
            add(adat, CL.name, animal, session, cl_prof_name, bin_size, label, K, to_add)

    store_in_cache('One big data structure for %i folds'%(Folds,),adat)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='How many folds.')
    parser.add_argument('folds',help='number of folds',default=6)

    folds = parser.parse_args().folds
    
    logging.basicConfig(level=logging.INFO)
    
    run(folds)