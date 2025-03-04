"""
Generates names from trigram transition matrix stored in a binary file
By default generates 10 names of each size from 4 to 10
Checks whether the name already exists
"""

import numpy as np
from numpy.random import choice
import codecs

# Build a dictionnary to check if the name already exists
filepath = "sample_names.txt"
dico = []
with codecs.open(filepath, "r", "utf-8") as lines:
    for l in  lines:
        dico.append(l[:-1])

# Load the trigram count matrix and normalize it
count = np.fromfile("count.bin",dtype="int32").reshape(256,256,256)
s=count.sum(axis=2)
st=np.tile(s.T,(256,1,1)).T
p=count.astype('float')/st
p[np.isnan(p)]=0

# Output file
outfile = "output.txt"
f = codecs.open(outfile,"w","utf-8")

# How many for each target size
quantity = 10
for target_size in range(4,11):
    total = 0
    while total<quantity:
        i=j=0
        result = u''
        while not j==10:
            k=choice(range(256),1,p=p[i,j,:])[0]
            result = result + chr(k)
            i=j
            j=k
        if len(result) == 1+target_size:
            if result[:-1] in dico:
                continue
            else:
                x=result[:-1]
            total += 1
            print(x)
            f.write(x+"\n")
f.close()