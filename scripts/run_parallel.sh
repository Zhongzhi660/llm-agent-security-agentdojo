#!/usr/bin/env bash
# Run AgentDojo over all user tasks of a suite in parallel (one process per user task).
# Usage: scripts/run_parallel.sh MODEL SUITE ATTACK|none N_USER_TASKS PARALLEL LOGDIR [extra run_bench args...]
set -u
export MODEL=$1 SUITE=$2 ATTACK=$3 LOGDIR=$6; NUT=$4; PAR=$5; shift 6
export EXTRA="$*"
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
mkdir -p "$LOGDIR/stdout"
one() {
  local ut=user_task_$1 atk=()
  [ "$ATTACK" != none ] && atk=(--attack "$ATTACK")
  .venv/bin/python -I scripts/run_bench.py --model "$MODEL" --suite "$SUITE" -ut "$ut" --logdir "$LOGDIR" \
    "${atk[@]}" $EXTRA > "$LOGDIR/stdout/${SUITE}_${ATTACK}_${ut}.log" 2>&1 \
  || { sleep 5; .venv/bin/python -I scripts/run_bench.py --model "$MODEL" --suite "$SUITE" -ut "$ut" --logdir "$LOGDIR" "${atk[@]}" $EXTRA >> "$LOGDIR/stdout/${SUITE}_${ATTACK}_${ut}.log" 2>&1; }
  echo "done $SUITE $ATTACK $ut rc=$?"
}
export -f one
seq 0 $((NUT-1)) | xargs -P "$PAR" -I{} bash -c 'one {}'
echo "ALL DONE $SUITE $ATTACK"
