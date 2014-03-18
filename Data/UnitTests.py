'''
Created on Mar 15, 2014

@author: jshor
'''

import unittest
from readData import load_cl, load_vl, load_mux, _datenum
from datetime import datetime
from getClusters import spike_loc
import numpy as np

class DataTests(unittest.TestCase):

    def testDataLoad(self):
        num = 66
        session = 70
        tetrode = 1
        
        fn, trigger_tm = load_mux(num,session)
        cl = load_cl(num,fn,tetrode)
        vl = load_vl(num,fn)
        self.failUnless(len(cl) == 3)
        self.failUnless(len(vl) == 8)

    def testDateNum(self):
        tmp = datetime(year=1998,month=2,day=4,minute=5)
        dn = _datenum(tmp)
        self.failUnless(dn - 729790.003472222 < 10**-9)
        
    def testSpikeLoc(self):
        validation_txt_fn = 'Animal 66, Session 60, Tetrode 4, Cluster 2.validation'
        with open(validation_txt_fn, 'r') as f:
            real_spk_locs = f.readlines()
        real_spk_locs = np.array([int(x.replace('\n','')) for x in real_spk_locs])
        
        fn, trigger_tm = load_mux(animal=66,session=60)
        cl = load_cl(animal=66,fn=fn,tetrode=4)
        vl = load_vl(animal=66,fn=fn)
        my_spk_locs = spike_loc(cl, vl, trigger_tm, target_cl=2)
        diff = np.setxor1d(my_spk_locs, real_spk_locs)
        self.failUnless(len(diff)==0)
        
def main():
    unittest.main()

if __name__ == '__main__':
    main()