from importlib.resources import path
# verifies if cancer data has been downloaded correctly
from os import listdir
import os
import shutil

path = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/patient_raw_files"
path_dest = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/cancer_raw_files"
for folder in listdir(path):
    filename = listdir(path+"/"+folder)[0]
    print(filename)
    shutil.copy(path+"/"+folder+"/"+filename,path_dest)

