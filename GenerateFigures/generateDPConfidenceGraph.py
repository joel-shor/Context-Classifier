'''
Created on Apr 11, 2014

@author: jshor
'''
import logging
import numpy as np

from Data.readData import load_mux, load_vl, load_cl
from ContextPredictors.DotProducts.DotProduct1 import DotProduct as Classifier
from cache import try_cache, store_in_cache
from Data.Analysis.classifyTask import get_orientation

def generate_DP_confidence_graph():
    
    animal = 66
    session = 60 # This is August 7, 2013 run
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in range(1,17)}
    
    
    room_shape = [[-60,60],[-60,60]]
    bin_size = 8
    # Actual Contexts
    
    
    '''
    cached = try_cache(Classifier,Classifier.name,vl,cls,trigger_tm,label_is,room_shape,bin_size)
    if cached is not None:
        classifier, Xs, Ys = cached
        logging.info('Got classifier and population vectors from cache.')
    else:
        classifier = Classifier(vl,cls,trigger_tm, label_is, room_shape, bin_size)
        Xs, Ys = classifier.generate_population_vectors()
        store_in_cache(Classifier,Classifier.name,vl,cls,trigger_tm,label_is,room_shape,bin_size,
                       [classifier,Xs,Ys])'''
    
    # Label based on task
    ''''''
    labels = np.unique(vl['Task'])
    label_is = {contxt: np.nonzero(vl['Task']==contxt)[0] for contxt in labels}
    label_l = vl['Task']
    
    '''
    label_l = get_orientation(vl,cntrx=0,cntry=0)
    labels = np.unique(label_l)
    label_is = {contxt: np.nonzero(label_l==contxt)[0] for contxt in labels}'''
    
    
    classifier = Classifier(vl,cls,trigger_tm, label_is, room_shape, bin_size)
    Xs, Ys = classifier.generate_population_vectors(label_l)
    
    task0 = []
    task1 = []
    
    for (xbin,ybin),vecs,lbls in zip(Xs.keys(),Xs.values(),Ys.values()):
        for vec,lbl in zip(vecs,lbls):
            zero, one = classifier.classifiy(xbin, ybin, vec)
            if zero == 0 and one == 0: continue
            nm = np.sqrt(zero**2+one**2)
            if lbl == 0:
                task0.append((one/nm-.5)*2)
            else:
                task1.append((one/nm-.5)*2)
    
    # Process
    task0 = np.array(task0)
    task1 = np.array(task1)
    
    from matplotlib import pyplot as plt
    
    for vals,name in [(task0,'Context -1'), 
                      (task1, 'Context 1'),
                       (np.concatenate([task0,task1]),'Pooled')]:
        # Accuracy meter
        plt.figure()
        plt.hist(vals,normed=True)
        plt.xlabel('Accuracy')
        plt.title(classifier.name+ ': '+name)
    
        msg = []
        for i in [-75,-50,0,50,75]:
            perc = 1.0*np.sum(vals > i/100.0)/len(vals)*100.0
            msg.append('>%i%%:  %.1f%%'%(i,perc))
        msg = '\n'.join(msg)
        plt.xlim([-1,1])
        xcoord = 0
        ycoord = plt.ylim()[0] + (plt.ylim()[1]-plt.ylim()[0])*.5
        plt.text(xcoord,ycoord,msg)
    plt.show()
    