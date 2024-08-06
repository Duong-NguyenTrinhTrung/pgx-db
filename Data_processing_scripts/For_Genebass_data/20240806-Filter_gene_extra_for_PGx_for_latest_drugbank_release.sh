#!/bin/bash

#SBATCH --nodes=1
#SBATCH --partition=standard
#SBATCH --qos=normal
module load jdk/1.8.0_291  
python   20240806-Filter_gene_extra_for_PGx_for_latest_drugbank_release.py
