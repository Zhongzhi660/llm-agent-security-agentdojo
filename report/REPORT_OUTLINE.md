# Final Report Framework — Why Indirect Prompt Injection Fails on Current Tool Agents, and What That Tells Us About the Boundary They Hold

NeurIPS template, **9 content pages max** (references + appendix excluded). Prose is written by the
team (Turnitin AI check: keep AI-generated text < 60% — this file gives structure, bullets, tables and
figure refs, **not** finished paragraphs). Page budget in each heading sums to ~9.0.

> **One-line thesis.** On current models, published single-shot injections *and* our own context-aware
> attack (FACA) both reach ~0% ASR; through a controlled diagnosis we show this is not a scoring artifact
> but a real **user-authorization / provenance boundary** the model enforces by the *structural source* of
> an instruction — then we locate the model scale at which that boundary appears and the defenses that
> re-supply it to models that lack it.

---

## Abstract (~180 words)
- Study object: the AgentDojo tool-calling agent (banking/slack/travel/workspace), a current model via relay.
- We reproduce 5 published indirect prompt-injection attacks **and** design a context-aware attack (FACA);
  both reach ~0% ASR on the strong model (1/1245 published; 0/N FACA).
- Rather than stop at a negative result, we run a **controlled root-cause diagnosis**: delivery is intact
  (90%), the action is executable when the *user* asks (6/6), yet identical text asserted by an untrusted
  tool return never executes (0/90). A byte-identical-action source test (U/R/N) and a provenance-vs-position
  test (Experiment C) isolate the decisive variable: the **structural source** of the instruction, not its
  content, framing, or dialogue position.
- We then show the finding is **scale-dependent** (8 models: only one small model is breakable — a threshold,
  not a gradient) and that effective **defenses** work by re-supplying the same data/instruction boundary.
- Contribution: a reproducible harness + a mechanism-level account of *why* current agents resist injection.

## 1. Introduction & Contributions (0.75 p)
- LLM agent = LLM + tools + loop; indirect prompt injection = attacker text in a tool-returned (data-plane)
  field trying to seize the control plane.
- Tension to motivate the paper: 2024-era attacks reported high ASR; do they still work, and if not, *why*?
- **Contributions** (state as a numbered list):
  1. A reproducible evaluation harness over AgentDojo driving a current relayed model, with CIs + repeat-run noise.
  2. FACA, a team-designed context-aware injection (context/dependency/authorization framings, V1–V7).
  3. A controlled, falsifiable **root-cause diagnosis** (H0–H4; controls A/B/C; source test U/R/N;
     provenance-vs-position Experiment C) showing the model holds a **source-based authorization boundary**.
  4. A **cross-model threshold** result (8 models) and a **defense trade-off** analysis closing the loop.

## 2. The Agent Under Study (1.0 p)  — maps to the presentation's "review of agents"
- **Task**: carry out a user instruction by calling domain tools (read transactions, send money, post messages…).
- **I/O**: user prompt + tool schemas → sequence of tool calls → final text answer.
- **Pipeline** (cite `agents/agentdojo/src/agentdojo/agent_pipeline/`):
  `SystemMessage → InitQuery → LLM (OpenAILLM, chat.completions + function calling) →
  ToolsExecutionLoop(ToolsExecutor + LLM)`, optional defense element. Injection enters as an
  attacker-controlled substring **inside a tool output**, i.e. the data plane.
- **Benign performance** (Table 1, `report/figs/utility_disruption.png` blue bars): 56–95% completion across
  suites; 3-run spread 5–6 pts (temperature noise, reported as the measurement floor).

## 3. Threat Model (0.6 p)
- **Category**: indirect prompt injection = data-plane → control-plane confusion. One-paragraph review
  (AgentDojo, InjecAgent, the `important_instructions` template family).
- **Attacker**: third party controlling exactly one external data field the agent will read (email body,
  file, web page, transaction memo). No access to system prompt, weights, or the user turn.
- **Victim/objective**: the delegating user; attacker wants a sensitive tool call (move money to attacker
  IBAN `US133000000121212121212`, exfiltrate data) ideally while the benign task still completes (stealth).
- **Assumptions**: static attack (not adaptive within an episode); all actions occur inside AgentDojo's
  sandbox on synthetic objects — **no real accounts, money, or user data**.

## 4. Evaluation Setup (0.6 p)
- Dataset: AgentDojo v1.2.1 — 97 user tasks; banking 16/slack 21/travel 20/workspace 40 user tasks,
  9/5/7/14 injection tasks. Main study + all diagnostics on **banking**; cross-model + defense on banking.
