#!/bin/bash
#SBATCH --job-name="range_finder"
#SBATCH --output="RangeFinderLog-out.%j.%N.out"
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --mem=250gb
#SBATCH --account=fsaeed
#SBATCH --no-requeue
#SBATCH -t 10:00:00

python3 range_finder_moz.py
