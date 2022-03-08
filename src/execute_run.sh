#!/bin/bash
#SBATCH --job-name="modifications classifier"
#SBATCH --output="modsClassifierLog-out.%j.%N.out"
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --mem=250gb
#SBATCH --account=fsaeed
#SBATCH --no-requeue
#SBATCH -t 10:00:00

python sbatch_run_train.py
