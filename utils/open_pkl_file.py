import pickle
objects = []
mgf_dir = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/"

with (open(mgf_dir+"healthy-pkl-files/08CPTAC_CCRCC_P_JHU_20171214_LUMOS_f01_compact.pkl","rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break

print(objects)
