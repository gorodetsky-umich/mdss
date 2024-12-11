#!/bin/bash
#SBATCH --job-name name_of_the_job
#SBATCH --nodes=8
#SBATCH --ntasks=288
#SBATCH --ntasks-per-node=36
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --mem-per-cpu=700m
#SBATCH --time=10:00:00
#SBATCH --account=account_name
#SBATCH --partition=standard
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=email_of_the_user
#SBATCH --output=mach_07/aoa05_result.txt

srun python python_file.py --inputFile yaml_file.yaml