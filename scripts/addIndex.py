#!/usr/bin/env python

# --------------------------------------------------------------------------
# To be run after OligoMiner pipeline; reads in probes.bed files.
# Reads in a tab-delim config file with sample names and index info,
#   and creates an updated version of the probes.bed files with indexes added,
#   ready for ordering at IDT/TWIST/etc.
# Requires valid column names for config file:
#   name: sample name (same as column 4 of OligoMiner input)
#   suffix: full .bed suffix used (to differentiate between various filters)
#   uniF: forward universal primer name; shared among pool
#   uniR: reverse universal primer name; shared among pool
#   barcodes: comma-separated barcode indexes; unique per sample
# In the future, I could edit the script to have backstreet options, etc. 
# --------------------------------------------------------------------------

import argparse
import csv
import sys

# Read in config input file from command line
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", 
                    required = True,
                    help="Probe bed file including sequence info")
parser.add_argument("--uniF", 
                    required = True,
                    help="Universal forward primer ID")
parser.add_argument("--uniR", 
                    required = True,
                    help="Universal forward primer ID")
parser.add_argument("--barcodes", 
                    required = True,
                    help="Comma-separated list of barcode IDs")
parser.add_argument("--indexInfo",
                    required = True,
                    help="Tab-separated index sequence info file with 'name' and 'seq' columns")
args = parser.parse_args()

# Function for reverse complementation of reverse primers
def reverse_comp(DNAstring):
    # DNA library
    hComplement = {'A':'T', 'G':'C', 'C':'G', 'T':'A', 'N':'N'}
    revcomp = []
    try:
        for base in DNAstring:
            revcomp.append(hComplement[base])
        return("".join(revcomp)[::-1])
    except KeyError:
        sys.exit("Check primers, could not recognize character {0} in primer "
                 "sequence.".format(base))

# Read in the index info file as a dictionary
with open(args.indexInfo, 'r') as indexFile:
    indexDict = {}
    indexInfo = csv.DictReader(indexFile, delimiter='\t')
    for index in indexInfo:
        indexDict[index['name']] = index['seq']

# Define input + output files
inFile = args.input
newFile = '_indexed.'.join(inFile.split('.'))

# Define barcode sequences
uniFseq = indexDict[args.uniF]
uniRseq = reverse_comp(indexDict[args.uniR])
barcodeList = args.barcodes
barcodeList = barcodeList.split(',')
barcodeSeq = ''.join([indexDict[x] for x in barcodeList])

with open(newFile, 'w') as outFile:
    # Write header line 
    outFile.write('\t'.join(['chr', 'start',' stop', 'seq'])+'\n')
    # Read in the input BED file as a dictionary
    with open(inFile, 'r') as bedFile:
        bed = csv.DictReader(bedFile, delimiter='\t', fieldnames=['chr','start','stop','seq'])
        # For each probe, append index sequences accordingly
        for probe in bed:
            # Append uniF, barcodes to 5', RC of uniR to 3' of probe sequence
            newSeq = ''.join([uniFseq, barcodeSeq, probe['seq'], uniRseq])
            outFile.write('\t'.join([probe['chr'], probe['start'], probe['stop'], newSeq]) + '\n')