
#incomplete
from pyopenms import *
from urllib.request import urlretrieve
from os import listdir
#gh = "https://raw.githubusercontent.com/OpenMS/pyopenms-extra/master"
#urlretrieve (gh + "/src/data/tiny.mzML", "test.mzML")
exp = MSExperiment()
location = "/blue/fsaeed/paulinaacostacev/data/cancer_proj_data/mzML_files/brain/PDC000245/"


print(listdir(location))

MzMLFile().load("01CPTAC_GBM_A_PNNL_20190619_B1S1_f02.mzML", exp)
count = 0
for spec in exp:
  #print ("MS Level:", spec.getMSLevel())
  count += 1
  #for peak in spec:
  #  print (peak.getIntensity())

print(count)

#spec = exp[1]
#mz, intensity = spec.get_peaks()
#print(sum(intensity))

