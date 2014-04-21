'''
Created on Apr 20, 2014

@author: jshor
'''
from os import listdir
from os.path import join
import hashlib
import cPickle

cache_loc = 'Data/Analysis/cache'

def _hash_args(args):
    h = hashlib.sha224()
    for arg in args:
        h.update(cPickle.dumps(arg))
    return h.hexdigest()

def try_cache(*args):

    fn = _hash_args(args)

    cached_items = [f for f in listdir(cache_loc)]

    if fn in cached_items:
        with open(join(cache_loc,fn),'r') as f:
            return cPickle.load(f)
    else:
        return None

def store_in_cache(*args):
    ''' Last arg is what to store. '''
    fn = _hash_args(args[:-1])
    with open(join(cache_loc,fn),'w') as f:
        cPickle.dump(args[-1],f)