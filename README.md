# LLM Agent Security — A Provenance Boundary in Tool Agents under Indirect Prompt Injection

Course project (attack track). We study the AgentDojo tool-calling agent and ask a single question:
do indirect prompt-injection attacks still work on a current model, and if not, **why**? The answer is
a mechanism — current models bind instruction authority to the *structural source* of the text — which
we establish with a controlled diagnosis, show to be scale-dependent across 8 models, and connect to the
defenses that restore it.

All experiments run inside AgentDojo's sandbox on synthetic objects (e.g. a synthetic attacker IBAN).
No real accounts, money, or user data are involved. Models are reached through an OpenAI-compatible relay.

## Findings (the full chain)
1. **Published attacks are neutralized.** 5 attacks on banking+slack → **1 success / 1245** on GPT-6.1-terra
   (vs. high ASR reported on 2024 models). They still cut benign task completion by up to ~20 pts
   (disruption without breach). The lone success needed the *user* to authorize the external text.
2. **Our context-aware attack (FACA) also reaches 0%** on the strong model, while the payload is delivered
   (reached 27/30). A negative result we turn into the central question.
3. **Root-cause diagnosis.** Delivery is intact (90%); the action executes when the *user* asks (6/6); the
   identical text from an untrusted tool return never executes (0/90). A byte-identical **source test**
   (U/R/N) and a **provenance-vs-position** experiment isolate the decisive variable: the **structural
   source** of the instruction, not its content, framing, or dialogue position.
4. **Scale threshold.** Across 8 models, only Qwen3.6-flash is breakable; the other 7 sit at 0% with the
   payload delivered — a threshold, not a gradient. On that one breakable model our attack is the
   **strongest in the panel**: FACA v9 = **70%** ASR vs the strongest published baseline
   (`important_instructions`) at 53%, same 30 pairs, higher benign utility — because FACA forges
   account-owner provenance, the exact lever the diagnosis identified (`eval/round5_faca_vs_baselines.md`).
5. **Defenses re-supply the boundary.** On the vulnerable model, `spotlighting_with_delimiting` (mark tool
   output as untrusted data) drops ASR with utility preserved — the same boundary, supplied externally.

See `report/main.pdf` for the write-up and `eval/` for every table and figure's source data.

## Layout
- `agents/agentdojo/` — upstream AgentDojo source (reference; NOT our contribution; gitignored).
- `attack/faca.py` — **FACA, our attack** (variants V1–V7 + dispatch). See `attack/README.md`.
- `scripts/` — the harness and every experiment:
  - `run_bench.py` — run any relay model over a suite; Utility + ASR; `--attack-module`, `--defense`.
  - `summarize.py` — Utility / ASR + 95% Wilson CI + blocked/error columns.
  - `faca_controls.py`, `round4_source_boundary.py`, `analyze_round4.py` — diagnosis (controls, source test).
  - `expc_provenance_position.py`, `analyze_expc.py`, `fig_expc.py` — Experiment C (provenance vs position).
  - `slurm_scale.sh` / `slurm_defense.sh`, `make_figs.py`, `probe_models.py` — scaling, defenses, figures.
- `eval/` — result tables, taxonomy, diagnosis summaries, the success-case walkthrough.
- `report/` — `main.tex` / `main.pdf` (NeurIPS draft), `references.bib`, `figs/`, `REPORT_OUTLINE.md`.
- `slides/` — `faca_presentation.pptx` + generator `build_deck.js` (16 slides, 5 acts).
- `runs/` — raw per-episode JSON logs (gitignored). `.env` — relay key + base URL (gitignored).

## Reproduce
```bash
set -a; . ./.env; set +a          # relay OPENAI_API_KEY + OPENAI_BASE_URL

# 1. published-attack baseline
python scripts/run_bench.py --model gpt-6.1-terra --suite banking \
    -ut user_task_0 --attack important_instructions --logdir runs/demo
python scripts/summarize.py runs/demo/gpt-6.1-terra

# 2. FACA (variant via env; dispatch attack name is `faca`)
FACA_VARIANT=v7 python scripts/run_bench.py --model gpt-6.1-terra --suite banking \
    -ut user_task_12 -it injection_task_4 \
    --attack faca --attack-module attack/faca.py --logdir runs/faca

# 3. diagnosis (sandbox-only; execution verified by final state, excluded from ASR)
python scripts/faca_controls.py --injection injection_task_0 injection_task_4 injection_task_8
python scripts/round4_source_boundary.py --pairs 20 --repeat 2 && python scripts/analyze_round4.py
python scripts/expc_provenance_position.py --pairs 20 --repeat 2 && python scripts/analyze_expc.py
```
> Note: the strong-model experiments require a relay key whose group serves `gpt-6.1-terra`; the
> cross-model and defense runs use Qwen/GLM models. Batch runs are launched via SLURM (`scripts/slurm_*.sh`).

## Report / slides
```bash
cd report && pdflatex main && bibtex main && pdflatex main && pdflatex main   # -> main.pdf (6 pp, room to 9)
node slides/build_deck.js                                                     # -> slides/faca_presentation.pptx
```
Report prose is a draft: the team rewrites the narrative sections in its own voice (Turnitin) and fills
the author block / per-member contributions; tables, figures, captions and numbers are factual.
