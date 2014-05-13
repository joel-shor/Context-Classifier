'''
Created on May 8, 2014

@author: jshor
'''

import numpy as np
from Data.Analysis.spikeRate import rates_from_pv
import logging

# rates[cell id, lbl, xbin, ybin]
logging.basicConfig(level=logging.WARNING)
bin_size=1
room=[[0,2],[0,2]]
X = np.array([[1,1,.5,.5,0,0],
              [0,1,1,0,0,0],
              [2,2,0,1,0,0] ])
Y = np.array([-1,
              -1,
              1])
rates = rates_from_pv(X,Y,bin_size,room)*.02
import pdb; pdb.set_trace()

import sys;sys.exit()

# Test the einsum command
import numpy as np
import time


bin_frac = np.arange(8).reshape(2,4,1)
X = np.arange(0,20,5).reshape(2,2,1)

# Generate an array [cells,xbins*ybins,# examples]
#  where the value is the ith cell's contribute to
#  firing in bin j on example k
s = time.time()
for _ in range(1000):
    cell_firings = np.einsum('ncs,nbs->cbn',X,bin_frac)
print 'Time: %.3f'%(time.time()-s,)

bin_frac = bin_frac.reshape(2,4)
X = X.reshape(2,2)
s = time.time()
for _ in range(1000):
    cf2 = _get_firings(X,bin_frac)
print 'Time: %.3f'%(time.time()-s,)
try:
    assert np.all(cell_firings == cf2)
except:
    import pdb;pdb.set_trace()
print X
print bin_frac
print cell_firings
import sys; sys.exit()


from Scripts.viewPCA import view_PCA
import logging

logging.basicConfig(level=logging.INFO)
view_PCA()