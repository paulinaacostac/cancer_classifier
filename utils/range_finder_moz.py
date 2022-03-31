
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
# valid spectra when withing intersect_range, charge <= 4 and num of peaks > 15
# mode-> True: returns count ; False: returns pointers
def get_valid_spectra(intersect_range,mgf_file,mode):
    print('Generating pointers for: {}'.format(mgf_file)) if not mode else print('Counting: {}'.format(mgf_file))
    #print('Reading: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()
    i = 0
    is_mw = False

    real_counter = 0
    pointers = []
    counter = 0
    compliant_mass = compliant_charge = False
    # cancer files are partially sorted
    while i < len(lines):
        line = lines[i]
        i += 1
        num_peaks = 0
        if line.startswith('BEGIN IONS'):
            start = i-1 #the pointer moved to the next line already.
            real_counter +=1
        if line.startswith('PEPMASS'):
            mass = round(float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])*1000)
            if mass > intersect_range[0] and mass < intersect_range[1]:  
                compliant_mass = True
            else: 
                if mode: print("mass {} not valid".format(mass))
                compliant_mass = False
                continue
        if compliant_mass and line.startswith('CHARGE'):
            l_charge = int(re.findall(r"CHARGE=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if l_charge <= 4:
                compliant_charge = True
            else:
                if mode: print("charge {} not valid".format(l_charge))
                compliant_charge = compliant_mass = False
                continue
        if compliant_mass and compliant_charge:
            while i < len(lines) and 'END IONS' not in lines[i].upper():
                if isfloat(re.split(' |\t|=', lines[i])[0]): num_peaks += 1
                i+=1
                
        if compliant_mass and compliant_charge and num_peaks > 15:
            #if mode:
            #    counter += 1
            #else:
            pointers.append(start)
            compliant_mass = compliant_charge = False
            num_peaks = 0

        if mode and num_peaks <= 15 and compliant_charge and compliant_mass: 
            print("peaks {} not valid at line {}".format(num_peaks,start))
            #print(lines[start-50:start+30])
    if mode: 
        print("Num all spectra in file {}".format(real_counter))
        return len(pointers)
    return pointers
def get_valid_spectra_folder(intersect_range,mgf_files):
    counter = 0
    min_spectra = float("inf")
    max_spectra = -1
    for i,mgf_file in enumerate(mgf_files):
        t0 = time.time()
        count_spectra_file = get_valid_spectra(intersect_range,mgf_file,True)
        counter += count_spectra_file
        min_spectra = min(count_spectra_file,min_spectra)
        max_spectra = max(count_spectra_file,max_spectra)
        print("file: {}    |    spectra_count: {}    |    progress: {}/{} ({})".format(str(mgf_file.split("/")[-1]),str(count_spectra_file),str(i), str(len(mgf_files)),str(round(i/len(mgf_files),2))))
    return [counter, max_spectra, min_spectra]
def write_new_mgf_file(mgf_out,min_spectra,intersect_range,mgf_file):
    #pointers = generate_pointers(mgf_file,intersect_range)
    pointers = get_valid_spectra(intersect_range,mgf_file,False)
    print("num valid spectra: {}".format(len(pointers)))
    print("range: ",find_range_file(mgf_file))

    f = open(mgf_file,"r")
    lines = f.readlines()
    f.close()

    directory = "/".join(mgf_file.split("/")[:-1])+"-compact"
    filename = mgf_file.split("/")[-1].split(".")[0]
    new_filename = directory+"/"+filename+"_compact.mgf"
    f = open(new_filename,"w")
    print('Writing: {}'.format(new_filename.split("/")[-1]))

    random_pointers = random.sample(pointers,min_spectra)
    print("len random pointers: {} == min spectra: {}".format(len(random_pointers),min_spectra))
    for p in random_pointers:
        line_pointer = p
        num_peaks = 0
        if not lines[line_pointer].startswith("BEGIN IONS"):
            print("not begin ions in line {}".format(line_pointer))
        while not lines[line_pointer].startswith('END IONS'):
            if isfloat(re.split(' |\t|=', lines[line_pointer])[0]): num_peaks += 1
            f.write(lines[line_pointer])
            line_pointer += 1
        
        if num_peaks <= 15:
            print("num peaks in write func: {}".format(num_peaks))
            print("p: {}".format(p))
            
            print(lines[p:line_pointer+1])
        f.write(lines[line_pointer])
        f.write('\n')
    f.close()

    print("verifying file {}".format(new_filename))
    real_count = get_valid_spectra(intersect_range,new_filename,True)
    print("real count: {} expected count: {}".format(real_count,min_spectra))
    if real_count == min_spectra: 
        print("file {} verified".format(new_filename))
    else: 
        print("file {} not valid".format(new_filename))
        exit()

 #weird func       
def generate_pointers(mgf_file,intersect_range):
    print('Generating pointers for: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()

    pointers = []
    i=0
    compliant_mass = compliant_charge = False
    # cancer files are partially sorted
    while i < len(lines):
        line = lines[i]
        i += 1
        num_peaks = 0
        if line.startswith('BEGIN IONS'):
            start = i-1 #the pointer moved to the next line already.
        if line.startswith('PEPMASS'):
            mass = round(float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0]),3)
            if mass >= intersect_range[0] and mass <= intersect_range[1]:  
                compliant_mass = True
            else: compliant_mass = False
        if compliant_mass and line.startswith('CHARGE'):
            l_charge = int(re.findall(r"CHARGE=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if l_charge <= 4:
                compliant_charge = True
            else: compliant_charge = False
        if compliant_mass and compliant_charge:
            while i < len(lines) and 'END IONS' not in lines[i].upper():
                num_peaks += 1
                i+=1
        #print("num peaks {}".format(num_peaks))
        if compliant_mass and compliant_charge and num_peaks > 15:
            pointers.append(start)
            compliant_mass = compliant_charge = False
    return pointers
def write_new_mgfs(mgf_out,min_spectra,mgf_files,intersect_range):     
    for mgf_file in mgf_files:
        write_new_mgf_file(mgf_out,min_spectra,intersect_range,mgf_file)
        #p = Process(target=write_new_mgf_file, args=(mgf_out,min_spectra,intersect_range,mgf_file))
        #p.start()
        #p.join()
def get_mgffiles(dirs,mgf_dir):
    mgf_files = []
    for directory in dirs:
        mgf_files.extend(verify_in_dir(mgf_dir+directory, "mgf", []))
    return mgf_files

if __name__ == '__main__':
    t0 = time.time()
    dirs = ["healthy-mgfs/","cancer-mgfs/"]
    mgf_dir = "/disk/raptor-2/pacos021/data/"
    mgf_out = "/disk/raptor-2/pacos021/data/"
    #create_out_dir(mgf_out, exist_ok=False)
    mgf_files = get_mgffiles(dirs,mgf_dir)

    #TEST
    mgf_files = [mgf_files[2]]

    print('reading {} files'.format(len(mgf_files)))
    intersect_range = [500278, 1346155] #[500.278289794922, 1346.155029296875] #[500.278289794922, 1346.155029296875] # or None if we dont know the range. Calculated 3/11/2022
    if not intersect_range:
        intersect_range = find_overlapping_range(mgf_files)
        f = open(join(mgf_out,"range.txt"),"w")
        f.write(str(intersect_range))
        f.close()
    print(intersect_range)

    #min_spectra will become the num of spectra per mgf file we will use
    #within that intersect_range, lets choose as many spectra as min_spectra is but distributed randomly in that range
    min_spectra = 5587 #None  # or None if we dont know the min espectra. Calculated 3/23/2022
    if not min_spectra:
        counter,_,min_spectra = get_valid_spectra_folder(intersect_range,mgf_files)
        f = open(join(mgf_out,"min_spectra.txt"),"w")
        f.write(str(min_spectra))
        f.close()
    print("min_spectra: ",min_spectra)
        
    write_new_mgfs(mgf_out,min_spectra,mgf_files,intersect_range) #add num files
    print("total time {}".format(round(time.time()-t0,2)))

    # to verify
    print("verifying")
    dirs = ["healthy-mgfs-compact/","cancer-mgfs-compact/"]
    mgf_files = get_mgffiles(dirs,mgf_dir)
    counter,max_spectra,min_spectra = get_valid_spectra_folder(intersect_range,mgf_files)
    print("total num_spectra: {} | max_spectra: {} | min_spectra: {} | total num_files: {}".format(counter,max_spectra,min_spectra,len(mgf_files)))

    # get pepmass distribution for each file