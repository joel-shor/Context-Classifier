import logging
import numpy as np

from ContextPredictors.GeneratePopulationVectors.ByTime import gpv as gpv
#from ContextPredictors.GeneratePopulationVectors.ByTimeWithSilence import generate_population_vectors as gpv
#from ContextPredictors.GeneratePopulationVectors.ByBin import gpv as gpv2

from Analysis.countCells import count_cells

from Analysis.spikeRate import get_fracs, fracs_from_pv
from Data.readData import load_mux, load_vl, load_cl


from Figures.rateGraphLib import plot_rates
from matplotlib import pyplot as plt


def gpv_rates():
    logging.basicConfig(level=logging.INFO)
    animal = 66
    session = 60 
    room_shape = [[-55,55],[-55,55]]
    tetrodes = [1]
    cells = range(2,10)
    bin_size = 5
    K =  50# Segment length used to calculate firing rates
    
    #xbins = ybins = (room_shape[0][1]-room_shape[0][0])/bin_size
    good_clusters = {tetrode:cells for tetrode in tetrodes}
    #good_clusters = get_good_clusters(0)
    
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cls = {tetrode:load_cl(animal,fn,tetrode) for tetrode in tetrodes}
    
    label_l = vl['Task']
    t_cells = count_cells(vl,cls,trigger_tm, good_clusters)
    
    
    logging.info('About to generate population vector.')
    X, Y = gpv(vl, t_cells, label_l, K, bin_size, room_shape)
    logging.info('%i population vectors generated.',X.shape[0])
    Y = Y.reshape([-1])
            
    # GPV rates
    rates = fracs_from_pv(X,Y,bin_size,room_shape,smooth_flag=True)
    
    # Now get normally calculate rates
    real_rates = get_fracs(vl['xs'],vl['ys'],label_l,room_shape,bin_size, t_cells,smooth_flag=True)
    
    try:
        assert np.all(rates == real_rates)
    except:
        print 'DOESNT WORK!!'
    plot_rates(rates,Y,t_cells)
    plot_rates(real_rates,Y,t_cells)
    plt.show()
    