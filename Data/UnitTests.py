'''
Created on Mar 15, 2014

@author: jshor
'''

import unittest
from readData import load_cl, load_vl, load_mux, _datenum
from datetime import datetime

class FooTests(unittest.TestCase):

    def testDataLoad(self):
        num = 66
        session = 70
        tetrode = 1
        
        tmp = datetime(year=1998,month=2,day=4,minute=5)
        dn = _datenum(tmp)
        self.failUnless(dn - 729790.003472222 < 10**-9)
        
        fn, trigger_dt, start_dt = load_mux(num,session)
        cl = load_cl(num,fn,tetrode)
        vl = load_vl(num,fn)
        self.failUnless(len(cl) == 3)
        self.failUnless(len(vl) == 8)

def main():
    unittest.main()

if __name__ == '__main__':
    main()