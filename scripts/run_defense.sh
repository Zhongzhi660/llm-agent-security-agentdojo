#!/usr/bin/env bash
# Run model+attack+defense over the fixed 30 banking pairs. Skips completed cases.
# Usage: scripts/run_defense.sh MODEL ATTACK DEFENSE LOGDIR [VARIANT] [--attack-module path]
set -u
MODEL=$1; ATTACK=$2; DEFENSE=$3; LOGDIR=$4; VARIANT=${5:-}; MA1=${6:-}; MA2=${7:-}
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
mkdir -p "$LOGDIR"
: > "$LOGDIR.stdout"
run_pair() {
  local ut=$1 it=$2
  FACA_VARIANT="$VARIANT" .venv/bin/python -I scripts/run_bench.py --model "$MODEL" --suite banking \
    -ut "$ut" -it "$it" --attack "$ATTACK" --defense "$DEFENSE" $MA1 $MA2 --logdir "$LOGDIR" >> "$LOGDIR.stdout" 2>&1
}
export -f run_pair; export MODEL ATTACK DEFENSE LOGDIR VARIANT MA1 MA2
tail -n +2 eval/faca_round2_cases.csv | while IFS=, read -r ut it; do echo "$ut $it"; done | \
  xargs -P 6 -I{} bash -c 'set -- {}; run_pair "$1" "$2"'
echo "DEF DONE $MODEL $ATTACK $DEFENSE $VARIANT"
