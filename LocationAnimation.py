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

import gobject as gobj
import numpy as np
import logging

MAXX = 100
MAXY = 100

def init_environment():
    ''' Set up window that will show the rat's location,
        velocity, etc. '''
    top = gtk.Window()
    top.connect('delete-event', gtk.main_quit)
    top.set_title('Environment')
    top.set_position(gtk.WIN_POS_CENTER)
    top.set_default_size(700,700)
    
    fig = Figure()
    ax = fig.add_subplot(111)
    canvas = FigureCanvas(fig)
    top.add(canvas)
    top.show_all()
    return top,canvas,ax

def init_waveformreader():
    ''' Set up the drawing window that will show the waveform. '''
    top = gtk.Window()
    top.connect('delete-event', gtk.main_quit)
    top.set_title('Wavveform')
    top.set_default_size(400,400)
    
    fig = Figure()
    ax = fig.add_subplot(111)
    canvas = FigureCanvas(fig)
    top.add(canvas)
    top.show_all()
    return top,canvas,ax

def is_clockwise(x,y,vx,vy):
    ''' Determines if motion is clockwise around the center
        of the room, which is [0, MAXX] x [0, MAXY] '''
    cross_prod = (x-MAXX/2.0)*vy - (y-MAXY/2.0)*vx
    clockwise = True if cross_prod < 0 else False
    return 1 if clockwise else 0
class Draw:
    ''' Object which updates the environment and waveform windows. '''
    def __init__(self, ER, WR, HMM, top_env,canvas_env,ax_env, top_wfr, canvas_wfr, ax_wfr):
        self.ER = ER
        self.WR = WR
        self.HMM = HMM
        
        self.top_env = top_env
        self.canvas_env = canvas_env
        self.ax_env=ax_env
        self.setup_env()
        
        self.top_wfr = top_wfr
        self.canvas_wfr = canvas_wfr
        self.ax_wfr=ax_wfr
        self.setup_wfr()
        
        self.update_background()
    
    def setup_env(self):
        
        self.x_hist = []; self.y_hist = []
        
        self.canvas_env.mpl_connect('resize_event',lambda x: self.update_background())
        
        self.pos, = self.ax_env.plot([],[],color='g',animated=True)
        self.vel = Arrow([0,0],[1,0],arrowstyle='-|>, head_length=3, head_width=3',
                         animated=True)
        self.ax_env.add_patch(self.vel)
        self.radius, = self.ax_env.plot([],[],color='r',animated=True)
        self.clockcounter = self.ax_env.text(MAXX,0,'',ha='right',size='large',animated=True)
        self.iters = self.ax_env.text(0,0,'',animated=True)
        self.ax_env.set_xlim([0,MAXY])
        self.ax_env.set_ylim([0,MAXY])
        self.count = 0
        
        self.draw_plc_flds()
        
        self.draw_HMM_sectors()
        self.predicted_counter = self.ax_env.text(MAXX,10,'',ha='right',size='large',animated=True)
        self.prediction_hist = None
        #self.cur_sec = Rectangle([0,0],self.HMM.dx,self.HMM.dy,fill=True,
        #                         color='k',animated=True)
        #self.ax_env.add_patch(self.cur_sec)
        
        self.canvas_env.draw()
    
    def draw_HMM_sectors(self):
        for i in range(self.HMM.cll_p_sd):
            curx = self.HMM.xrange[0]+i*self.HMM.dx
            cury = self.HMM.yrange[0]+i*self.HMM.dy
            self.ax_env.plot([curx,curx],[0,MAXY],'k')
            self.ax_env.plot([0,MAXX],[cury,cury], 'k')
    
    def setup_wfr(self):
        self.t_lim = 1000
        self.ax_wfr.set_xlim([0,self.t_lim])
        self.ax_wfr.set_ylim([-20,20])
        
        self.wave, = self.ax_wfr.plot([],[],'',animated=True)
        
        self.wave_hist = []; self.t_hist = []
        self.canvas_wfr.mpl_connect('resize_event',lambda x: self.update_background())
        self.canvas_wfr.draw()
        
    def draw_plc_flds(self):
        clrs = ['b','g']
        legend_widgets = []
        for i, plc_flds in zip(range(len(self.WR.contexts)),self.WR.contexts.values()):
            added = False
            for plc_fld in plc_flds:
                circ = Circle([plc_fld.x,plc_fld.y], plc_fld.r, color=clrs[i])
                self.ax_env.add_patch(circ)
                
                if not added:
                    legend_widgets.append(circ)
                    added=True
        self.ax_env.legend(legend_widgets, ('counterclockwise','clockwise'),'lower right')
    
    def update_background(self):
        self.canvas_env.draw()
        self.canvas_wfr.draw()
        self.background_env = self.canvas_env.copy_from_bbox(self.ax_env.bbox)
        self.background_wfr = self.canvas_wfr.copy_from_bbox(self.ax_wfr.bbox)
    
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
    
    def update_environment(self, x,y,vx,vy, signal):
            
        self.canvas_env.restore_region(self.background_env)
        
        self.x_hist.append(x)
        self.y_hist.append(y)
        
        self.pos.set_data(self.x_hist,self.y_hist)
        if vx != 0 or vy != 0: 
            self.vel.set_positions([x, y], [x+vx,y+vy])
        self.radius.set_data([MAXX/2.0,x],[MAXY/2.0,y])

        if is_clockwise(x,y,vx,vy) == 1:
            self.clockcounter.set_text('Clockwise')
        else:
            self.clockcounter.set_text('Counterclockwise')

        self.iters.set_text(str(self.count))

        try:
            self._make_prediction(is_clockwise(x,y,vx,vy))
        except:
            logging.warning('Make prediction failed.')

        for itm in [self.pos, self.vel, self.radius,
                    self.clockcounter,self.iters, self.predicted_counter]:
            self.ax_env.draw_artist(itm)
        
        self.canvas_env.blit(self.ax_env.bbox)
    
    def update_waveformreader(self, time, signal):
        self.canvas_wfr.restore_region(self.background_wfr)
        
        if len(self.wave_hist) < self.t_lim:
            self.wave_hist.append(signal)
            #self.t_hist.append(time)
        else:
            self.wave_hist.pop(0)
            self.wave_hist.append(signal)
        self.wave.set_data(range(len(self.wave_hist)),self.wave_hist)
        #print self.wave_hist
        
        for itm in [self.wave]:
            self.ax_wfr.draw_artist(itm)
        
        self.canvas_wfr.blit(self.ax_wfr.bbox)
    def update(self):
        #self.txt.set_text(self.count)
        
        x,y,vx,vy = self.ER.read()
        #context = is_clockwise(x,y,vx,vy)
        signal = WAVE_L[self.count]
        
        self.update_environment(x,y,vx,vy, signal)
        self.update_waveformreader(self.count, signal)
        
        self.count += 1
        
        #self.canvas.draw()
        return True

