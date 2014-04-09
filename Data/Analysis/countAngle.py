'''
Created on Apr 3, 2014

@author: jshor
'''
import numpy as np
from numpy import power as powr

def count_angle(vl, room_shape):
    ''' Generate the cumulative, signed angle traveled. '''
    
    [[minx,maxx],[miny,maxy]] = room_shape
    if maxx-minx != maxy-miny:
        raise Exception('Room shape assumptions not accurate.')
    xcntr = np.mean([minx,maxx])
    ycntr = np.mean([miny,maxy])
    
    def mag(vx,vy):
        return np.sqrt(powr(vx,2)+powr(vy,2))
    
    def get_angle(x1,y1,x0,y0):
        vx1=x1-xcntr; vx0=x0-xcntr
        vy1=y1-ycntr; vy0=y0-ycntr
        
        sin_ang = (vx1*vy0-vy1*vx0)/(mag(vx1,vy1)*mag(vx0,vy0))
        return np.arcsin(sin_ang)
    x1 = vl['xs'][1:]; x0 = vl['xs'][:-1]
    y1 = vl['ys'][1:]; y0 = vl['ys'][:-1]
    da_s = np.concatenate([[0],get_angle(x1,y1,x0,y0)])
    return np.cumsum(da_s)
        
 
    