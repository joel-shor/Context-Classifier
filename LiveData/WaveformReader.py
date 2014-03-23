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
    def __init__(self, wv, cl, wv_iters, start_iter):
        super(WaveformReader,self).__init__(win_size=[400,800],
                                            win_loc=pos,
                                            title='Waveform',
                                            subplot_dim=[4,1])
        self.wv = wv
        self.cl = cl
        self.wv_iters = wv_iters
        self.cur_iter = start_iter
        self.cur_iter_chunk = []
        self.cur_i = 0

        self.t_lim = 1000
        for j in range(4):
            self.axs[j].set_xlim([0,self.t_lim])
            self.axs[j].set_ylim([np.min(wv[:,j-1]),np.max(wv[:,j-1])])
        
        self.waves = [ax.plot([],[],'',animated=True)[0] for ax in self.axs]     
        
        self.wave_hists = np.zeros([0,4])
        self.canvas.mpl_connect('resize_event',lambda x: self.update_background())
        self.canvas.draw()
    
    def read(self, *args):
        ''' Try to do it in chunks '''
        cnt = 1; step = 50
        #print 'cur iter in wv:', self.cur_iter
        while not np.any(np.nonzero(self.cur_iter_chunk > self.cur_iter)[0]):
            next_chunk = np.array([x for x in islice(self.wv_iters,cnt*step)])
            self.cur_iter_chunk = np.concatenate([self.cur_iter_chunk,
                                                  next_chunk])
            cnt += 1
        #print 'final count:', cnt
        #print self.cur_iter_chunk
        inds = np.nonzero(self.cur_iter_chunk <= self.cur_iter)[0]
        wv_out = self.wv[self.cur_i+inds]
        
        if len(inds) != 0:
            last_ind = inds[-1]
            self.cur_iter_chunk = self.cur_iter_chunk[last_ind+1:]
            self.cur_i += last_ind+1
        self.cur_iter += 1
        return wv_out
    
    def draw(self, signal):
        ''' Signal is Xx4 '''
        for bg in self.backgrounds:
            self.canvas.restore_region(bg)
        
        
        if len(self.wave_hists) + len(signal) < self.t_lim:
            self.wave_hists = np.concatenate([self.wave_hists,signal])
        else:
            self.wave_hists = np.concatenate([self.wave_hists,signal])[-1*self.t_lim:]

        '''
        try:
            print self.wave_hist.shape
        except:
            print len(self.wave_hist)'''
        
        for j in range(4):
            self.waves[j].set_data(range(len(self.wave_hists)),self.wave_hists[:,j])
        
        for itm,ax in zip(self.waves,self.axs):
            ax.draw_artist(itm)
            self.canvas.blit(ax.bbox)