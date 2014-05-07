'''
Created on Apr 11, 2014

@author: jshor
'''
import matplotlib.pyplot as plt
import logging
import numpy as np
from itertools import product


from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.DotProducts.MultinomialOptimum import MultinomialOptimum as CL6
from ContextPredictors.DotProducts.PoissonOptimum import PoissonOptimum as CL7
from ContextPredictors.SVM import SVM as CL5


from Data.goodClusters import get_good_clusters
from Data.Analysis.cache import try_cache

clrs = ['b','r','c','k','y','m']
ln_typs = ['-','--','-.',':']

s_per_vl_pt = .02 #in seconds

def compare():
    logging.basicConfig(level=logging.INFO)
    
    CLs = [CL2,CL7,CL5,CL6]
    
    # Good trials is a dictionary
    #  good_trials[animal] = [list of sessions that are task trials
    #                         and have at least one labeled cluster]
    #good_trials = try_cache('Good trials')
    #animal_sess_combs = [(animal,session) for animal in range(65,74) 
    #                     for session in good_trials[animal]]
    animal_sess_combs = [(66,60)]
    Folds = 6
    bin_sizes = [5]
    Ks = np.arange(1,15,5) # Segment length used to calculate firing rates
    cl_profs = [0]
    label = 'Task'
    exceptions = []
    
    room = [[-55,55],[-55,55]]
    
    
    adat = try_cache('One big data structure for %i folds'%(Folds,))
    #adat = try_cache('One big data structure')
    if adat is None: raise Exception()

    good_trials = try_cache('Good trials')

    for animal in range(66,67):
        if animal not in good_trials: continue
        for session in good_trials[animal]:
            if True not in [(animal in adat[CL.name])
                            and (session in adat[CL.name][animal]) 
                            for CL in CLs]: continue
            plt.figure()
            for CL, cluster_profile, bin_size in product(CLs, cl_profs, bin_sizes):
                if (CL,cluster_profile) in exceptions: continue
                if animal not in adat[CL.name] or session not in adat[CL.name][animal]:continue
                
                cl_prof_name, _ = get_good_clusters(cluster_profile)
                name = CL.name+','+cl_prof_name+', bin size '+str(bin_size)
                pts = []
                try:
                    for K, correct_dp in adat[CL.name][animal][session][cl_prof_name][bin_size][label].items():
                        if len(correct_dp) == 0: continue
                        y = 100.0*np.sum(correct_dp>.5)/len(correct_dp)     
                        pts.append((K,y))
                except:
                    pass
                if len(pts) == 0: continue
                
                pts.sort(key=lambda x: x[0])
                
                # Get the right color
                CL_i = CLs.index(CL)
                cp_i = cl_profs.index(cluster_profile)
                b_i = bin_sizes.index(bin_size)
                clr_i = CL_i*len(cl_profs)+cp_i
                
                clr_str = clrs[clr_i]+ln_typs[b_i]
                xs,ys = zip(*pts)
                plt.plot(np.array(xs)*s_per_vl_pt,ys,clr_str,label=name)
    
            plt.legend(fontsize='x-small',loc='upper left')
            plt.xlabel('Segment Length (s)')
            plt.ylabel('Percent Correct')
            plt.title('Accuracy vs Segment Size, Animal %i Session %i'%(animal, session))
    plt.show()
            