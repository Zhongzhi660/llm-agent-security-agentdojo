#!/usr/bin/env bash
# Round-2 paired comparison: control, v5, v6, v7 over the SAME case list (eval/faca_round2_cases.csv).
# One --logdir per variant. Deterministic payloads. Usage: scripts/run_faca_round2.sh [SUITE]
set -u
SUITE=${1:-banking}
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
CASES=eval/faca_round2_cases.csv
run_pair() {  # $1=variant $2=ut $3=it
  FACA_VARIANT="$1" .venv/bin/python -I scripts/run_bench.py --model gpt-6.1-terra --suite "$SUITE" \
    -ut "$2" -it "$3" --attack faca --attack-module attack/faca.py \
    --logdir "runs/faca_round2_$1" >> "runs/faca_round2_$1.stdout" 2>&1
}
export -f run_pair; export SUITE
for v in control v5 v6 v7; do
  : > "runs/faca_round2_$v.stdout"
  tail -n +2 "$CASES" | while IFS=, read -r ut it; do echo "$v $ut $it"; done
done | xargs -P 8 -I{} bash -c 'set -- {}; run_pair "$1" "$2" "$3"'
echo "ROUND2 DONE"
