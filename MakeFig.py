'''
Created on Mar 29, 2014

@author: jshor
'''
from GenerateFigures.generateClusterGraphs import generate_cluster_graphs
from GenerateFigures.generateSpikeRateGraphs import generate_spike_rate_graphs
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #generate_cluster_graphs()
    generate_spike_rate_graphs()