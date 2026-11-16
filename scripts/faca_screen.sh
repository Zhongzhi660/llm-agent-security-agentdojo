#!/usr/bin/env bash
# Round-1 FACA screening: each variant over a fixed (user_tasks x injection_tasks) set, in parallel.
# Usage: scripts/faca_screen.sh SUITE LOGDIR "ut_list" "it_list" variant1 variant2 ...
set -u
SUITE=$1; LOGDIR=$2; UTS=$3; ITS=$4; shift 4
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
mkdir -p "$LOGDIR/stdout"
ut_args=""; for u in $UTS; do ut_args="$ut_args -ut user_task_$u"; done
it_args=""; for i in $ITS; do it_args="$it_args -it injection_task_$i"; done
run_one() {
  local v=$1
  .venv/bin/python -I scripts/run_bench.py --model gpt-6.1-terra --suite "$SUITE" \
    $ut_args $it_args --attack "$v" --attack-module attack/faca.py --logdir "$LOGDIR" \
    > "$LOGDIR/stdout/${SUITE}_${v}.log" 2>&1
  echo "done $v rc=$?"
}
export -f run_one; export ut_args it_args SUITE LOGDIR
printf '%s\n' "$@" | xargs -P 5 -I{} bash -c 'run_one {}'
echo "SCREEN DONE"
