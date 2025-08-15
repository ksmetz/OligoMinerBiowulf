#! /bin/bash -login
#SBATCH -J OligoMiner
#SBATCH -t 2:00:00
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1  
#SBATCH -p norm
#SBATCH --mem=20gb
#SBATCH -o "%x-%j.out"

## Exit if any command fails
set -e

## Load modules
module load snakemake

## Source conda
source /data/$USER/conda/etc/profile.d/conda.sh

## Make directory for slurm logs
mkdir output
# mkdir -p output/logs_slurm

## Execute snakemake workflow
snakemake --use-conda --cores 1 -p -s workflows/oligoMiner 

## Success message
echo "Entire workflow completed successfully!"