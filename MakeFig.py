'''
Created on Mar 29, 2014

@author: jshor
'''
import argparse


#from Figures.generateDPConfidenceGraph import generate_DP_confidence_graph
#from Figures.generateDPPredictionGraph import generate_DP_prediction_graph

import logging

if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(description='Choose which figure to graph.')
    parser.add_argument('graph_name',help='name of the graph to make',
                        choices=['gpv_rates','clusters','rate','angle',
                                 'dp_accuracy', 'context_rate','simulation',
                                 'filter',
                                 'smoothing'])

    nn = parser.parse_args().graph_name
    
    if nn == 'clusters':    
        from Figures.clusters import cluster_graphs
        cluster_graphs()
    elif nn == 'rate':
        from Figures.rateGraph import rate_graph as rg   
        rg()
    elif nn == 'angle':
        from Figures.cumulAngleTraveled import cumulative_angle_traveled
        cumulative_angle_traveled()
    elif nn == 'dp_accuracy': 
        from Figures.dpAccuracy import dp_accuracy
        dp_accuracy()
    elif nn == 'simulation':
        from Figures.viewSimulation import view_simulation
        view_simulation()
    elif nn == 'gpv_rates':
        from Figures.gpvRates import gpv_rates
        gpv_rates()
    
    #For paper
    elif nn == 'context_rate':
        from Figures.PaperGraphs.rateGraph import rate_graph
        rate_graph()
    elif nn == 'filter':
        from Figures.PaperGraphs.filterGraph import filter_graph
        filter_graph()
    elif nn == 'smoothing':
        from Figures.PaperGraphs.smoothingGraph import smoothing
        smoothing()