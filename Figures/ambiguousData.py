'''
Created on Apr 21, 2014

@author: jshor
'''
descr = '''
Plot the (animal, session) combinations as a function of ambiguous data.
These are moments in time when the clockwiseness of the task is not the same
as the the clockwiseness of the rat's motion.
'''
import logging

from Analysis.findAmbiguousData import find_ambiguous_data

def ambiguous_data_graphs():
    ''' Amb is in the form of 
     Final data structure will be a dictionary:
      amb[animal][session] = (# radial, #discrepency, total) '''
    
    logging.info(descr)
    
    amb = find_ambiguous_data()
    
    # Get a blob of data
    tmp = [(an,sess,1.0*dd[0]/dd[2], 1.0*(dd[1]-dd[0])/(dd[2]-dd[0]),dd[2]) 
           for (an, dat) in amb.items()  
           for (sess,dd) in dat.items() if dd is not None]
    
    
    tmp.sort(key=lambda x:x[3])
    print '(Animal,Session):    Fraction radial    Fraction Discrepency    Total # data points'
    for animal,sess,rad,disc,tot in tmp:
        print '(%i,%i):    %.3f    %.3f    %i'%(animal,sess,rad,disc,tot)
