from matplotlib import pyplot as plt
import numpy as np

from Data.readData import load_mux, load_vl

from Data.Analysis.countAngle import count_angle
from Data.Analysis.classifyTask import get_orientation,find_runs
from Data.Analysis.findAmbiguousData import find_ambiguous_data

vl_sample_rate = 32.0

'''
potential:
    animal 65, session 20
'''

def mk_grph(animal,session):
    room_shape = [[-60,60],[-60,60]]
    cntrx = cntry = 0
    
    fn, _ = load_mux(animal, session)
    vl = load_vl(animal,fn)
    
    if len(np.unique(vl['Task'])) <= 1:
        raise Exception('VL Task not right.')
    xs = np.linspace(0,len(vl['Task'])/vl_sample_rate/60,len(vl['Task']))

    plt.figure()
    angls = count_angle(vl,room_shape)
    plt.plot(xs,angls,label='Angle')
    
    
    scale = (np.max(angls)-np.min(angls))/2.0
    plt.plot(xs,vl['Task']*scale+(np.max(angls)-scale),label='Task')
    
    # Overwrite sections with discrepencies
    
    
    orient = get_orientation(vl,cntrx,cntry)
    #plt.plot(orient*np.max(angls),label='Orientation')
    discrep = np.sum(orient != vl['Task'])
    radial = np.sum(orient == 0)
    txt = ('Discrepency data: %.3f of %i \n'+
           'Radial data: %.3f of %i')%(1.0*(discrep-radial)/(len(orient)-radial), 
                                       len(orient)-radial,
                                       1.0*radial/len(orient), len(orient))
    txt2 = 'Filename: %s'%(fn,)
    plt.autoscale(axis='x',tight=True)
    plt.text(0,plt.ylim()[0],txt)
    plt.text(plt.xlim()[1],plt.ylim()[0],txt2,horizontalalignment='right')
    plt.ylabel('Angle (radians)')
    plt.xlabel('Time (min)')
    plt.legend()
    plt.title('Animal:%i  Session:%i Filename:%s'%(animal,session, fn))

def generate_angle_graphs():
    animal = 66
    session = 60
    mk_grph(animal,session)
    plt.show()
    '''
    amb = find_ambiguous_data()
    for animal in amb.keys():
        for session in amb[animal].keys():
            if amb[animal][session] is None: continue
            #if animal == 66: continue # He's too good!
            mk_grph(animal,session)
        plt.show()'''