#!/usr/bin/env bash
# Round 5 — FACA vs. the full AgentDojo baseline panel on the vulnerable model
# (Qwen3.6-flash), over the fixed 30-pair Round-2 case list. Each run_cases.sh
# fans out -P6 internally. Results -> runs/r5/<attack>/; analyze with the snippet
# in eval/round5_faca_vs_baselines.md (dedup by pair, drop attack_type=none and
# unparsed security=None episodes). See eval/round5_faca_vs_baselines.{md,csv}.
set -u
cd "$(dirname "$0")/.."
ROOT=runs/r5
mkdir -p "$ROOT"
echo "R5 START $(date)"

# Baseline panel — all unmodified AgentDojo attacks (load_attack).
for atk in direct ignore_previous system_message injecagent tool_knowledge important_instructions; do
  echo ">>> baseline $atk $(date +%H:%M:%S)"
  rm -rf "$ROOT/base_$atk"
  scripts/run_cases.sh qwen3.6-flash "$atk" "$ROOT/base_$atk"
done

# FACA variants — v7 (stealth ladder) + v8/v9/v10 (forge owner provenance).
# NOTE: payloads must avoid the YAML document separator '---' (use '===').
for v in v7 v8 v9 v10; do
  echo ">>> faca $v $(date +%H:%M:%S)"
  rm -rf "$ROOT/faca_$v"
  scripts/run_cases.sh qwen3.6-flash faca "$ROOT/faca_$v" "$v" --attack-module attack/faca.py
done

echo "R5 DONE $(date)"
touch "$ROOT/.R5_DONE"
