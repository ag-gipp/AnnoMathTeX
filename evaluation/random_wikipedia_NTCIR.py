mypath = "E:\\Downloads/NTCIR-12_MathIR_Wikipedia_Corpus"

from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

print("end")