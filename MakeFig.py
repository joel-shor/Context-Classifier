'''
Created on Mar 29, 2014

@author: jshor
'''
from GenerateFigures.generateClusterGraphs import generate_cluster_graphs
from GenerateFigures.generateSpikeRateGraphs import generate_spike_rate_graphs
from GenerateFigures.generateRunLengthGraphs import generate_run_length_graphs
from GenerateFigures.generateThetaRhythmGraphs import generate_theta_rhythm_graphs
from GenerateFigures.generateAngleGraphs import generate_angle_graphs


import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #generate_cluster_graphs()
    generate_spike_rate_graphs()
    #generate_run_length_graphs()
    #generate_theta_rhythm_graphs()
    #generate_angle_graphs()