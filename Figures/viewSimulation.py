'''
Plots the accuracy of various classifiers as a function of segment length
K.


Created on Apr 11, 2014

@author: jshor
'''
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging
import numpy as np
from itertools import product

from Data.readData import load_mux, load_vl


from ContextPredictors.Predictors.DotProducts.DotProduct3 import DotProduct as CL3
from ContextPredictors.Predictors.DotProducts.Jezek_PCA import DotProduct as CL4
from ContextPredictors.Predictors.DotProducts.DP2_PCA import DotProduct as CL5

from ContextPredictors.Predictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.Predictors.DotProducts.DotProduct2 import DotProduct as CL2
from ContextPredictors.Predictors.DotProducts.PoissonOptimum import PoissonOptimum as CL6
from ContextPredictors.Predictors.DotProducts.DotProduct2b import DotProduct as CL7
from ContextPredictors.Predictors.DotProducts.BinomialOptimum import BinomialOptimum as CL8
from ContextPredictors.Predictors.DotProducts.PoissonOptimum2 import PoissonOptimum2 as CL9



from Data.goodClusters import get_good_clusters
from Cache.cache import try_cache

clrs = ['b','r','c','k','y','m']
ln_typs = ['-','--','-.',':']

def view_simulation():
    logging.basicConfig(level=logging.INFO)
    mpl.rcParams['font.size'] = 26
    lw = 3
    
    CLs = [CL6,CL7, CL2]
    Folds = 6
    
    # Good trials is a dictionary
    #  good_trials[animal] = [list of sessions that are task trials
    #                         and have at least one labeled cluster]
    #good_trials = try_cache('Good trials')
    #animal_sess_combs = [(animal,session) for animal in range(65,74) 
    #                     for session in good_trials[animal]]
    animal_sess_combs = [(66,60)]
    
    bin_sizes = [5]
    cl_profs = [0]
    label = 'Task'
    exceptions = []
    
    room = [[-55,55],[-55,55]]
    
    adat = try_cache('One big data structure for %i folds'%(Folds,))
    #adat = try_cache('One big data structure')
    if adat is None: raise Exception()

    print adat.keys()
    good_trials = try_cache('Good trials')

    for animal, session in animal_sess_combs:
        # Get time per point
        fn, _ = load_mux(animal, session)
        vl = load_vl(animal,fn)
        tms = vl['Time']*24*60*60
        tpp = np.mean(tms[1:]-tms[:-1])
        print tpp
        
        plt.figure()
        for CL, cluster_profile, bin_size in product(CLs, cl_profs, bin_sizes):
            if (CL,cluster_profile) in exceptions: continue
            if animal not in adat[CL.name] or session not in adat[CL.name][animal]:continue
            
            cl_prof_name, _ = get_good_clusters(cluster_profile)
            pts = []
            try:
                for K, correct_dp in adat[CL.name][animal][session][cl_prof_name][bin_size][label].items():
                    if len(correct_dp) == 0: continue
                    y = 100.0*np.sum(correct_dp>.5)/len(correct_dp)     
                    pts.append((K,y))
            except:
                logging.warning('Something fishy with %s',CL.name)
            if len(pts) == 0: continue
            
            pts.sort(key=lambda x: x[0])
            
            # Get the right color
            CL_i = CLs.index(CL)
            cp_i = cl_profs.index(cluster_profile)
            b_i = bin_sizes.index(bin_size)
            clr_i = CL_i*len(cl_profs)+cp_i
            
            clr_str = clrs[clr_i]+ln_typs[b_i]
            xs,ys = zip(*pts)
            plt.plot(np.array(xs)*tpp,ys,clr_str,label=CL.name,
                     linewidth=lw)

        plt.legend(fontsize='x-small',loc='lower right')
        plt.xlabel('Segment Length (s)')
        plt.ylabel('Percent Correct')
        #plt.title('Accuracy vs Segment Size, Animal %i Session %i'%(animal, session))
    plt.ylim([60,95])
    plt.title('%i-Fold Validation'%(Folds,))
    plt.show()
            