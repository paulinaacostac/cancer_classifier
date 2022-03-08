import numpy as np

var = np.load('../pickle_files/means.npy')
var_1 = np.load('../pickle_files/stds.npy')
print("mean: ",var," len: ",len(var))
print("stds: ",var_1," len: ",len(var_1 ))