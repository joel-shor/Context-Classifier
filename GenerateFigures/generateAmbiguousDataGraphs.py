'''
Created on Apr 21, 2014

@author: jshor
'''

from Data.Analysis.findAmbiguousData import find_ambiguous_data

def generate_ambiguous_data_graphs():
    ''' Amb is in the form of 
    # Final data structure will be a dictionary:
    #  amb[animal][session] = (# radial, #discrepency, total) '''
    
    amb = find_ambiguous_data()
    
    # Get a blob of data
    tmp = [(an,sess,1.0*dd[0]/dd[2], 1.0*(dd[1]-dd[0])/(dd[2]-dd[0]),dd[2]) 
           for (an, dat) in amb.items()  
           for (sess,dd) in dat.items() if dd is not None]
    
    
    tmp.sort(key=lambda x:x[3])
    print '(Animal,Session):    Fraction radial    Fraction Discrepency    Total # data points'
    for animal,sess,rad,disc,tot in tmp:
        print '(%i,%i):    %.3f    %.3f    %i'%(animal,sess,rad,disc,tot)
