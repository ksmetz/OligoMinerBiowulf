# OligoMiner

[![DOI](https://zenodo.org/badge/DOI/10.1073/pnas.1714530115.svg)](http://dx.doi.org/10.1073/pnas.1714530115)

## Overview

This repository contains the code for the [OligoMiner](http://dx.doi.org/10.1073/pnas.1714530115) tool.

If you are looking to use probe sequences that we have already generated for various genome assemblies (hg19, hg38, mm9, mm10, dm3, dm6, ce6, ce11, danRer10, tair10), you can download those on our [website](http://genetics.med.harvard.edu/oligopaints). If you would like to run the OligoMiner tool yourself, please see below for instructions.

This tool was original created by the [Beliveau lab](https://github.com/beliveau-lab/OligoMiner/tree/master), then edited by Kathleen Reed in the Misteli lab for easy launching using snakemake on the Biowulf HPC. 

## Biowulf installation steps

The following steps only need to be done a single time, to make sure the pipeline will run smoothly.

1. Make sure you have [conda](https://docs.conda.io/en/latest/miniconda.html) installed, as per the [Biowulf instructions](https://hpc.nih.gov/docs/diy_installation/conda.html). 

	Generally this requires the following steps:
	
		$ sinteractive --mem=20g --gres=lscratch:20
		$ module load mamba_install
		$ mamba_install
		
	This should generate a directory in `/data/$USER/conda` by default.

2. Clone this repo on the cluster in the desired run location (generally in `/data/$USER`):

		$ git clone https://github.com/ksmetz/OligoMinerBiowulf
		$ cd OligoMinerBiowulf

3. In an interactive node, create the conda [environment](./environment.yml) from the `OligoMinerBiowulf` directory:
	
		$ sinteractive --mem=20g --gres=lscratch:20
		$ source /data/$USER/conda/etc/profile.d/conda.sh
		$ conda env create -f environment.yml

	This will install the following packages and their dependencies into the `probeMining` conda environment, saved locally to your user directory at `/data/$USER/conda/envs`:

	* [Python 2.7.15](https://www.python.org/downloads/release/python-2715/)
	* [Biopython](https://biopython.org/)
	* [scikit-learn](https://scikit-learn.org/stable/)
	* [Bowtie 2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)
	* [JELLYFISH](https://www.cbcb.umd.edu/software/jellyfish/)

	**Troubleshooting note:** if you encounter an error ending in the message `Note that strict channel priority may have removed packages required for satisfiability.`, you may need to run the following command before the `conda env create` command:
	
		$ conda config --set channel_priority flexible

	Note that NUPACK is no longer included in the `environment.yml` file as it has been removed from conda - see next step for installation.

4. For structure filtering step: Download and install NUPACK 3.0.6 manually.

	To download:
	* [Log in](https://nupack.org/auth/log-in) to [NUPACK](https://nupack.org/). 
	* If you do not have an account, make one using the following steps:
		* Click **subscribe** to create an account
		* Select the "Individual Non-commercial academic subscription" option. It should list a price but also state "temporarily free"
		* Fill out user info and follow instructions to make an account. Note that you should **NOT** be asked for payment info.
	* Navigate to the [Download](https://nupack.org/download/overview) page 
	* Select "Go to Standard License"
	* Accept the Software License Agreement
	* Download NUPACK 3.0.6 `.tar` file, and transfer it to your chosen software download location on Biowulf within `/data/$USER`

	To install:
	
		$ tar -xvf nupack3.0.6.tar
		$ cd nupack3.0.6
		$ make
	
	Edit your `~/.bash_profile` file to update your PATH and set the `NUPACKHOME` variables, i.e.:
		
		PATH=$PATH:/data/reedks/tools/nupack3.0.6/bin
		NUPACKHOME=/data/reedks/tools/nupack3.0.6
		export PATH
		export NUPACKHOME

5. For k-mer filtering step: Generate a Jellyfish dictionary for k-mer filtering. The can be done from anywhere on the cluster, but you should plan to save the resulting `.jf` file somewhere in `/data/$USER` as a reference file for future use.

	Note that the genome FASTA file (`/fdb/genomebrowser/fasta/hg38/hg38.fa`) will differ based on organism. Adjust k-mer length (`-m 18`) and output file name (`-o hg38_18.jf`) accordingly for your needs.

	This command takes many minutes for large genomes. Consider launching it as a SLURM job instead of in an interactive node. This can also be run locally but may take several hours. The resulting output file is ~1.5GB for hg38 18-mers. 
	
	Katie has a copy of one for hg38 18-mers that she can also share directly upon request to avoid having to remake this.

		$ sinteractive --mem=20g --gres=lscratch:20
		$ source /data/$USER/conda/etc/profile.d/conda.sh
		$ conda activate probeMining
		$ jellyfish count -s 3300M -m 18 -o hg38_18.jf --out-counter-len 1 -L 2 /fdb/genomebrowser/fasta/hg38/hg38.fa

## Running pipeline on Biowulf

1. Clone this repo on the cluster in the desired run location (generally in `/data/$USER`):
	
		$ git clone https://github.com/ksmetz/OligoMinerBiowulf
		$ cd OligoMinerBiowulf

2. Edit the config file for your run:

	**Input file**
	* `input`: in quotations, path to the input `.bed` file. See `'exampleInput.bed'` for an example input file. See Step 3 below for file details.

	**Pipeline run options**
	* `alignmentMode`: either `'unique'` or `'LDA`', depending on which mode you wish to use. Adjusts the bowtie alignment and outputClean.py parameters accordingly
	* `probeLengthMin`, `probeLengthMax`: probe length parameters for blockParse.py step
	* `kmerFilter`, `structureFilter`, and `addIndex`: Either `True` or `False` depending on if you want to use this step.
	* `kmerLength`: If using k-mer filter step, length of k-mer. This must match the setting used to generate the jellyfish index above. 
	* `kmerCount`, `structureThresh`: parameters for filtering steps

	**Genome-specific reference files**
	* `genomeFASTA`: path to the FASTA sequence file for your assembly of interest. Many of these are already saved on Biowulf at `/fdb/genomebrowser/fasta`
	* `bowtieIndex`: path to the bowtie2 index files for your assembly of interest. Many of these are already saved on Biowulf at `/fdb/igenomes/<organism>/<source>/<assembly>/Sequence/Bowtie2Index/genome`
	* `jellyfishIndex`: path to the `.jf` file (see [installation](#biowulf-installation-steps) step 5)

	**Index sequence information**
	* `indexSeqs`: A tab-delimited file containing `name` and `seq` columns for indexes to be appeneded to the probe when `addIndex` is set to `True`. By default we include `indexSequences.txt`, a list of barcodes from Allistair Boettiger with limited “off targets” for mouse, human, or Drosophila, as used by Leah Rosin's lab.

3. Generate a tab-delimited input `.bed` file.

	The following columns are required:
	* `chr`, `start`, `stop`: coordinates for regions where probes should be generated
	* `name`: the name of the region, and the output `probes.bed` file

	The following columns are required if appending indexes (i.e. `addIndex: True` in `config.yaml`):
	* `uniF`: the name of the primer used as the universal forward primer. Appended to the 5' end of the probe
	* `uniR`: the name of the primer used as the universal reverse primer. Reverse complement appended to the 3' end of the probe
	* `barcodes`: the name of the primer(s) used as sample barcodes. Appended to the 5' end of the probe after the universal forward primer.
	* Note: All primer names should correspond to entries in the `indexSeqs` information file (`indexSequences.txt` by default).
	
	See the `exampleInput.bed` file as an example.

4. Launch pipeline as a SLURM job with `sbatch ./runOligoMiner.sbatch`

	Pipeline progress will be recorded in `OligoMiner-%j.out`, and output files will be generated in `output`.
	
	Note that you can skip straight to this step after step 1 to test the pipeline; it should run in less than 5 minutes.

### Note about operating systems

OligoMiner is a set of command-line scripts developed on Python 2.7 that can easily be executed from a [Bash Shell](https://en.wikipedia.org/wiki/Bash_(Unix_shell)). If you are using standard Linux or Mac OS X sytsems, we expect these instructions to work for you.

If you are using Windows 10, we recommend enabling [Ubuntu on Windows 10](https://ubuntu.com/tutorials/ubuntu-on-windows), a full Linux distribution, and then running OligoMiner in the Ubuntu terminal.

### Notes on running OligoMiner on new genomes

You'll need to download your genome of interest in FASTA format and prepare index/dictionary files for your NGS aligner and optionally Jellyfish. We recommend using unmasked files for dictionary file construction and repeat-masked files as the input files for `blockParse.py`

## Citation

Please cite according to the enclosed [citation.bib](./citation.bib):

```
@article{Beliveau2018,
        doi = {10.1073/pnas.1714530115},
        url = {https://doi.org/10.1073%2Fpnas.1714530115},
        year = 2018,
        month = {feb},
        publisher = {Proceedings of the National Academy of Sciences},
        volume = {115},
        number = {10},
        pages = {E2183--E2192},
        author = {Brian J. Beliveau and Jocelyn Y. Kishi and Guy Nir and Hiroshi M. Sasaki and Sinem K. Saka and Son C. Nguyen and Chao-ting Wu and Peng Yin},
        title = {{OligoMiner} provides a rapid, flexible environment for the design of genome-scale oligonucleotide in situ hybridization probes},
        journal = {Proceedings of the National Academy of Sciences}
}
```

## Questions

Please reach out to [Brian](mailto:beliveau@uw.edu) with any questions about installing and running the scripts, or [open an issue](../../issues/new) on GitHub.

For questions on running the SnakeMake version of the pipeline on Biowulf, reach out to [Katie](mailto:kathleen.reed2@nih.gov).

## License

We provide this open source software without any warranty under the [MIT license](https://opensource.org/licenses/MIT).

## Contributing

We welcome commits from researchers who wish to improve our software. Please follow the [git flow](http://nvie.com/posts/a-successful-git-branching-model/) branching model. Make all changes to a topic branch off the branch `dev`. Merge the topic branch into `dev` first (preferably using `--no-ff`) and ensure everything works. Code will _only_ merged into `master` for release builds. Hotfixes should be developed and tested in a separate branch off `master`, and a new release should be generated immediately after the hotfix is merged.
