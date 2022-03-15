
from distutils.command.config import config
from pathlib import Path
from os.path import isfile, join
import shutil
from os import listdir
import re
import math
import pickle
import numpy as np
import random
import time
from multiprocessing import Process


def isfloat(str_float):
    try:
        float(str_float)
        return True
    except ValueError: 
        return False

def create_out_dir(dir_path, exist_ok=True):
    out_path = Path(dir_path)
    if out_path.exists() and out_path.is_dir():
        if not exist_ok:
            shutil.rmtree(out_path)
            out_path.mkdir()
    else:
        out_path.mkdir()

def verify_in_dir(dir_path, ext, ignore_list):
    in_path = Path(dir_path)
    print(in_path)
    assert in_path.exists() and in_path.is_dir()
    
    files = [join(dir_path, f) for f in listdir(dir_path) if
                 isfile(join(dir_path, f)) and not f.startswith('.') 
                 and f.split('.')[-1] == ext and f not in ignore_list]

    assert len(files) > 0
    return files

def find_range_file(mgf_file):
    print('Finding range for: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()

    i = 0
    is_mw = False
    max_pepmass = -1
    min_pepmass = float("inf")
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith('PEPMASS'):
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            max_pepmass = max(mass,max_pepmass)
            min_pepmass = min(mass,min_pepmass)
    return [min_pepmass,max_pepmass]


def count_spectra_in_range(intersect_range,mgf_file):
    #print('Reading: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()

    i = 0
    is_mw = False

    counter = 0
    # cancer files are partially sorted
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith('PEPMASS'):
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if mass >= intersect_range[0] and mass <= intersect_range[1]: 
                counter += 1

    #print("len pointers: ",len(pointers), " counter: ",counter)
    return counter

def find_overlapping_range(mgf_files):
    ranges = []
    for mgf_file in mgf_files:
        ranges.append(find_range_file(mgf_file))
    
    start,end = ranges.pop()
    while ranges:
        start_temp, end_temp = ranges.pop()
        start = max(start,start_temp)
        end = min(end,end_temp)
    
    return [start,end]

def spectra_in_range_per_file(intersect_range,mgf_files):
    counter = 0
    min_spectra = float("inf")
    max_spectra = -1
    for i,mgf_file in enumerate(mgf_files):
        t0 = time.time()
        count_spectra_file = count_spectra_in_range(intersect_range,mgf_file)
        counter += count_spectra_file
        min_spectra = min(count_spectra_file,min_spectra)
        max_spectra = max(count_spectra_file,max_spectra)
        print("file: "+mgf_file.split("/")[-1]+"    |    spectra_count: "+str(count_spectra_file)+"    |    progress: "+str(i)+"/"+str(len(mgf_files)+" ("+str(round(i//len(mgf_files),2))+")"+"     |    time: "+str(round(time.time()-t0,2))))
    return [counter, max_spectra, min_spectra]

def write_new_mgf_file(mgf_out,pointers,min_spectra,mgf_file):

    f = open(mgf_file,"r")
    lines = f.readlines()
    f.close()

    directory = "/".join(mgf_file.split("/")[:-1])+"-compact"
    filename = mgf_file.split("/")[-1].split(".")[0]
    new_filename = join(directory,"/",filename,"_compact.mgf")
    f = open(new_filename,"w")
    print('Writing: {}'.format(new_filename.split("/")[-1]))

    pointers = random.sample(pointers,min_spectra)
    for p in pointers:
        i = p
        while not lines[i].startswith('END IONS'):
            f.write(lines[i])
            i+=1
        f.write(lines[i])
        f.write('\n')
    f.close()

def generate_pointers(mgf_file,intersect_range):
    #print('Reading: {}'.format(mgf_file))
    pointers = generate_pointers(mgf_file,intersect_range)

    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()

    pointers = []
    # cancer files are partially sorted
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith('BEGIN IONS'):
            start = i
        if line.startswith('PEPMASS'):
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if mass >= intersect_range[0] and mass <= intersect_range[1]:  
                pointers.append(start)
    
    return pointers

def write_new_mgfs(mgf_out,min_spectra,mgf_files,intersect_range):     
    for mgf_file in mgf_files:
        t0 = time.time()
        p = Process(target=write_new_mgf_file, args=(mgf_out,pointers,min_spectra,intersect_range,mgf_file))
        p.start()
        p.join()
        #print("file {}       |       len pointers within range: {}       |       progress: {}/{} ({})    |    time: {}".format(mgf_file.split("/")[-1],len(pointers),i,len(mgf_files),round(i/len(mgf_files),2),round(time.time()-t0,2)))

#20111225_EXQ5_KiSh_SA_LabelFree_HeLa_Phospho_Control_rep4_FT3.raw

if __name__ == '__main__':
    t0 = time.time()
    #mgf_dir = config.get_config(section='input', key='mgf_dir')
    dirs = ["healthy-mgfs/","cancer-mgfs/"]
    mgf_dir = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/"
    mgf_out = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/"
    #prep_dir = config.get_config(section='input', key='prep_dir')

    mgf_files = []
    for directory in dirs:
        mgf_files.extend(verify_in_dir(mgf_dir+directory, "mgf", []))
    #create_out_dir(out_dir, exist_ok=False)
     
    #TEST
    #mgf_files = [mgf_files[270],mgf_files[271],mgf_files[272]]

    print('reading {} files'.format(len(mgf_files)))
    
    intersect_range = [500.278289794922, 1346.155029296875] # or None if we dont know the range. Calculated 3/11/2022
    if not intersect_range:
        intersect_range = find_overlapping_range(mgf_files)
    print(intersect_range)

    #f = open(join(mgf_out,"range.txt"),"w")
    #f.write(str(intersect_range))
    #f.close()
    # min_spectra will become the num of spectra per mgf file we will use
    # within that intersect_range, lets choose as many spectra as min_spectra is but distributed randomly in that range

    counter,_,min_spectra = spectra_in_range_per_file(intersect_range,mgf_files)
    print("min_spectra: ",min_spectra)
    f = open(join(mgf_out,"min_spectra.txt"),"w")
    f.write(str(min_spectra))
    f.close()

    write_new_mgfs(mgf_out,min_spectra,mgf_files,intersect_range) #add num files
    print("total time {}".format(round(time.time()-t0,2)))
