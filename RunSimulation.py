'''
Created on Apr 28, 2014

@author: jshor
'''

import logging
import numpy as np
from itertools import product
from sklearn import cross_validation
import argparse
from ContextPredictors.checkClassifier import check_classifier
from Data.readData import load_mux, load_vl, load_cl
from Analysis.countCells import count_cells
from Data.goodClusters import get_good_clusters
from Cache.cache import try_cache, store_in_cache, add

# Take your pick of how to generate population vecors
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
from ContextPredictors.GeneratePopulationVectors.ByTime import gpv

# Take your pick of Context Predictors
from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.Predictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.Predictors.DotProducts.DotProduct3 import DotProduct as CL3
from ContextPredictors.Predictors.DotProducts.Jezek_PCA import DotProduct as CL4
from ContextPredictors.Predictors.DotProducts.DP2_PCA import DotProduct as CL5
from ContextPredictors.Predictors.DotProducts.PoissonOptimum import PoissonOptimum as CL6
from ContextPredictors.Predictors.DotProducts.DotProduct2b import DotProduct as CL7
from ContextPredictors.Predictors.DotProducts.BinomialOptimum import BinomialOptimum as CL8
from ContextPredictors.Predictors.DotProducts.PoissonOptimum2 import PoissonOptimum2 as CL9
from ContextPredictors.Predictors.DotProducts.BinomialOptimum2 import BinomialOptimum2 as CL10

def run(Folds):
    # Toggle-able parameters
    #CLs = [CL2,CL6,CL5]
    #CLs = [CL6, CL7]
    CLs = [CL10]
    Ks = np.arange(10,200,20) # Segment length used to calculate firing rates
    

    # Sort of toggle-able parameters
    #animal_sess_combs = [(66,60),(70,8),(70,10),(66,61)]
    animal_sess_combs = [(66,60)]
    #good_trials = try_cache('Good trials')
    #animal_sess_combs = [(animal,session) for animal in range(65,74) 
    #                     for session in good_trials[animal]]
    bin_sizes = [5]
    label = 'Task'
    exceptions = []
    cl_profs = [0]
    
    # Not really toggle-able parameters
    room = [[-55,55],[-55,55]]
    
    
    
    cache = try_cache('One big data structure for %i folds'%(Folds,))
    adat = ({} if cache is None else cache)

    for animal, session in animal_sess_combs:
        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)
        cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
        
        if label == 'Task': label_l = vl['Task']
        else: raise Exception('Not implemented yet.')
        
        for clust_prof in cl_profs:
            cl_prof_name, good_clusters = get_good_clusters(clust_prof)
            t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
            
            for bin_size, K in product(bin_sizes,Ks):
                cached = np.zeros(len(CLs))
                for CL in CLs:
                    i = CLs.index(CL)
                    try:
                        raise Exception
                        adat[CL.name][animal][session][cl_prof_name][bin_size][label][K]
                        cached[i] = True
                    except:
                        cached[i] = False
                
                if np.sum(cached) == len(CLs): 
                    print 'Everything already cached'
                    continue # Everything is already cached!
                
                
                logging.info('About to generate population vector.')
                X, Y = gpv(vl, t_cells, label_l, K, bin_size, room)
                
                
                # The main data stricture
                dps = {CL:[] for CL in CLs if CL not in cached}
                
                if Folds >0: kf = cross_validation.KFold(len(Y),n_folds=Folds,shuffle=True)
                else: kf = [(range(len(Y)),range(len(Y)))]
                for train_index, test_index in kf:
                    logging.warning('Training/testing: %i/%i',len(train_index),len(test_index))
                    for CL in CLs:
                        if cached[CLs.index(CL)]: continue
                        logging.warning('%s, %i seg, (%i, %i)',CL.name, K, animal, session)
                        if (CL,clust_prof) in exceptions: continue
                        CL.delt_t = K
                        correct_dp = check_classifier(train_index,test_index,X,Y,CL, room, bin_size)
        
                        dps[CL].extend(correct_dp.tolist())
                for CL in CLs:
                    if cached[CLs.index(CL)]: continue
                    to_add = np.array(dps[CL]).reshape([-1])
                    add(adat, CL.name, animal, session, cl_prof_name, bin_size, label, K, to_add)

    store_in_cache('One big data structure for %i folds'%(Folds,),adat)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='How many folds.')
    parser.add_argument('--folds',help='number of folds',default=6)

    folds = parser.parse_args().folds
    
    logging.basicConfig(level=logging.WARNING)
    
    run(int(folds))