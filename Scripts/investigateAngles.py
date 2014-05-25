'''
Created on Mar 29, 2014

@author: jshor
'''

from Analysis.findAmbiguousData import find_ambiguous_data
from Figures.generateAngleGraphs import mk_grph
from matplotlib import pyplot as plt
import logging

def investigate_angle_graphs():
    amb = find_ambiguous_data()
    
    # Get a blob of data
    tmp = [(an,sess,1.0*dd[0]/dd[2], 1.0*(dd[1]-dd[0])/(dd[2]-dd[0]),dd[2]) 
           for (an, dat) in amb.items()  
           for (sess,dd) in dat.items() if dd is not None]
    
    
    tmp.sort(key=lambda x:x[3],reverse=True)
    
    for i in range(len(tmp)):
        if i < 254: continue
        logging.info('%i/%i',i,len(tmp))
        (animal, session, _,_,_) = tmp[i]
        try:
            mk_grph(animal,session)
        except Exception as e:
            print e
            continue
        plt.show()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    investigate_angle_graphs()