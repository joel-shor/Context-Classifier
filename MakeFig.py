'''
Created on Mar 29, 2014

@author: jshor
'''
import argparse


from GenerateFigures.generateClusterGraphs import generate_cluster_graphs
from GenerateFigures.rateGraph import rate_graph as rg
from GenerateFigures.generateRunLengthGraphs import generate_run_length_graphs
from GenerateFigures.generateThetaRhythmGraphs import generate_theta_rhythm_graphs
from GenerateFigures.generateAngleGraphs import generate_angle_graphs
from GenerateFigures.generateDPBaselineGraphs import generate_dp_baseline_graphs
from GenerateFigures.dpAccuracy import dp_accuracy
#from GenerateFigures.generateDPConfidenceGraph import generate_DP_confidence_graph
#from GenerateFigures.generateAmbiguousDataGraphs import generate_ambiguous_data_graphs
#from GenerateFigures.generateDPPredictionGraph import generate_DP_prediction_graph
from GenerateFigures.generateAccuracyVsKGraphs import generate_accuracy_vs_k_graphs

from GenerateFigures.PaperGraphs.rateGraph import rate_graph
from GenerateFigures.PaperGraphs.compareGraph import compare

import logging

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(description='Choose which figure to graph.')
    parser.add_argument('graph_name',help='name of the graph to make',
                        choices=['clusters','rate','runs','theta','angle','dp_baseline',
                                 'spike_rate_diff','dp_accuracy','k_accuracy',
                                 'paper_rate','paper_compare'])

    nn = parser.parse_args().graph_name
    
    logging.basicConfig(level=logging.INFO)
    
    if nn == 'clusters':    generate_cluster_graphs()
    elif nn == 'rate':      rg()
    elif nn == 'runs':      generate_run_length_graphs()
    elif nn == 'theta':     generate_theta_rhythm_graphs()
    elif nn == 'angle':     generate_angle_graphs()
    elif nn == 'dp_baseline':generate_dp_baseline_graphs()
    elif nn == 'dp_accuracy': dp_accuracy()
    elif nn == 'k_accuracy':generate_accuracy_vs_k_graphs()

    #generate_DPTimeSeg_accuracy_graph()
    #generate_DP_confidence_graph()
    #generate_ambiguous_data_graphs()
    #generate_DP_prediction_graph()
    
    #For paper
    elif nn == 'paper_rate': rate_graph()
    elif nn == 'paper_compare':compare()
    