from Data.readData import load_mux, load_wv, load_vl, load_cl
from matplotlib import pyplot as plt
from Data.Analysis.getClusters import spike_loc


import numpy as np

fn, trigger_tm = load_mux(animal, session)
cl = load_cl(animal,fn,tetrode)
vl = load_vl(animal,fn)