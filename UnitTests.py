'''
Created on Mar 15, 2014

@author: jshor
'''

import unittest
import numpy as np

from Data.readData import load_cl, load_vl, load_wv, load_mux, _datenum
from datetime import datetime
from Data.Analysis.getClusters import spike_loc
from Data.Analysis.classifyTask import get_orientation, find_runs
from Data.Analysis.filter import bandfilt

from os.path import join

class DataTests(unittest.TestCase):

    def testDataLoad(self):
        num = 66
        session = 60
        tetrode = 1
        
        fn, _ = load_mux(num,session)
        cl2 = load_cl(num,fn,tetrode)
        vl = load_vl(num,fn)
        wv = load_wv(num,fn,tetrode)
        self.failUnless(len(cl2) == 3)
        self.failUnless(len(vl) == 8)
        self.failUnless(wv.shape[1] == 4)
        import pdb; pdb.set_trace()

    def testDateNum(self):
        tmp = datetime(year=1998,month=2,day=4,minute=5)
        dn = _datenum(tmp)
        self.failUnless(dn - 729790.003472222 < 10**-9)

class AnalysisTests(unittest.TestCase):   
    def testSpikeLoc(self):
        validation_txt_fn_x = 'Animal 66, Session 60, Tetrode 4, Cluster 2, xs.validation'
        validation_txt_fn_y = 'Animal 66, Session 60, Tetrode 4, Cluster 2, ys.validation'
        
        flder = 'UnitTest'
        
        with open(join(flder,validation_txt_fn_x), 'r')  as f:
            real_spk_xs = f.readlines()
        
        with open(join(flder,validation_txt_fn_y), 'r')  as f:
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
    
    def testTaskClassification(self):
        num = 66
        session = 60
        
        fn, _= load_mux(num,session)
        vl = load_vl(num,fn)
        
        task = get_orientation(vl, 0, 0)
        
        self.failUnless(len(task) == len(vl['xs']))
        
        acceptable_labels = [0,1]
        
        correct_lbl = 0
        for label in acceptable_labels:
            correct_lbl += len(np.nonzero(task==label)[0])
        self.failUnless(correct_lbl == len(task)) 
        
        sgn, run_len = find_runs(task)
        
        self.failUnless(len(sgn) == len(run_len))
        self.failUnless(np.sum(run_len)==len(task))

    def testBandpassFilter(self):
        freq = 1000
        x = np.arange(0,100,1.0/freq)
        wv1 = np.cos(2*np.pi*x) # Freq = 1
        wv2 = np.cos(2*np.pi*x*7.0) # Freq = 7
        wv = wv1+wv2
        out = bandfilt(wv,6,8,freq)
        self.failUnless(np.sum(out-wv2) < 10**-10)

def main():
    unittest.main()

if __name__ == '__main__':
    main()