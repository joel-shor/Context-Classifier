'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

from Predictor import ContextPredictor

class DotProduct(ContextPredictor):
    def __init__(self, vl, wv, cl):
        self.vl = vl
        self.wv = wv
        self.cl = cl