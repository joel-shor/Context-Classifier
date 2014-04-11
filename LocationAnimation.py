try:
    import pygtk
    pygtk.require("2.0")
except:
    raise Exception()
import gtk


from Animation.AnimationWindow import MainWin as MainWin

import gobject as gobj
import logging

from Data.readData import load_mux, load_vl, load_wv, load_cl
from Data.Analysis.matchClToVl import match_cl_to_vl
from ContextPredictors.PiecewiseHMM import PiecewiseHMM
from ContextPredictors.DotProduct import DotProduct

timeout_rate = 15
animation_step_size = 10

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    room_shape = [[-60,60],[-60,60]]
    animal = 66
    session = 60 # This is August 7, 2013 run
    tetrode=3
    
    
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)
    cl = load_cl(animal,fn,tetrode)
    wv = load_wv(animal,fn,tetrode)
    wv_iters = match_cl_to_vl(cl['Time'],vl, trigger_tm)
    
    #WAVE_L = WR.read(vl[2],vl[3], is_clockwise(*vl[2:6]))
    #actual_prediction = np.array([is_clockwise(x,y,vx,vy) for 
    #                              x,y,vx,vy in zip(*vl.values()[2:6])])
    #logging.info('Starting to generate waveforms...')
    #global WAVE_L
    #WAVE_L = WR.read(vl[2],vl[3],actual_prediction)
    #WAVE_L = np.array([WR.read(x,y,actual) for actual, x,y in zip(actual_prediction, *vl[2:4])])
    #logging.info('Finished generating waveform.')
    
    '''
    HMM = PiecewiseHMM(vl[2],vl[3],WAVE_L,actual_prediction)
    comps = np.array([len(hmm_tup[1].means_) if hmm_tup is not None else 0 for hmm_tup in HMM.HMMs])
    side_of_arr = int(np.sqrt(len(comps)))
    comps = comps.reshape([side_of_arr,side_of_arr])
    print comps'''
    
    #HMM.make_predictions()
    #HMM.print_perc_correct()
    
    #physical = rand_walk(step_num=1000,step_size=.05)
    CPr = None
    top = MainWin(step=animation_step_size)
    top.init_ER(vl, room_shape)
    top.init_WR(wv, cl, wv_iters)
    top.add_predictor(CPr)
    gobj.timeout_add(timeout_rate,top.update)
    gtk.main()
    