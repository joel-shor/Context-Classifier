'''
Created on Apr 9, 2014

@author: jshor

The Dot Product classifier as described by Jezek, et al (2011)
'''

import numpy as np

# Technically, it is important to keep bin_id and bin_index seperate
#  The reason is that bin_id is arbitrary, but bin_index must be able to
#  be put into the indices of an array/matrix
def bin_id(xbin,ybin,y_bin_len):
    return xbin*y_bin_len + ybin + 1

def bin_index(xbin,ybin,y_bin_len):
    # This has to be a valid index...ie 0 to the end
    return bin_id(xbin,ybin,y_bin_len)-1
def bin_ind_inv(b_id, y_bin_len):
    xbin = b_id/y_bin_len
    ybin = b_id%y_bin_len
    return (xbin,ybin)

def bin_indicator(x,y,xblen,yblen,bin_size,room_shape):
    indicator = np.zeros([len(x),1])
    left_edge = room_shape[0][0]
    bottom_edge = room_shape[1][0]
    
    for xbin in range(xblen):
        minx = xbin*bin_size+left_edge
        maxx = (xbin+1)*bin_size+left_edge
        in_x_strip = (x>=minx)&(x<maxx)
        
        for ybin in range(yblen):
            miny = ybin*bin_size+bottom_edge
            maxy = (ybin+1)*bin_size+bottom_edge
            in_y_strip = (y>=miny)&(y<maxy)
            
            in_bin = in_x_strip & in_y_strip
            
            bid = bin_id(xbin,ybin,yblen)
            
            indicator[in_bin] = bid
    return indicator

def cell_id(tetrode,cell,t_cells):
    return t_cells.keys().index((tetrode,cell))

def spk_indicators(t_cells,n):
    ''' t_cells is a dictionary of {(tetrode, cell): spk_i}
        n is total length of time
        
        Use the old power of 2 trick
     '''
    
    indicator = np.zeros(n)
    for tetrode,cell in t_cells.keys():
        spk_i = t_cells[(tetrode,cell)]
        indicator[spk_i] += 2**cell_id(tetrode, cell,t_cells)
    return indicator

def pos_to_xybin(x,y, xblen,yblen,bin_size,room_shape):
    ''' Convert from position to bin coordinates '''
    left_edge = room_shape[0][0]
    bottom_edge = room_shape[1][0]
    
    for xbin in range(xblen):
        minx = xbin*bin_size+left_edge
        maxx = (xbin+1)*bin_size+left_edge
        if not (x>=minx)&(x<maxx): continue
        
        for ybin in range(yblen):
            miny = ybin*bin_size+bottom_edge
            maxy = (ybin+1)*bin_size+bottom_edge
            if not (y>=miny)&(y<maxy): continue
            return (xbin,ybin)
    print 'Position not in a bin'
    import pdb; pdb.set_trace()
    raise Exception('Position is not in a bin')

if __name__ == '__main__':
    from itertools import product
    for xbin,ybin in product(range(50),range(50)):
        assert (xbin,ybin) == bin_ind_inv(bin_index(xbin,ybin,50),50)