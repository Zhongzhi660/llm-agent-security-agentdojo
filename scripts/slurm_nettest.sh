#!/bin/bash
#SBATCH --job-name=nettest
#SBATCH --partition=batch
#SBATCH --account=nl2lab
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=/home/zl22754/LLM-Agent-Security/runs/nettest_%j.out
set -a; source /home/zl22754/LLM-Agent-Security/.env; set +a
echo "node: $(hostname)"
echo "HTTP test to relay:"
curl -s -m 25 -o /dev/null -w "models endpoint HTTP %{http_code}\n" "$OPENAI_BASE_URL/models" -H "Authorization: Bearer $OPENAI_API_KEY"
