#! /bin/bash -login
#SBATCH -J addIndex
#SBATCH -t 1:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1  
#SBATCH -p norm
#SBATCH --mem=2gb
#SBATCH -o "%x-%j.out"

## Exit if any command fails
set -e

## Source conda
source /data/$USER/conda/etc/profile.d/conda.sh
conda activate probeMining

## Execute snakemake workflow
python scripts/addIndex.py -i indexInput.txt