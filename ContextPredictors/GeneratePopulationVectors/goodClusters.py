'''
Created on Apr 28, 2014

@author: jshor
'''

def get_good_clusters(i):
    name = ['All clusters', 'Place Cell clusters'][i]
    good = [{1:range(2,8),
                 2:range(2,8),
                 3:range(2,14),
                 4:range(2,7),
                 5:range(2,12),
                 6:[2],
                 7:[2,3,4],
                 11:[2],
                 12:[2,3]},
            {1:[2,4,5,6],
                 2:[5,6],
                 3:[2,3,4,7,8,10,11],
                 4:[2,5,6],
                 5:[2,3,6,7,9],
                 6:[2],
                 7:[2,3],
                 11:[2],
                 12:[2,3]}][i]
    return name, good