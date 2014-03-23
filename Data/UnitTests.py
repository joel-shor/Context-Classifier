'''
Created on Mar 15, 2014

@author: jshor
'''

import unittest
from readData import load_cl, load_vl, load_wv, load_mux, _datenum
from datetime import datetime
from getClusters import spike_loc
import numpy as np

class DataTests(unittest.TestCase):

    def testDataLoad(self):
        num = 66
        session = 60
        tetrode = 1
        
        fn, trigger_tm = load_mux(num,session)
        cl = load_cl(num,fn,tetrode)
        vl = load_vl(num,fn)
        wv = load_wv(num,fn,tetrode)
        self.failUnless(len(cl) == 3)
        self.failUnless(len(vl) == 8)
        self.failUnless(wv.shape[1] == 4)

    def testDateNum(self):
        tmp = datetime(year=1998,month=2,day=4,minute=5)
        dn = _datenum(tmp)
        self.failUnless(dn - 729790.003472222 < 10**-9)
        
    def testSpikeLoc(self):
        validation_txt_fn_x = 'Animal 66, Session 60, Tetrode 4, Cluster 2, xs.validation'
        validation_txt_fn_y = 'Animal 66, Session 60, Tetrode 4, Cluster 2, ys.validation'
        
        with open(validation_txt_fn_x, 'r')  as f:
            real_spk_xs = f.readlines()
        
        with open(validation_txt_fn_y, 'r')  as f:
            real_spk_ys = f.readlines()

        real_spk_xs = np.array([float(x) for x in real_spk_xs[0].split(',')])
        real_spk_ys = np.array([float(x) for x in real_spk_ys[0].split(',')])
        
        # There are sometimes rounding differences, so (try to) get rid of them 
        real_spk_xs = np.round(real_spk_xs,1)
        real_spk_ys = np.round(real_spk_ys,1)
        
        fn, trigger_tm = load_mux(animal=66,session=60)
        cl = load_cl(animal=66,fn=fn,tetrode=4)
        vl = load_vl(animal=66,fn=fn)
        my_spk_locs = spike_loc(cl, vl, trigger_tm, target_cl=2)
        
        # [-38.54974573, -38.54974573])
        # There are sometimes rounding differences
        my_spk_xs = np.round(vl['xs'][my_spk_locs],1)
        my_spk_ys = np.round(vl['ys'][my_spk_locs],1)
        
        diff1 = np.setxor1d(real_spk_xs, my_spk_xs)
        diff2 = np.setxor1d(real_spk_ys, my_spk_ys)
        
        # There is sometimes roundoff error
        self.failUnless(len(diff1)<5 and len(diff2)<5) 
        
def main():
    unittest.main()

if __name__ == '__main__':
    main()