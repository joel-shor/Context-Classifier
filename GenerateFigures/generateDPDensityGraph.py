'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.DotProduct import DotProduct as Classifier

def generate_DP_density_graph():
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    session = 60 # This is August 7, 2013 run
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,16)}
    
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    # Actual Contexts
    labels = np.unique(vl['Task'])
    label_is = {contxt: np.nonzero(vl['Task']==contxt)[0] for contxt in labels}
    
    classifier = Classifier(vl,cls,trigger_tm, label_is, room_shape, bin_size)
    Xs, Ys = classifier.generate_population_vectors()
    
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
    
    # 2d Histogram
    plt.figure()
    hist,xedges,yedges = np.histogram2d(correct_dp, incorrect_dp, 150)
    Xs, Ys = np.meshgrid(xedges, yedges)
    grph = plt.pcolor(Xs,Ys,hist)
    plt.xlim([0,xedges[-1]])
    plt.ylim([0,yedges[-1]])
    plt.colorbar(grph, extend='both')
    plt.title('Dot Product Classifier Accuracy')
    plt.xlabel('Population vector x Correct Template')
    plt.ylabel('Population vector x Incorrect Template')
    
    # Accuracy meter
    plt.figure()
    accuracy = correct_dp / np.sqrt(correct_dp**2+incorrect_dp**2)
    plt.hist(accuracy)
    plt.xlabel('Accuracy')
    
    plt.show()
    