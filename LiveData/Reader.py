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

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas


class Reader(object):
    def __init__(self,win_size, win_loc, title):
        self.top = gtk.Window()
        self.top.connect('delete-event', gtk.main_quit)
        self.top.set_title(title)
        self.top.set_position(gtk.WIN_POS_CENTER)
        self.top.set_default_size(win_size,win_size)
        
        fig = Figure()
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvas(fig)
        self.top.add(self.canvas)
        self.top.show_all()
        
        self.update_background()
        
    def update_background(self):
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
    
    def draw(self):
        raise Exception('Not implemented.')
    
    def read(self):
        raise Exception('Not implemented yet.')