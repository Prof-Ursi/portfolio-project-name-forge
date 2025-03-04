# Count the occurence of unicode characters trigrams in a text file

import numpy as np
import codecs


filepath = "sample_names.txt"

count = np.zeros((256,256,256),dtype='int32')

with codecs.open(filepath, "r", "utf-8") as lines:
    for l in  lines:
        i = j = 0
        for k in [ord(c) for c in list(l)]:
            count[i,j,k] += 1
            i = j
            j = k
count.tofile("count.bin")