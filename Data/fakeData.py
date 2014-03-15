''' This is a place holder '''
from random import random

def rand_walk(step_num=100,step_size=.5,maxx=10,maxy=10):
    xs = [0]; ys=[0]; vx=[0]; vy=[0]
    for i in range(step_num):
        vxnew = step_size*(random()*2-1)
        if vxnew > .95*step_size: vxnew -= vx[-1]
        while abs(xs[-1] + vx[-1] + vxnew) > maxx:
            vxnew = -vx[-1] + step_size*(random()*2-1)
        vynew = step_size*(random()*2-1)
        if vynew > .95*step_size: vynew -= vy[-1]
        while abs(ys[-1] + vy[-1] + vynew) > maxy:
            vynew = -vy[-1] + step_size*(random()*2-1)

        vx.append(vx[-1] + vxnew)
        vy.append(vy[-1] + vynew)
        xs.append(xs[-1] + vx[-1])
        ys.append(ys[-1] + vy[-1])
        
    return xs,ys,vx,vy

    