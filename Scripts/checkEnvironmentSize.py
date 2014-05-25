'''
Created on May 4, 2014

@author: jshor

Try to empirically determine the size of the environment by tracking
how much of the environment is covered by various animals in various sessions.
'''
from Data.readData import load_mux, load_vl
import numpy as np
from Cache.cache import try_cache
import logging

## Environment is bounded by [-53.57,53.57]x[-53.57,53.57]

logging.basicConfig(level=logging.INFO)

good_trials = try_cache('Good trials')

minx = [];  maxx=[]
miny=[];    maxy=[]

from time import time
s = time()
for animal in [66,70]:
    for session in good_trials[animal]:
        logging.info('Currently on: (%i, %i)', animal, session)
        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)
        
        minx.append(np.min(vl['xs']))
        maxx.append(np.max(vl['xs']))
        
        miny.append(np.min(vl['ys']))
        maxy.append(np.max(vl['ys']))

logging.info('Total time:%.4f',time()-s)
logging.info('x:%.3f, %.3f',min(minx), max(maxx))
logging.info('y:%.3f, %.3f',min(miny), max(maxy))
