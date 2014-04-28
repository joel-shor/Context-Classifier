
a = {}
def b(a):
    a[1] = 2

b(a)
print a
import sys; sys.exit()

from Data.Analysis.findAmbiguousData import find_ambiguous_data

from matplotlib import pyplot as plt
from Data.readData import load_mux, load_vl
from Data.Analysis.classifyTask import *

amb = find_ambiguous_data()

for animal in amb.keys():
    for session in amb[animal]:
        if amb[animal][session] is not None: continue
        try:
            fn, _= load_mux(animal,session)
            print 'Animal:%i    Fn:%s'%(animal,fn)
            vl = load_vl(animal,fn)
        except Exception as e:
            print e
            import pdb; pdb.set_trace()

import sys; sys.exit()

ns,bins, _ = plt.hist(run_len,bins=range(1,np.max(run_len)+1))
plt.title('Run length')

# For some reasons len(ns) != len(bins), so do this computation
#  manually
pts_for_classification = np.array([i*len(np.nonzero(run_len==i)[0]) for i in range(1,np.max(run_len)+1)])
plt.figure()
plt.bar(range(1,np.max(run_len)+1), pts_for_classification, align='center')
plt.title('Number of points for a given run length')
plt.xlabel('Run length')
plt.ylabel('Number of points')

if np.sum(pts_for_classification) != np.sum(run_len):
    print 'Problem'
    import pdb; pdb.set_trace()
    raise Exception('Run length calculation incorrect')

reverse_cumul_pts = np.zeros(len(pts_for_classification))
reverse_cumul_pts[-1] = pts_for_classification[-1]
for i in range(len(pts_for_classification)-2,-1,-1):
    reverse_cumul_pts[i] =  reverse_cumul_pts[i+1] + pts_for_classification[i]
    
plt.figure()
plt.bar(range(1,np.max(run_len)+1), reverse_cumul_pts, align='center')
plt.title('Number of points to train on if cutoff were x')
plt.xlabel('Run length')
plt.ylabel('Cumulative number of points')

plt.show()