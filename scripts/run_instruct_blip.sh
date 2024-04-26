#!/bin/bash
#SBATCH --job-name="InstructBLIP (Lateral Thinking Visual Brainteasers)"
#SBATCH --time=72:00:00
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=defq
#SBATCH -C A6000
#SBATCH --gres=gpu:1

module load cuda11.7/toolkit

source $HOME/.bashrc
conda activate

python /var/scratch/hkd800/scripts/main.py instruct-blip
