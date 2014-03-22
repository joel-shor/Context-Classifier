try:
    import pygtk
    pygtk.require("2.0")
except:
    raise Exception()
import gtk

import matplotlib
matplotlib.use('GTKAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

from matplotlib.patches import FancyArrowPatch as Arrow
from matplotlib.patches import Circle, Rectangle

from LiveData.WaveformReader import WaveformReader
from LiveData.EnvironmentReader import EnvironmentReader

import gobject as gobj
import numpy as np
import logging

class MainWin:
    ''' Object which updates the environment and waveform windows. '''
    def __init__(self, ER, WR, top_env,canvas_env,ax_env, top_wfr, canvas_wfr, ax_wfr):
        self.ER = EnvironmentReader()
        self.WR = WaveformReader()
    
    def add_predictor(self, predictor):
        self.HMM = predictor
    
    def _make_prediction(self, actual_is_clockwise):
        ''' This is going to cheat and look into the future. '''
        cnt = self.ER.count
        
        prediction = self.HMM.predictions[cnt]
        
        if prediction == -1:
            self.predicted_counter.set_text('None')
        elif prediction == 1:
            self.predicted_counter.set_text('Clockwise')
        elif prediction == 0:
            self.predicted_counter.set_text('Counterclockwise')
        else:
            raise Exception
        if prediction == actual_is_clockwise:
            self.predicted_counter.set_color('g')
        else:
            self.predicted_counter.set_color('r')
    
    def update(self):
        #self.txt.set_text(self.count)
        
        x,y,vx,vy = self.ER.read()
        #context = is_clockwise(x,y,vx,vy)
        signal = self.WR.read(x,y)
        
        self.ER.draw(x,y,vx,vy, signal)
        self.WR.draw(self.count, signal)
        
        self.count += 1
        
        return True

from EnvironmentReader import  EnvironmentReader as EnvR
from WaveformReader import WaveformReader as WvR
from Data.readData import load_mux, load_vl
from HMM.PiecewiseHMM import PiecewiseHMM
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    animal = 66
    session = 60 # This is August 7, 2013 run
    fn, trigger_tm = load_mux(animal, session)
    vl = load_vl(animal,fn)

    room_shape = [100,100]

    ER = EnvR(vl, room_shape)
    WR = WvR()
    
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
    HMM = None
    top = MainWin()
    top.add_predictor(HMM)
    gobj.timeout_add(40,top.update)
    gtk.main()
    