'''
Created on May 14, 2014

@author: jshor
'''
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def cluster_count():
    mpl.rcParams['font.size'] = 26
    cells = []
    animal = []
    with open('GenerateFigures/Images/how many clusters.txt', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        spamreader.next()
        for row in spamreader:
            #import pdb; pdb.set_trace()
            cell = int(row[0].split('    ')[-1])
            if cell == 0: continue
            cells.append(cell)
            animal.append(int(row[0].split('    ')[0]))
    
    print 'Average number of cells:', np.mean(cells)
    print 'Max cells:', np.max(cells)
    print 'Total number of animals:', len(np.unique(animal))
    print 'Animals:', np.unique(animal)
    print 'Total number of sessions:', len(cells)
    plt.hist(cells)
    plt.title('Cell Data')
    plt.xlabel('Number of Cells')
    plt.ylabel('Count')
    plt.show()
