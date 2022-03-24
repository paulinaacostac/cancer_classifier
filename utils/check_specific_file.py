import re

filename = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/guot_L130410_001c_SW-kt1.mgf"

def generate_pointers(mgf_file,intersect_range):
    #print('Reading: {}'.format(mgf_file))
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
            start = i
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
        #print("num peaks {}".format(num_peaks))
        if compliant_mass and compliant_charge and num_peaks > 15:
            pointers.append(start)
            compliant_mass = compliant_charge = False
    return pointers

def count_valid_spectra(intersect_range,mgf_file):
    #print('Reading: {}'.format(mgf_file))
    f = open(mgf_file, "r")
    lines = f.readlines()
    f.close()
    i = 0
    counter = 0
    compliant_mass = False
    # cancer files are partially sorted
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith('PEPMASS'):
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if mass >= intersect_range[0] and mass <= intersect_range[1]: 
                compliant_mass = True
            else: compliant_mass = False
        if line.startswith('CHARGE'):
            l_charge = int(re.findall(r"CHARGE=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if l_charge <= 4 and compliant_mass:
                counter += 1
                compliant_mass = False
    return counter

def count_valid_spectra2(intersect_range,piece):
    #print('Reading: {}'.format(mgf_file))
    i = 0
    counter = 0
    compliant_mass = False
    # cancer files are partially sorted
    while i < len(piece):
        line = piece[i]
        i += 1
        if line.startswith('PEPMASS'):
            mass = float(re.findall(r"PEPMASS=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if mass >= intersect_range[0] and mass <= intersect_range[1]: 
                compliant_mass = True
            else: compliant_mass = False
        if line.startswith('CHARGE'):
            l_charge = int(re.findall(r"CHARGE=([-+]?[0-9]*\.?[0-9]*)", line)[0])
            if l_charge <= 4 and compliant_mass:
                counter += 1
                compliant_mass = False
    return counter

def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

count = 0
with open(filename) as f:
    for piece in read_in_chunks(f):
        count += count_valid_spectra2([500.278289794922, 1346.155029296875],piece)

print(count)


# f = open(filename,"r")
# lines = f.readlines()
# f.close()
# i=0
# pointers = generate_pointers(filename,[500.278289794922, 1346.155029296875])
# vals = count_valid_spectra([500.278289794922, 1346.155029296875], filename)
# print(len(pointers))
# print(vals)



