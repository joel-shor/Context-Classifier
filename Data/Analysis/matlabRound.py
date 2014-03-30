'''
Created on Mar 22, 2014

@author: jshor
'''
import numpy as np

def matround(a, decimals=0):
    '''Python rounds to the nearest EVEN integer in the case
    #  of ties, while Matlab does not. In order to check for consistency
    #  between the two, I implement a method that simulates matlab rounding
    #  behavior'''
    return np.round(a+10**(-(decimals+5)), decimals=decimals)