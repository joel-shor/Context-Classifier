'''
Created on Mar 22, 2014

@author: jshor
'''
from gtk import WIN_POS_CENTER as pos
#from gtk import WIN_POS_NONE as pos
from matplotlib.patches import FancyArrowPatch as Arrow
from matplotlib.patches import Circle
import logging
import numpy as np

from Reader import Reader

class EnvironmentReader(Reader):
    def __init__(self, vl, room_shape, start_iter):
        super(EnvironmentReader,self).__init__(win_size=[700,700],
                                               win_loc=pos,
                                               title='Environment')
        self.vl = vl
        self.cur_iter = start_iter
        
        self.cur_i = 0
        self.max_iter = np.max(vl['Iter num'])
        self.maxx = room_shape[0][1]
        self.maxy = room_shape[1][1]
        self.cntr_x = np.mean(room_shape[0])
        self.cntr_y = np.mean(room_shape[1])
        
        self.x_hist = []; self.y_hist = []
        
        self.canvas.mpl_connect('resize_event',lambda x: self.update_background())
        
        self.pos, = self.ax.plot([],[],color='g',animated=True)
        self.vel = Arrow([0,0],[1,0],arrowstyle='-|>, head_length=3, head_width=3',
                         animated=True)
        self.ax.add_patch(self.vel)
        self.radius, = self.ax.plot([],[],color='r',animated=True)
        self.clockcounter = self.ax.text(self.maxx,room_shape[1][0],
                                         '',ha='right',size='large',
                                         animated=True)
        self.iters = self.ax.text(self.maxx-1, room_shape[1][0]+3,
                                  '',ha='right',animated=True)
        self.ax.set_xlim(room_shape[0])
        self.ax.set_ylim(room_shape[1])
        
        self.draw_plc_flds()
        
        self.draw_HMM_sectors()
        self.predicted_counter = self.ax.text(self.maxx,room_shape[1][0]+10,'',
                                              ha='right',size='large',animated=True)
        self.prediction_hist = None
        #self.cur_sec = Rectangle([0,0],self.HMM.dx,self.HMM.dy,fill=True,
        #                         color='k',animated=True)
        #self.ax_env.add_patch(self.cur_sec)
        
        self.canvas.draw()
        
    def read(self, iteration=None):
        ''' Return the environment data corresponding to
            the next iteration.
            
            Note that 0 or multiple data points can be
            associated with a single iteration number.
            
            All of the environment data before self.cur_i
            has already been recorded.'''
        if iteration is not None: self.cur_iter = iteration
        try:
            
            cur_j = 1+self.cur_i+ np.nonzero(self.vl['Iter num'][self.cur_i:] == self.cur_iter)[0][-1]
        except:
            # There is no iteration with that value
            self.cur_iter += 1
            return [np.NAN, np.NAN, np.NAN, np.NAN]
        cur_x = self.vl['xs'][self.cur_i:cur_j]
        cur_y = self.vl['ys'][self.cur_i:cur_j]
        cur_vx = self.vl['vxs'][self.cur_i:cur_j]
        cur_vy = self.vl['vys'][self.cur_i:cur_j]
        self.cur_iter += 1
        self.cur_i = cur_j

        return (cur_x, cur_y, cur_vx, cur_vy)
    
    def draw_HMM_sectors(self):
        return
        for i in range(self.HMM.cll_p_sd):
            curx = self.HMM.xrange[0]+i*self.HMM.dx
            cury = self.HMM.yrange[0]+i*self.HMM.dy
            self.ax_env.plot([curx,curx],[0,self.maxy],'k')
            self.ax_env.plot([0,self.maxx],[cury,cury], 'k')

        
    def draw_plc_flds(self):
        return
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
        self.ax.legend(legend_widgets, ('counterclockwise','clockwise'),'lower right')
    
    def draw(self, xs,ys,vxs,vys):
        ''' Display the environment data to the window.
        
            The environment data are inputs. '''
        
        self.iters.set_text('%i/%i'%(self.cur_iter,self.max_iter))
        
        if np.any(np.isnan(xs)):
            return
        
        self.canvas.restore_region(self.background)
        
        x = xs[-1]; y=ys[-1]; vx=vxs[-1]; vy=vys[-1]
        
        self.x_hist.extend(xs)
        self.y_hist.extend(ys)
        
        self.pos.set_data(self.x_hist,self.y_hist)
        if vx != 0 or vy != 0: 
            self.vel.set_positions([x, y], [x+vx,y+vy])
        self.radius.set_data([self.cntr_x,x],[self.cntr_y,y])

        if self.is_clockwise(x,y,vx,vy) == 1:
            self.clockcounter.set_text('Clockwise')
        else:
            self.clockcounter.set_text('Counterclockwise')

        try:
            self._make_prediction(self.is_clockwise(x,y,vx,vy))
        except:
            pass
            #logging.warning('Make prediction failed.')

        for itm in [self.pos, self.vel, self.radius,
                    self.clockcounter,self.iters, self.predicted_counter]:
            self.ax.draw_artist(itm)
        
        self.canvas.blit(self.ax.bbox)

    def is_clockwise(self,x,y,vx,vy):
        ''' Determines if motion is clockwise around the center
            of the room, which is [0, MAXX] x [0, MAXY] '''
        cross_prod = (x-self.cntr_x)*vy - (y-self.cntr_y)*vx
        clockwise = True if cross_prod < 0 else False
        return 1 if clockwise else 0