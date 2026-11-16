#!/bin/bash
#SBATCH --job-name=faca_scale
#SBATCH --partition=batch
#SBATCH --account=nl2lab
#SBATCH --time=06:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=4G
#SBATCH --output=/home/zl22754/LLM-Agent-Security/runs/slurm_scale_%j.out
set -euo pipefail
cd /home/zl22754/LLM-Agent-Security
echo "node: $(hostname)  start: $(date)"
for m in qwen3.7-max qwen3.8-max glm-5.2 qwen4-max-preview; do
  scripts/run_cases.sh "$m" important_instructions "runs/scale/${m}_impinstr"
  scripts/run_cases.sh "$m" faca "runs/scale/${m}_facav7" v7 --attack-module attack/faca.py
done
echo "SCALE_SBATCH_DONE $(date)"
