'''
Created on Mar 29, 2014

@author: jshor
'''
import argparse

import logging

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Choose which figure to graph.')
    parser.add_argument('script_name',help='name of the script',
                        choices=['populate_spike_cache',
                                 'update_good_trials',
                                 'check_gpv',
                                 'view_pca',
                                 'cl_cnt',
                                 'vl_look_data',
                                 'count_clusters',
                                 'count_vl'])

    nn = parser.parse_args().script_name

    if nn == 'populate_spike_cache':    
        from Scripts.populateSpikeLocationCache import run as psl
        psl()
    elif nn=='update_good_trials':
        from Scripts.updateGoodTrials import run as ugt
        ugt()
    elif nn=='view_pca':
        from Scripts.viewPCA import view_PCA as pca
        pca()
    elif nn=='cl_cnt':
        from Scripts.graphClusterCount import cluster_count
        cluster_count()
    elif nn=='vl_look_data':
        from Scripts.lookAtVl import vl_look
        vl_look()
    elif nn=='count_clusters':
        from Scripts.countClusters import count
        count()
    elif nn=='count_vl':
        from Scripts.countVlLen import count_vl
        count_vl()
    