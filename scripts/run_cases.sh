#!/usr/bin/env bash
# Run a model+attack over the fixed Round-2 case list (eval/faca_round2_cases.csv), paired by pair.
# Usage: scripts/run_cases.sh MODEL ATTACK LOGDIR [FACA_VARIANT] [--attack-module path]
set -u
MODEL=$1; ATTACK=$2; LOGDIR=$3; VARIANT=${4:-}; MODARG=${5:-}; MODVAL=${6:-}
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
CASES=eval/faca_round2_cases.csv
run_pair() {
  local ut=$1 it=$2
  FACA_VARIANT="$VARIANT" .venv/bin/python -I scripts/run_bench.py --model "$MODEL" --suite banking \
    -ut "$ut" -it "$it" --attack "$ATTACK" $MODARG $MODVAL --logdir "$LOGDIR" >> "$LOGDIR.stdout" 2>&1
}
export -f run_pair; export MODEL ATTACK LOGDIR VARIANT MODARG MODVAL
mkdir -p "$LOGDIR" "$(dirname "$LOGDIR")"
: > "$LOGDIR.stdout"
tail -n +2 "$CASES" | while IFS=, read -r ut it; do echo "$ut $it"; done | \
  xargs -P 6 -I{} bash -c 'set -- {}; run_pair "$1" "$2"'
echo "CASES DONE $MODEL $ATTACK $VARIANT"
