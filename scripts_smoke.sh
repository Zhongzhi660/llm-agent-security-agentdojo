#!/usr/bin/env bash
# Smoke test: 2 banking user tasks, no attack, then with built-in attack. Needs OPENAI_API_KEY in .env
set -a; source "$(dirname "$0")/.env"; set +a
cd "$(dirname "$0")"
.venv/bin/python -W ignore -m agentdojo.scripts.benchmark -s banking -ut user_task_0 -ut user_task_1 \
  --model GPT_4O_MINI_2024_07_18 --logdir runs/smoke
.venv/bin/python -W ignore -m agentdojo.scripts.benchmark -s banking -ut user_task_0 -ut user_task_1 \
  --model GPT_4O_MINI_2024_07_18 --attack important_instructions --logdir runs/smoke
