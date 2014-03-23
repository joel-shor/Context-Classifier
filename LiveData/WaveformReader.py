'''
Created on Mar 22, 2014

@author: jshor
'''

from itertools import islice
import numpy as np

from Reader import Reader
#from gtk import WIN_POS_MOUSE as pos
from gtk import WIN_POS_NONE as pos

class WaveformReader(Reader):
    ''' Keeps track of waveforms and the pyGTK window
        that displays them. '''
    def __init__(self, wv, wv_iters, start_iter):
        super(WaveformReader,self).__init__(win_size=400,
                                            win_loc=pos,
                                            title='Waveform')
        self.wv = wv
        self.wv_iters = wv_iters
        self.cur_iter = start_iter
        self.cur_i = 0
        
        self.cur_i = 0
        self.t_lim = 1000
        self.ax.set_xlim([0,self.t_lim])
        self.ax.set_ylim([np.min(wv),np.max(wv)])
        
        self.wave, = self.ax.plot([],[],'',animated=True)
        
        self.wave_hist = []; self.t_hist = []
        self.canvas.mpl_connect('resize_event',lambda x: self.update_background())
        self.canvas.draw()
        
    def read2(self, *args):
        ''' This is slow '''
        cnt = 0
        for i in islice(self.wv_iters,self.cur_i,len(self.wv)):
            cnt += 1
            if i > self.cur_iter:
                break
        wv_out = self.wv[self.cur_i:self.cur_i+cnt]
        self.cur_i += cnt
        return wv_out
    
    def read(self, *args):
        ''' Try to do it in chunks '''
        cnt = 1; step = 50
        print 'cur iter in wv:', self.cur_iter
        print 'cur i in wv:', self.cur_i
        while self.cur_i + cnt*step < len(self.wv):
            chunk = np.array([x for x in islice(self.wv_iters,
                                       self.cur_i+cnt*step)])
                                       
            if np.any(np.nonzero(chunk > self.cur_iter)[0]):
                inds = np.nonzero(chunk <= self.cur_iter)[0]
                break
            else:
                # If none of them are larger
                cnt += 1
        print 'final count:', cnt
        print chunk
        print 'inds:', inds
        last_ind = inds[-1]
        print 'last ind', last_ind
        wv_out = self.wv[self.cur_i+inds]
        self.cur_i += last_ind
        self.cur_iter += 1
        return wv_out
    
    def draw(self, signal):
        ''' Signal is Xx4 '''
        self.canvas.restore_region(self.background)
        
        
        if len(self.wave_hist) + len(signal) < self.t_lim:
            self.wave_hist.extend(signal[:,0])
        else:
            self.wave_hist = np.concatenate([self.wave_hist,signal[:,0]])[-1*self.t_lim:]

        '''
        try:
            print self.wave_hist.shape
        except:
            print len(self.wave_hist)'''
        self.wave.set_data(range(len(self.wave_hist)),self.wave_hist)
        
        for itm in [self.wave]:
            self.ax.draw_artist(itm)
        
        self.canvas.blit(self.ax.bbox)