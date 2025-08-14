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
# snakemake -j 100 --use-conda --max-jobs-per-second 5 --max-status-checks-per-second 5 --rerun-incomplete --restart-times 3 -p -s workflows/oligoMiner --latency-wait 500 --cluster-config "config/cluster.yaml" --cluster "sbatch -J {cluster.name} -p {cluster.partition} -t {cluster.time} -c {cluster.cpusPerTask} --mem-per-cpu={cluster.memPerCpu} -N {cluster.nodes} --output {cluster.output} --error {cluster.error} --parsable"
snakemake --use-conda --cores 1 -p -s workflows/oligoMiner 

## Success message
echo "Entire workflow completed successfully!"