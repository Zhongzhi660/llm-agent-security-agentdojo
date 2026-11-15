# LLM Agent Security — Indirect Prompt Injection on AgentDojo

Course project. Studies the AgentDojo tool-calling agent and the robustness of published indirect
prompt-injection attacks on a current model (GPT-6.1-terra via an OpenAI-compatible relay).

## Layout
- `agents/agentdojo/` — upstream AgentDojo source (reference; NOT our contribution).
- `scripts/` — our harness:
  - `run_bench.py`   run any relay model over a suite; computes Utility + ASR; `--attack-module` loads custom attacks.
  - `run_parallel.sh`  one process per user task, with one auto-retry.
  - `summarize.py`   Utility / ASR + 95% Wilson CI + blocked/error columns.
  - `failure_analysis.py`, `make_figs.py`, `sample_for_validation.py`, `probe_models.py`.
- `attack/` — slot for the team's attack (see attack/README.md). THIS is the graded contribution.
- `eval/` — result tables + taxonomy + validation + the success-case walkthrough.
- `report/`, `slides/` — outlines + figures.
- `runs/` — raw per-episode JSON logs (baseline + 2 repeats). gitignored.
- `.env` — OPENAI_API_KEY + OPENAI_BASE_URL (gitignored).

## Reproduce
```
set -a; . ./.env; set +a
python scripts/run_bench.py --model gpt-6.1-terra --suite banking \
    -ut user_task_0 --attack important_instructions --logdir runs/demo
python scripts/summarize.py runs/demo/gpt-6.1-terra
```

## Key finding so far
5 published attacks → ASR 1/1245 (~0%) on GPT-6.1-terra, vs. high ASR reported on 2024 models.
Attacks still cut benign task completion by up to ~20 pts (disruption without breach). The lone success
required the *user* to authorize external content as instructions.
