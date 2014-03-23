'''
Created on Mar 22, 2014

@author: jshor
'''

from itertools import islice
import numpy as np

from Reader import Reader
#from gtk import WIN_POS_MOUSE as pos
from gtk import WIN_POS_NONE as pos

spk_clr = {2:'r',
           3:'g',
           7:'k',
           8:'y',
           9:'b',
           10:'m'}

class WaveformReader(Reader):
    ''' Keeps track of waveforms and the pyGTK window
        that displays them. '''
    def __init__(self, wv, cl, wv_iters, start_iter):
        super(WaveformReader,self).__init__(win_size=[400,800],
                                            win_loc=pos,
                                            title='Waveform',
                                            subplot_dim=[4,1])
        self.wv = wv
        self.cl = cl['Label']
        self.wv_iters = wv_iters
        self.cur_iter = start_iter
        self.cur_iter_chunk = []
        self.cur_i = 0

        self.t_lim = 1000
        for j in range(4):
            self.axs[j].set_xlim([0,self.t_lim])
            self.axs[j].set_ylim([np.min(wv[:,j-1]),np.max(wv[:,j-1])])
        
        class Waves:
            widgs = [ax.plot([],[],'',animated=True)[0] for ax in self.axs]
            hists = np.zeros([0,4])
        
        class Clusters:
            # An array of vlines
            widgs = np.zeros([0,4])
            
        self.wave = Waves()
        self.vlines = Clusters()
        self.canvas.mpl_connect('resize_event',lambda x: self.update_background())
        self.canvas.draw()
    
    def read(self, iteration=None):
        ''' Try to do it in chunks '''
        cnt = 1; step = 50
        
        if iteration is not None: self.cur_iter = iteration
        #print 'cur iter in wv:', self.cur_iter
        while not np.any(np.nonzero(self.cur_iter_chunk > self.cur_iter)[0]):
            next_chunk = np.array([x for x in islice(self.wv_iters,cnt*step)])
            self.cur_iter_chunk = np.concatenate([self.cur_iter_chunk,
                                                  next_chunk])
            cnt += 1

        inds = np.nonzero(self.cur_iter_chunk <= self.cur_iter)[0]
        wv_out = self.wv[self.cur_i+inds]
        #import pdb; pdb.set_trace()
        spks_out = self.cl[self.cur_i+inds]
        #import pdb; pdb.set_trace()
        
        if len(inds) != 0:
            last_ind = inds[-1]
            self.cur_iter_chunk = self.cur_iter_chunk[last_ind+1:]
            self.cur_i += last_ind+1
        self.cur_iter += 1
        return wv_out, spks_out
    
    def draw(self, signal, clusters):
        ''' Signal is Xx4,
            clusters is an array of spk id's.
                where 0 index corresponds to the 
                beginning of the signal vector'''
        
        new_start_i = np.max([0,len(self.wave.hists) + len(signal)-self.t_lim])
        self.wave.hists = np.concatenate([self.wave.hists,signal])[new_start_i:]
        
        for j in range(4):
            self.wave.widgs[j].set_data(range(len(self.wave.hists)),self.wave.hists[:,j])
        
        # Alter old vlines
        i_keep = []
        for i in range(len(self.vlines.widgs)):
            vline0 = self.vlines.widgs[i,0]
            x_dat = vline0.get_xdata()
            if x_dat[0] >= new_start_i:
                for vline in self.vlines.widgs[i,:]:
                    vline.set_xdata(x_dat-new_start_i)
                i_keep.append(i)
        if len(i_keep) > 0:
            self.vlines.widgs = self.vlines.widgs[np.array(i_keep)]
        else:
            self.vlines.widgs = np.zeros([0,4])
        
        # Add new vlines
        new_vlines = []
        for spk_i in np.nonzero(clusters-1)[0]:
            clid = clusters[spk_i,0]
            if clid not in spk_clr.keys(): continue
            x = len(self.wave.hists)-new_start_i+spk_i
            
            #ax = self.axs[0]
            #new_vline, = ax.plot([x]*2,[-10,10],color=spk_clr[clid],animated=True)
            #new_vlines.append(new_vline)
            tmp = []
            for ax, j in zip(self.axs,range(4)):
                new_vline, = ax.plot([x]*2,[-10,10],color=spk_clr[clid],animated=True)
                tmp.append(new_vline)
            new_vlines.append(tmp)
            
        if len(new_vlines) > 0:
            self.vlines.widgs = np.concatenate([self.vlines.widgs,np.array(new_vlines)])
        
        for bg in self.backgrounds:
            self.canvas.restore_region(bg)
        
        for itm,ax in zip(self.wave.widgs,self.axs):
            ax.draw_artist(itm)
        
        for j in range(self.vlines.widgs.shape[1]):
            for i in range(self.vlines.widgs.shape[0]):
                self.axs[j].draw_artist(self.vlines.widgs[i,j])
        
        for ax in self.axs:
            self.canvas.blit(ax.bbox)