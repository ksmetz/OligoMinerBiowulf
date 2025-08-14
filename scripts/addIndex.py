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
                    help="Tab-separated config file with 'name', 'suffix', 'uniF', 'uniR', and 'barcodes' columns")
parser.add_argument("--indexInfo",
                    default="indexInfo.txt",
                    help="Tab-separated index info file with 'name' and 'seq' columns")
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

# Open config file
with open(args.input, 'r') as inputFile:
    # Read in as dictionary
    input = csv.DictReader(inputFile, delimiter='\t')
    for sample in input:
        # Find probe BED file input name, build BED file output name
        inFile = "output/" + sample['name'] + sample['suffix']
        newFile = "output/" + sample['name'] + '_indexed' + sample['suffix']
        # Begin writing an output file
        with open(newFile, 'w') as outFile:
            # Write header line from keys
            outFile.write('\t'.join(['chr', 'start',' stop', 'seq'])+'\n')
            # Read in the input BED file as a dictionary
            with open(inFile, 'r') as bedFile:
                bed = csv.DictReader(bedFile, delimiter='\t', fieldnames=['chr','start','stop','seq'])
                # For each probe, append index sequences accordingly
                for probe in bed:
                    # Look up and combine multiple barcodes
                    barcodeList = sample['barcodes'].split(',')
                    barcodes = ''.join([indexDict[x] for x in barcodeList])
                    # Append uniF, barcodes to 5', RC of uniR to 3' of probe sequence
                    newSeq = ''.join([indexDict[sample['uniF']], barcodes, probe['seq'], reverse_comp(indexDict[sample['uniR']])])
                    outFile.write('\t'.join([probe['chr'], probe['start'], probe['stop'], newSeq]) + '\n')