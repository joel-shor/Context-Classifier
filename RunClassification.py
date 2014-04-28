'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from Data.Analysis.getClusters import spike_loc
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as Classifier
from ContextPredictors.GeneratePopulationVectors.BySpace import generate_population_vectors as gpv

good_clusters = {1:range(2,8),
                 2:range(2,8),
                 3:range(2,14),
                 4:range(2,7),
                 5:range(2,12),
                 6:[2],
                 7:[2,3,4],
                 11:[2],
                 12:[2,3]}


def count_cells(vl,cls,trigger_tm,good_clusters):
    t_cells = {}
    for tetrode,cl in cls.items():
        if tetrode not in good_clusters: continue
        for cell in good_clusters[tetrode]:
            logging.info('Finding spike locations for tetrode %i, cell %i',tetrode,cell)
            cache_key = (cl['Label'][::10],vl['xs'][::10],trigger_tm,cell,)
            spk_i = spike_loc(cl, vl, trigger_tm, cell, cache_key)
            if spk_i is np.NAN: break
            t_cells[(tetrode,cell)] = spk_i
    return t_cells

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    session = 60 
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    K = 32 # Segment length used to calculate firing rates
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}

    ''''''
    # Label with task
    labels = np.unique(vl['Task'])
    label_is = {contxt: np.nonzero(vl['Task']==contxt)[0] for contxt in labels}
    label_l = vl['Task']
    
    t_cells = count_cells(vl,cls,trigger_tm,good_clusters)
    
    X, y = gpv(vl, t_cells, room_shape, bin_size, label_l, K=32)
    
    import pdb; pdb.set_trace()
    
    classifier = Classifier(vl,cls,trigger_tm, label_is, room_shape, bin_size)
    Xs, Ys = classifier.generate_population_vectors(vl['Task'])
    
    correct_dp = []
    incorrect_dp = []
    
    for (xbin,ybin),vecs,lbls in zip(Xs.keys(),Xs.values(),Ys.values()):
        for vec,lbl in zip(vecs,lbls):
            if lbl == 0:
                crct, incrct = classifier.classifiy(xbin, ybin, vec)
            else:
                incrct, crct  = classifier.classifiy(xbin, ybin, vec)
            correct_dp.append(crct)
            incorrect_dp.append(incrct)
    
    # Process
    correct_dp = np.array(correct_dp)
    incorrect_dp = np.array(incorrect_dp)
    nonzero_is = (correct_dp > 0) | (incorrect_dp > 0)
    correct_dp = correct_dp[np.nonzero(nonzero_is)[0]]
    incorrect_dp = incorrect_dp[np.nonzero(nonzero_is)[0]]
    
    from matplotlib import pyplot as plt
    hist,xedges,yedges = np.histogram2d(correct_dp, incorrect_dp, 300)
    
    Xs, Ys = np.meshgrid(xedges, yedges)
    import pdb; pdb.set_trace()
    grph = plt.pcolor(Xs,Ys,hist)
    plt.colorbar(grph, extend='both')
    plt.figure()
    plt.scatter(correct_dp,incorrect_dp)
    plt.show()