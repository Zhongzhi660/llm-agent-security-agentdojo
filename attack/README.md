# FACA — the team's attack (implemented)

FACA (Failure-feedback Adaptive Context Attack) is our graded contribution, implemented in
`attack/faca.py`. It abandons loud override templates and instead frames the malicious step as content
the user's own task would naturally contain. The engineering around it (running, scoring, CIs, defenses)
is handled by `scripts/run_bench.py` and `scripts/summarize.py`; FACA only crafts the injection payload.

## How AgentDojo attacks work
An attack subclasses `agentdojo.attacks.base_attacks.BaseAttack` and implements
`attack(user_task, injection_task) -> dict[str, str]`, mapping each injection placeholder id to the string
substituted into the tool output. The ground-truth malicious tool calls come from `injection_task`; the
attack only crafts the text that makes the agent emit them. `build_payload(user_prompt, goal, variant)` in
`faca.py` is where the payload text is built.

Engineering note: AgentDojo re-serializes the environment to YAML, so payloads **avoid** `---` and double
quotes (which break serialization) — we use `===` and unquoted text, and verify delivery at the *content*
level, not byte level. `TEMPLATE_VERSION = "faca-r2-v1"`.

## Registered variants
Single-factor variants, so any effect is attributable to one mechanism:

| name | factor added |
|---|---|
| `faca_context` / `faca_v5` | task-aligned: the action appears as a "related follow-up" in a record about the user's task |
| `faca_dependency` / `faca_v6` | + a "reconciliation pending" workflow step the task seems to depend on |
| `faca_authorization` / `faca_v7` | + the record claims it was "approved" |
| `faca_combined` | all factors together |
| `faca_placebo` / `faca_control` | benign same-format record (rules out keyword/length effects) |
| `faca` | dispatch attack; variant chosen by the `FACA_VARIANT` env var (default `v5`) |

Run it (no framework edits):
```bash
FACA_VARIANT=v7 python scripts/run_bench.py --model gpt-6.1-terra --suite banking \
    -ut user_task_12 -it injection_task_4 \
    --attack faca --attack-module attack/faca.py --logdir runs/faca
```

## Result and what it led to
On GPT-6.1-terra (30 banking pairs) every variant reaches **0% ASR** while the payload is delivered
(reached 27/30). FACA does not beat the baselines on the strong model — so we stopped adding templates and
diagnosed *why* (see `eval/faca_round3_diagnosis.md`, `eval/round4_source_boundary_summary.md`,
`eval/expc_provenance_summary.md`). The controlled finding: the model enforces a **user-authorization /
provenance boundary** keyed to the structural source of an instruction. FACA breaks the one model that
lacks it (Qwen3.6-flash: 10% with V7, 40% with `important_instructions`).

## Design dimensions (for the report)
1. **Injection point** — which tool field is attacker-controlled, and how trusted it looks in context.
2. **Instruction/data framing** — how the text is positioned relative to the surrounding document (the V5→V7 ladder).
3. **Stealth** — keep benign Utility high (we measure Utility-under-attack and keep a placebo control).
4. **Robustness of the trigger** — does it survive across user tasks / suites, not just one case.

Evaluate every variant with the same harness and report ASR + 95% CI next to the 5 baselines + the ablation.
