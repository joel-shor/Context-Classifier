'''
Created on May 4, 2014

@author: jshor
'''
from Data.readData import load_mux, load_vl
import numpy as np
from cache import try_cache

## Environment is bounded by [-53.57,53.57]x[-53.57,53.57]


good_trials = try_cache('Good trials')
animal = 66
session = 60

minx = []; maxx=[]
miny=[];maxy=[]

from time import time
s = time()
for animal in range(65,67):
    for session in good_trials[animal]:
        print animal, session
        fn, trigger_tm = load_mux(animal, session)
        vl = load_vl(animal,fn)

        try:        
            speed = np.sqrt(vl['vxs']**2+vl['vys']**2)
            dx = vl['xs'][1:]-vl['xs'][:-1]
            dy = vl['ys'][1:]-vl['ys'][:-1]
        except:
            from traceback import print_exc as ps
            ps()
            import pdb; pdb.set_trace()
        dxy = np.sqrt(dx**2+dy**2)
        speed_by_pos = dxy*32.0
        
        minx.append(np.min(vl['xs']))
        maxx.append(np.max(vl['xs']))
        
        miny.append(np.min(vl['ys']))
        maxy.append(np.max(vl['ys']))

print 'Total time:%.4f'%(time()-s,)

import pdb; pdb.set_trace()

#print 'velocity:%.3f, %.3f'%(np.min(speed), np.max(speed))
try:
    print 'x:%.3f, %.3f'%(min(minx), max(maxx))
    print 'y:%.3f, %.3f'%(min(miny),max(maxx))
except Exception as e:
    print e
    import pdb; pdb.set_trace()
#print 'velocity by position:%.3f, %.3f'%(np.min(speed_by_pos), np.max(speed_by_pos))