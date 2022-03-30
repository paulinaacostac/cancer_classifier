
import re

from sqlalchemy import intersect


filename = "/disk/raptor-2/pacos021/data/healthy-mgfs-compact/20120128_EXQ5_KiSh_SA_LabelFree_HeLa_Phospho_Control_rep3_Fr3_compact.mgf"
#filename = "/disk/raptor-2/pacos021/data/healthy-mgfs/20120128_EXQ5_KiSh_SA_LabelFree_HeLa_Phospho_Control_rep3_FT1.mgf"

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
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
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
        if compliant_mass and compliant_charge and num_peaks > 15:
            if mode:
                counter += 1
            else:
                pointers.append(start)
            compliant_mass = compliant_charge = False
    if mode: 
        print("real counter {}".format(real_counter))
        return counter
    return pointers


def f(intersect_range,mgf_file):
    #print('Reading: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()
    print(lines[-2])


intersect_range = [500.278289794922, 1346.155029296875]
pointers = get_valid_spectra(intersect_range,filename,True)

#print(get_valid_spectra([500.278289794922, 1346.155029296875],filename))