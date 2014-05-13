'''
Created on Mar 29, 2014

@author: jshor
'''
import argparse


from Scripts.populateSpikeLocationCache import run as psl
from Scripts.updateGoodTrials import run as ugt
from Scripts.checkGPV import checkGPV as gpv

import logging

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Choose which figure to graph.')
    parser.add_argument('script_name',help='name of the script',
                        choices=['populate_spike_cache',
                                 'update_good_trials',
                                 'check_gpv'])

    nn = parser.parse_args().script_name
    
    if nn == 'populate_spike_cache':    psl()
    elif nn=='update_good_trials':      ugt()
    elif nn=='check_gpv':               gpv()
    