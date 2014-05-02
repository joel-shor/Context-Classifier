'''
Created on Apr 28, 2014

@author: jshor
'''

def get_good_clusters(i):
    '''
    0 is all place cells
    1 is for animal 66, session 60
    2 is for animal 70, session 8
    
    Names need to be distinct for caching to work
    '''
    name = ['All clusters', 'Place Cell clusters (66,60)', 
            'Place Cell clusters (70,8)'][i]
    good = [{i: range(2,100) for
             i in range(1,17)},
            
            {1:[2,4,5,6],
             2:[5,6],
             3:[2,3,4,7,8,10,11],
             4:[2,5,6],
             5:[2,3,6,7,9],
             6:[2],
             7:[2,3],
             11:[2],
             12:[2,3]},
            
             {2:range(2,19),
             3:range(2,10),
             4:range(2,20),
             6:[2,3],
             9:[2,3,4,5,6,7,11],
             10:[2,3,4],
             11:[3,4],
             13:[2,3],
             15:[2,3],
             16:[2,3,4]}][i]
    return name, good