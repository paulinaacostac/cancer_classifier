from importlib.resources import path
# verifies if cancer data has been downloaded correctly
from os import listdir
import os

path = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/raw_files"
for folder in listdir(path):
    filename = listdir(path+"/"+folder)[0]
    if filename.startswith("Unconfirmed"):
        print("folder ",folder," file ",filename," size ",os.path.getsize(path+"/"+folder+"/"+filename))

