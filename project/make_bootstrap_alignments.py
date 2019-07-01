#!/usr/bin/python3

from numpy import *
from dendropy import *

import os
import re
import subprocess
import sys
import shutil

source = "src_make_bootstrap_alignments/"
sys.path.append(source)

from aligner import *
from treebuilder import *
from bootstrapper import *

###################### User input (or derived from user input) ###########################
assert(len(sys.argv) == 6), "\n USAGE: python3 make_bootstrap_alignments.py <fastafile> <output directory> <protein/dna> <num bootstraps> <threads>"


unaligned   = sys.argv[1]        # infile
outpath     = sys.argv[2]        # outpath
alphabet    = sys.argv[3].upper()  # This should be either "AA" or "DNA"
n           =  int(sys.argv[4])  # bootstraps
numproc     =  int(sys.argv[5])  # threads
os.environ["OMP_NUM_THREADS"] = str(numproc)

prealn_file = 'prealn.fasta' # Will contain the raw (unaligned) sequences in fasta format
refaln_file = 'refaln.fasta' # Will contain the reference (unmasked!) alignment
prefix      = unaligned.split(".fasta")[0]

#BootDir     =  prefix + "_alnversions/"
if (os.path.exists(outpath)):
	for file in os.listdir(outpath):
		os.remove(outpath+file)	
else:
	os.mkdir(outpath)
	assert(os.path.exists(outpath))
os.chdir(outpath)	
os.system("cp ../" + unaligned + " " + prealn_file)

############################### Internal variables #######################################

# Aligner
amod = MafftAligner("mafft", " --auto --quiet ")
if alphabet == "DNA":
    addarg = " -nt "
else:
    addarg = " "
tmod = builderFastTree("FastTreeMP", " -fastest -nosupport -quiet -nopr" + addarg) # -nosupport **MUST** be there
bmod = BootstrapperLight(bootstraps = n, prealn_file = prealn_file, refaln_file = refaln_file, BootDir = outpath, 
                           threads = numproc, aligner=amod, tree_builder = tmod, srcdir = source)
                           
#print("making base alignment")
amod.makeAlignment(prealn_file, refaln_file)

#print("bp trees, aln")
bmod.bootstrap()	

 
for i in range(1, n+1):
     os.system("mv alnversion" + str(i) + ".fasta " + prefix + "_alnversion_" + str(i) + ".fasta")
os.system("rm *txt *tre prealn.fasta refaln.BS")
os.system("mv refaln.fasta " + prefix + "_alnversion_" + str(n+1) + ".fasta")
