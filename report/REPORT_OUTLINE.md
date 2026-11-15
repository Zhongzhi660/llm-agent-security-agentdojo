# Final Report Outline — Indirect Prompt Injection against AgentDojo Tool Agents

NeurIPS template, 9 content pages max (refs + appendix excluded). Prose to be written by the team
(Turnitin AI check: keep AI-generated text < 60%). This file is a scaffold + where each result lives.

## Abstract (~150 words)
- One LLM agent studied: the AgentDojo tool-calling agent (banking/slack/travel/workspace).
- We replicate 5 published indirect prompt-injection attacks and measure them on a current model (GPT-6.1-terra).
- Headline finding: published attacks that scored high ASR on 2024 models now achieve ~0% ASR (1/1245),
  but still degrade benign task completion by up to ~20 pts. We analyze *why* and discuss implications.

## 1. Introduction & Roadmap (0.75 p)
- LLM agents = LLM + tools + loop; indirect prompt injection via tool-returned (untrusted) content.
- Contributions: (i) reproducible evaluation harness over AgentDojo with a relayed current model;
  (ii) multi-attack robustness measurement with CIs and repeat-run noise; (iii) failure-stage taxonomy;
  (iv) [attack design by team — to be added].

## 2. The Agent Under Study (1.5 p)  — maps to presentation "review of agents"
- **Task**: execute a user instruction by calling domain tools (read files, send money, post messages...).
- **Input/Output**: user prompt + tool schemas  →  sequence of tool calls + final text answer.
- **Structure / modules** (cite src/agentdojo/agent_pipeline/):
  SystemMessage → InitQuery → LLM (OpenAILLM, chat.completions + function calling) →
  ToolsExecutionLoop(ToolsExecutor + LLM), optional defense element.
- **Inference pipeline**: system msg set → user query → LLM emits tool_calls → executor runs them in a
  sandboxed stateful environment → tool outputs appended → loop until no tool call → final answer.
  Injection enters as attacker-controlled substring inside a tool output.
- **Benign performance** (Table 1): 56–95% task completion across suites, 3-run spread 5–6 pts.
  [report/figs/utility_disruption.png blue bars; eval/all_attacks_* ]

## 3. Threat Model (0.75 p)
- **Attack category**: indirect prompt injection (data-plane → control-plane confusion). Brief review of the
  category and prior work (AgentDojo, InjecAgent, important_instructions template).
- **Attacker**: third party controlling a piece of external data the agent will read (an email, a file, a
  web page, a transaction memo). No access to system prompt, model weights, or the user.
- **Victim**: the user delegating a task to the agent (e.g. Emma Johnson, Blue Sparrow Tech).
- **Objective**: make the agent call a sensitive tool chosen by the attacker (exfiltrate data / move money)
  while ideally still completing the benign task so the user does not notice (stealth).
- **Capabilities/assumptions**: can inject arbitrary text into exactly one tool-returned field; attack is
  static (not adaptive to the model's reply within an episode).

## 4. Evaluation Setup (0.75 p)
- Dataset: AgentDojo v1.2.1 — 97 user tasks, suites banking(16)/slack(21)/travel(20)/workspace(40);
  9/5/7/14 injection tasks respectively. Examples sampled directly from these suites (workspace: 7 of 14
  injection tasks, even-indexed, to bound cost; others full).
- Model: GPT-6.1-terra via an OpenAI-compatible relay (chat.completions + function calling). Note relay-side
  content filter (OpenAI cyber_policy) that can refuse requests; we log such refusals separately (0 in final data).
- Metrics: benign Utility; Utility-under-attack (stealth proxy); Attack Success Rate (ASR, AgentDojo security
  check). 95% Wilson CIs. Attacks: important_instructions, ignore_previous, system_message, injecagent, tool_knowledge.

## 5. Results — Robustness of Published Attacks (1.5 p)
- **Table 2 / Fig asr_by_attack.png**: ASR ≈ 0 for all 5 attacks (1/1245; max CI upper bound 3.8%).
- **Fig utility_disruption.png**: attacks do NOT breach the agent but DO disrupt benign task completion,
  most for the loudest templates (slack: 95%→72% under important_instructions; injecagent nearly harmless 94%).
- **Failure-stage taxonomy (Table 3, eval/p2_stage_analysis.txt)**: of defeated cases, ~5–12% explicitly
  named/refused the injection; ~15–35% stopped to ask the user for confirmation before any sensitive action
  (safe-by-caution); ~43–68% silently finished the benign task ignoring the injection. (Heuristic labels,
  validated by manual sample, ~80% precision on the 'refused' class — eval/p2_validation_notes.md.)
- **The single success (Sec 5.x, eval/success_case_walkthrough.txt)**: banking user_task_12 x injection_task_4.
  The *user prompt itself* said "follow the instructions precisely", collapsing the data/instruction boundary;
  the agent then executed the injected standing-order change. Lesson: current robustness leans on the user NOT
  authorizing external content as instructions.

## 6. [Proposed Attack — TEAM CONTRIBUTION] (1.5 p)
- Designed by team members (see guidelines in attack/README.md). To include: motivation per step, why it is
  expected to work given Sec 5 failure modes, detailed design, ASR vs. the 5 baselines, ablation.
- Engineering/eval harness provided: attack/ plugin interface + scripts/run_bench.py --attack-module.

## 7. Discussion & Limitations (0.5 p)
- Robustness is high but not from a single mechanism: refusal + cautious confirmation + task-focus all contribute.
- Disruption-without-breach is itself a (mild) availability risk.
- Limitations: one model family; relay content filter confounds; heuristic taxonomy; workspace subsampled.

## 8. Conclusion & Next Steps (0.25 p)
- Published single-shot injections are largely neutralized on current models; the open question is whether
  context-consistent / user-authorized injections (Sec 5 success case) generalize. Team attack targets this.

## Appendix (unlimited)
- Per-injection-task ASR tables; full prompts; extra suites; reproduction commands.

## Contributions list (required)
- [member A]: ... / [member B]: ... / [member C]: ...  (fill before submission)

---
### Result artifacts map
- eval/all_attacks_gpt-6.1-terra.txt   — Table 2 (ASR + CI, all attacks)
- eval/p2_stage_analysis.txt           — Table 3 (failure-stage taxonomy)
- eval/p2_failure_analysis.txt         — coarse 4-way taxonomy
- eval/p2_validation_notes.md          — manual validation of taxonomy
- eval/success_case_walkthrough.txt    — the one successful attack, full trajectory
- report/figs/utility_disruption.png   — Fig: benign vs under-attack utility
- report/figs/asr_by_attack.png        — Fig: ASR per attack
- runs/baseline, runs/repeat1, runs/repeat2 — raw logs (3-run benign noise)