from LiveData.readData import EnvironmentReader, WaveformReader
from Data.readData import reconstruct_bundles
from HMM.PiecewiseHMM import PiecewiseHMM
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    gen = reconstruct_bundles('66')
    vl,cl, fn = gen.next()
    
    ER = EnvironmentReader(*vl[2:6])
    WR = WaveformReader(MAXX,MAXY)
    
    #WAVE_L = WR.read(vl[2],vl[3], is_clockwise(*vl[2:6]))
    actual_prediction = np.array([is_clockwise(x,y,vx,vy) for x,y,vx,vy in zip(*vl[2:6])])
    logging.info('Starting to generate waveforms...')
    global WAVE_L
    WAVE_L = WR.read(vl[2],vl[3],actual_prediction)
    #WAVE_L = np.array([WR.read(x,y,actual) for actual, x,y in zip(actual_prediction, *vl[2:4])])
    logging.info('Finished generating waveform.')
    
    HMM = PiecewiseHMM(vl[2],vl[3],WAVE_L,actual_prediction)
    comps = np.array([len(hmm_tup[1].means_) if hmm_tup is not None else 0 for hmm_tup in HMM.HMMs])
    side_of_arr = int(np.sqrt(len(comps)))
    comps = comps.reshape([side_of_arr,side_of_arr])
    print comps
    
    #HMM.make_predictions()
    #HMM.print_perc_correct()

    env = init_environment()
    wfr = init_waveformreader()
    
    #physical = rand_walk(step_num=1000,step_size=.05)
    
    drawer = Draw(ER, WR, HMM, *(env+wfr))
    gobj.timeout_add(40,drawer.update)
    gtk.main()