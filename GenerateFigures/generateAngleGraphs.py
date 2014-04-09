from matplotlib import pyplot as plt
from Data.readData import load_mux, load_vl

from Data.Analysis.countAngle import count_angle

def generate_angle_graphs():
    animal = 66
    session = 60 # This is August 7, 2013 run
    room_shape = [[-60,60],[-60,60]]
    
    fn, _ = load_mux(animal, session)
    vl = load_vl(animal,fn)
    
    angls = count_angle(vl,room_shape)
    plt.plot(angls)
    plt.show()