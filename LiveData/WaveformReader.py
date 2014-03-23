'''
Created on Mar 22, 2014

@author: jshor
'''
from Reader import Reader
#from gtk import WIN_POS_MOUSE as pos
from gtk import WIN_POS_NONE as pos

class WaveformReader(Reader):
    ''' Keeps track of waveforms and the pyGTK window
        that displays them. '''
    def __init__(self, wv, wv_iters):
        super(WaveformReader,self).__init__(win_size=400,
                                            win_loc=pos,
                                            title='Waveform')
        self.wv = wv
        self.wv_iters = wv_iters
        
        self.cur_i = 0
        self.t_lim = 1000
        self.ax.set_xlim([0,self.t_lim])
        self.ax.set_ylim([-20,20])
        
        self.wave, = self.ax.plot([],[],'',animated=True)
        
        self.wave_hist = []; self.t_hist = []
        self.canvas.mpl_connect('resize_event',lambda x: self.update_background())
        self.canvas.draw()
        
    def read(self, *args):
        return 0
    
    def draw(self, count, signal):
        self.canvas.restore_region(self.background)
        
        if len(self.wave_hist) < self.t_lim:
            self.wave_hist.append(signal)
        else:
            self.wave_hist.pop(0)
            self.wave_hist.append(signal)
        self.wave.set_data(range(len(self.wave_hist)),self.wave_hist)
        
        for itm in [self.wave]:
            self.ax.draw_artist(itm)
        
        self.canvas.blit(self.ax.bbox)