
from distutils.command.config import config
from pathlib import Path
from os.path import isfile, join
import shutil
from os import listdir
import re
import math
import pickle
import numpy as np



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
    print('Reading: {}'.format(mgf_file))
    
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

        while not isfloat(re.split(' |\t|=', lines[i])[0]):
            i += 1

        spec_ind = []
        spec_val = []
        num_peaks = 0
        while 'END IONS' not in lines[i].upper():
            if lines[i] == '\n':
                i += 1
                continue
            mz_line = lines[i]
            i += 1
            num_peaks += 1
    return [min_pepmass,max_pepmass]


def count_spectra_in_range(range,mgf_files):
    pass

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
    spectra_per_file = []
    for mgf_files in mgf_files:
        spectra_per_file.append(count_spectra_in_range(intersect_range,mgf_file))
    return spectra_per_file


if __name__ == '__main__':

    #mgf_dir = config.get_config(section='input', key='mgf_dir')
    mgf_dir = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/cancer-mgfs/"
    #prep_dir = config.get_config(section='input', key='prep_dir')

    mgf_files = verify_in_dir(mgf_dir, "mgf", [])
    #create_out_dir(out_dir, exist_ok=False)
        
    #TEST
    mgf_files = mgf_files[:3]

    print('reading {} files'.format(len(mgf_files)))
    
    intersect_range = find_overlapping_range(mgf_files)
    print(intersect_range)

    print(spectra_in_range_per_file(intersect_range))        
