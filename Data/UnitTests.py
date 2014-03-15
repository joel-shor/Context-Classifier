'''
Created on Mar 15, 2014

@author: jshor
'''

import unittest
from readData import load_cl, load_vl

class FooTests(unittest.TestCase):

    def testDataLoad(self):
        num = 66
        fn = '20130610T170549'
        tetrode = 1
        cl = load_cl(num,fn,tetrode)
        vl = load_vl(num,fn)
        self.failUnless(len(cl) == 3)
        self.failUnless(len(vl) == 8)

def main():
    unittest.main()

if __name__ == '__main__':
    main()