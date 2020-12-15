#!/bin/bash

# 1 node
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --job-name="hello-mpi"
#SBATCH -o hello-mpi.%J.out
#SBATCH -e hello-mpi.%J.err
#SBATCH -t 00:01:00
#SBATCH -p par7.q

source /etc/profile.d/modules.sh

module load intelmpi/gcc/2019.6
module load python/3.6.8

# You'll need to activate a virtual environment that contains mpi4py
# Before this works
mpirun python hello.py
