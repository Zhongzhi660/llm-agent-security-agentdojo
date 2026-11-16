#!/bin/bash
#SBATCH --job-name=faca_def
#SBATCH --partition=batch
#SBATCH --account=nl2lab
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=4G
#SBATCH --output=/home/zl22754/LLM-Agent-Security/runs/slurm_def_%j.out
set -u
cd /home/zl22754/LLM-Agent-Security
echo "node: $(hostname)  start: $(date)"
M=qwen3.6-flash
for DEF in tool_filter spotlighting_with_delimiting repeat_user_prompt; do
  scripts/run_defense.sh "$M" important_instructions "$DEF" "runs/defense/${M}_impinstr_${DEF}"
  scripts/run_defense.sh "$M" faca "$DEF" "runs/defense/${M}_facav7_${DEF}" v7 --attack-module attack/faca.py
done
echo "DEFENSE_SBATCH_DONE $(date)"
