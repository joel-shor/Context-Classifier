'''
Created on Mar 22, 2014

@author: jshor
'''

try:
    import pygtk
    pygtk.require("2.0")
except:
    raise Exception()
import gtk

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

class Reader(object):
    def __init__(self,win_size, win_loc, title,subplot_dim=[1,1]):
        self.top = gtk.Window()
        self.top.connect('delete-event', gtk.main_quit)
        self.top.set_title(title)
        self.top.set_position(gtk.WIN_POS_CENTER)
        self.top.set_default_size(*win_size)
        
        self.fig = Figure()
        
        self.axs = [self.fig.add_subplot(subplot_dim[0],
                                           subplot_dim[1],
                                           i+1) for i in
                    range(np.prod(subplot_dim))]
        self.canvas = FigureCanvas(self.fig)
        self.top.add(self.canvas)
        self.top.show_all()
        
        self.backgrounds = [self.update_background(ax) for ax in
                            self.axs]
        if len(self.axs) == 1:
            self.ax = self.axs[0]
            self.background = self.backgrounds[0]
            
        
    def update_background(self,ax):
        self.canvas.draw()
        return self.canvas.copy_from_bbox(ax.bbox)
    
    def draw(self):
        raise Exception('Not implemented.')
    
    def read(self):
        raise Exception('Not implemented yet.')