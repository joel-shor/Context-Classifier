
import logging
import numpy as np
from itertools import product

from ContextPredictors.checkClassifier import check_classifier
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as CL1
from ContextPredictors.DotProducts.DotProduct2 import DotProduct as CL2
from Data.goodClusters import get_good_clusters
from Data.Analysis.cache import try_cache, store_in_cache, add


adat = try_cache('One big data structure')
import pdb; pdb.set_trace()


CLs = [CL1, CL2]
animal = 70
session = 8 
cl_profs = [0,2]
bin_sizes = [2,4,8]
label = 'Task'
exceptions = []

adat = try_cache('One big data structure')
if adat is None: raise Exception()


for CL, cluster_profile in product(CLs, cl_profs):
    if (CL.name,cluster_profile) in exceptions: continue
    cl_prof_name, good_clusters = get_good_clusters(cluster_profile)
    name = CL.name+','+cl_prof_name
    for bin_size in bin_sizes:
        try:
            for K in adat[CL.name][animal][session][cl_prof_name][bin_size][label]:
                adat[CL.name][animal][session][cl_prof_name][bin_size][label][K] = []
        except:
            pass
            
store_in_cache('One big data structure', adat)