- Model: **GPT-6.1-terra** via an OpenAI-compatible relay (chat.completions + function calling). Relay-side
  content filter (OpenAI `cyber_policy`) can refuse a request; such refusals are logged separately
  (`FilterAwareOpenAILLM` → `[BLOCKED_BY_PROVIDER_FILTER]`; 0 in final data).
- Metrics: benign **Utility**; **Utility-under-attack** (stealth/availability proxy); **ASR** (AgentDojo
  security check, attacker IBAN in a real call's args). 95% **Wilson** CIs throughout. Diagnostic
  "execution" quantities are verified by final sandbox state and kept **separate from ASR**.

## 5. Published Attacks Are Neutralized (1.0 p)
- **Table 2 / `report/figs/asr_by_attack.png`**: ASR ≈ 0 for all 5 (ignore_previous, important_instructions,
  injecagent, system_message, tool_knowledge) → **1 / 1245** total; CI upper bound ≤ 3.8%.
- **`report/figs/utility_disruption.png`**: attacks don't breach the agent but **disrupt benign completion**
  (e.g. slack 95%→72% under important_instructions); injecagent nearly harmless (≈94%). Frame as an
  availability effect, not success.
- **Failure-stage taxonomy (Table 3, `eval/p2_stage_analysis.txt`)**: of defeated cases ~5–12% named/refused
  the injection; ~15–35% paused to ask the user (safe-by-caution); ~43–68% silently finished the benign task.
  Heuristic labels, manually validated ~80% precision on "refused" (`eval/p2_validation_notes.md`).
- **The one success (`eval/success_case_walkthrough.txt`)**: banking user_task_12 × injection_task_4 — the
  *user prompt itself* said "follow the instructions precisely," collapsing the data/instruction boundary.
  → Robustness leans on the user NOT authorizing external content. This motivates FACA.

## 6. FACA: A Context-Aware Attack [TEAM-DESIGNED] (1.0 p)
- Hypothesis: the single success collapsed the boundary via *authorization*; FACA tries to manufacture that
  authorization from within the injected content — framing the malicious step as **context-consistent**,
  a **dependency/pending workflow step**, or a **record-claimed approval** (variants V1–V7, `attack/faca.py`,
  `attack/README.md`). Engineering note: payloads avoid `---`/`"` (break AgentDojo YAML serialization) → `===`.
- Motivation per family + why each *should* work given the Sec 5 failure modes (team writes).
- **Result (Table 4, `eval/faca_round2_summary.md`)**: on 30 banking train pairs, **ASR 0/30 for every
  variant**, while the injected payload still reaches the tool output (**S1 ≈ 27/30**). FACA does not beat
  the baselines on the strong model. → A negative result that we turn into the paper's core question.

## 7. Root-Cause Diagnosis: What Boundary Is Being Enforced? (2.0 p) — **the core contribution**
- **7.1 Five hypotheses (`eval/faca_round3_diagnosis.md`).** H0 delivery/scoring bug · H1 target not
  executable · H2 external content treated as data · H3 insufficient framing · H4 disruption-not-advancement.
- **7.2 Evaluation-chain audit.** Over 90 variant-episodes: payload content delivered **81/90 = 90%** (after
  YAML normalization); target tool present **90/90**; attacker token ever placed in call args **0/90**.
  → **H0 ruled out.**
- **7.3 Authorization controls (Table 5, `eval/faca_round3_controls.csv`).**
  A comprehension (user asks to read it back) = **6/6** quotes it; B legitimate (user requests the action
  directly) = **6/6** executes, security=True; C untrusted claim (FACA) = **0/90**. → **H1 ruled out; H2
  supported.** Decision rule A-yes/B-yes/C-no ⇒ the authorization boundary is effective; *stop stacking
  templates, do not blind-search.*
- **7.4 Source test, byte-identical action (Table 6, `eval/round4_source_boundary_summary.md`,
  `report/figs/…`).** Same action text T (harmless synthetic `city`=sentinel via `update_user_info`), vary
  only source: **U (user) 20/20 · R (injected tool return) 0/20 · N (descriptive) 0/20**; R executed|reached
  = 0/40. Execution verified by final sandbox state, separate from ASR.
- **7.5 Provenance vs position — Experiment C (Table 7, `eval/expc_provenance_summary.md`,
  `report/figs/expc_provenance.png`).** Resolves the Round-4 confound (source was entangled with early-vs-late
  dialogue position). Add a user-sourced instruction at a **late** position (2nd user turn after a tool read):
  **U1 user/early 20/20 · U2 user/LATE 20/20 · Rext external/late 0/20 · Ruser claims-user/late 0/20**
  (Rext/Ruser reached 20/20). U2 vs Rext share position, differ only in source ⇒ **source decides, not
  position**; Ruser=0 ⇒ the boundary tracks the **structural turn-role**, not a semantic authorship claim.
- **7.6 Statement of the finding.** The decisive variable is the *structural source/provenance* of an
  instruction; the strong model enforces a user-authorization boundary that framing, relevance, and dialogue
  position do not move.

## 8. The Boundary Is Scale-Dependent (0.75 p)
- **8-model sweep (Table 8, `eval/scaling_curve_summary.md`, `report/figs/scaling_curve.png`)**: on the same
  30 pairs, **only qwen3.6-flash is breakable** (important_instructions 40%, FACA-V7 10%); qwen3.8-flash,
  qwen3.7-plus/max, qwen3.8-max, glm-5.2, qwen4-max-preview, gpt-6.1-terra all **0%**. A **threshold, not a
  gradient**. Genuineness verified (injection reached 27–30/30, high utility, 0 errors; weak model actually
  sends money to the attacker IBAN — `eval/weak_vs_strong_comparison.md`). deepseek-v4.1-flash excluded
  (unparseable outputs).

## 9. Defenses Re-Supply the Boundary (0.75 p)
- **Table 9 / `report/figs/defense_tradeoff.png`** (qwen3.6-flash, the breakable model):
  important_instructions 40%→ tool_filter **0%** (utility 80→40), spotlighting **13%** (utility 80), repeat
  21% (79); FACA-V7 10%→ tool_filter 0% (40), spotlighting 7% (83), repeat 7% (80).
- Reading: **spotlighting_with_delimiting** is the practical winner (large ASR drop, utility preserved);
  tool_filter hits 0 but halves utility. Effective defenses externally re-supply the data-vs-instruction
  boundary the strong models already hold internally — **closing the loop with Sec 7**.

## 10. Discussion & Limitations (0.5 p)
- Robustness is a *mechanism* (source-based provenance trust), not luck or a single refusal heuristic.
- Disruption-without-breach remains a mild availability risk.
- **Limitations**: single model family for the main study; one suite (banking) for diagnostics; one synthetic
  field; static (non-adaptive) attacker; relay content filter as a confound; heuristic taxonomy labels;
  cross-model sweep at N=30 (wide CIs). Generality to slack/travel/workspace is untested (future work).

## 11. Conclusion (0.25 p)
- Current agents resist both published and context-aware single-shot injection because they bind instruction
  authority to the *structural source*; this boundary emerges at a model-capability threshold and can be
  approximated in weaker models by spotlighting-style defenses. Open question: adaptive / multi-turn attacks
  that manufacture genuine user-turn provenance.

## Appendix (unlimited, excluded from 9 pages)
- Per-injection-task ASR tables; full FACA prompts + template versions; integrity tests
  (`tests/test_round4_controls.py`); Experiment C two-turn driver; all reproduction commands; model catalog
  and relay notes.

## Contributions list (REQUIRED — only the team can fill)
- [member A]: … / [member B]: … / [member C]: …

---
### Result-artifact map (every table/figure → file)
| Report element | File |
|---|---|
| Table 1 benign utility | `report/figs/utility_disruption.png` (blue), `eval/baseline_all_gpt-6.1-terra.txt` |
| Table 2 / Fig ASR of 5 attacks | `eval/all_attacks_gpt-6.1-terra.txt`, `report/figs/asr_by_attack.png` |
| Table 3 failure-stage taxonomy | `eval/p2_stage_analysis.txt`, `eval/p2_validation_notes.md` |
| Sec 5 success case | `eval/success_case_walkthrough.txt` |
| Table 4 FACA | `eval/faca_round2_summary.md`, `eval/faca_round2_results.csv` |
| Sec 7.1–7.3 diagnosis + controls | `eval/faca_round3_diagnosis.md`, `eval/faca_round3_controls.csv` |
| Table 6 source test (U/R/N) | `eval/round4_source_boundary_summary.md`, `eval/round4_source_boundary_pairs.csv` |
| Table 7 / Fig Experiment C | `eval/expc_provenance_summary.md`, `report/figs/expc_provenance.png` |
| Table 8 / Fig scaling | `eval/scaling_curve_summary.md`, `report/figs/scaling_curve.png` |
| Table 9 / Fig defenses | `eval/defense_summary.md`, `eval/defense_results.csv`, `report/figs/defense_tradeoff.png` |
| Weak-vs-strong detail | `eval/weak_vs_strong_comparison.md` |
