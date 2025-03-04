v0.1 : First version of the python generator, working.

# How to use :
## 1. run the trigram counter
    python3 trigram_counter.py 

    It will create the count.bin file containing the probability matrix of the different trigram combinations of the names present in the sample_names.txt file.
## 2. run the name generator
    python3 name_generator.py

    name_generator.py will use the probability matrix contained in count.bin to generate new names through a markov chain process and will list them in output.txt.