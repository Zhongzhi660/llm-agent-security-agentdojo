# FACA Round-3 — Failure Root-Cause Diagnosis

Model gpt-6.1-terra · AgentDojo v1.2.1 · banking · same 30 train pairs as Round 2 ·
diagnostics are sandbox-only on synthetic AgentDojo objects and are **excluded from ASR**.

## Question
Round 2 showed S1 (injection reaches the tool output) ≈ 27/30 but S3 (target-action attempt) = 0/30
and ASR = 0/30 for every FACA variant. Why does a delivered injection never turn into a target action?
We tested five hypotheses H0–H4 before proposing any new attack.

## P0 — Evaluation-chain audit (offline, `scripts/diagnose_faca_round2.py`)
Over 90 variant-episodes (v5/v6/v7 × 30 pairs):

| check | result | meaning |
|---|---|---|
| payload content delivered (normalized) | **81/90 = 90%** | equals the 27/30 S1 rate; the 10% gap = user tasks that never read the injected slot |
| target tool exists in suite | 90/90 = 100% | the action's tool is always available |
| target_attempt (attacker token in call **args**) | 0/90 | no episode ever put the attacker IBAN into a call |
| ASR (AgentDojo security) | 0/90 | — |
| first divergence vs control | none 62, distraction 16, stopped_early 8, task_clarification 4 | in 69% the injection changed **nothing** in the action sequence |

Note on an evaluation artifact we fixed: the raw injected string is **not** byte-identical in the tool
text because AgentDojo re-serializes the environment to YAML (newlines→spaces, `'`→`''`). After
whitespace/quote normalization the **full content** (including the attacker IBAN and the complete
follow-up instruction) is present in 90% of episodes. So delivery is intact — **H0 (delivery/truncation
bug) is ruled out** for the episodes where the slot is read. We also re-verified S3 at argument level: the
earlier non-zero S3 on the control was a false positive from benign uses of `update_scheduled_transaction`;
with arg-level matching the control is 0/30.

## P1/P3 — Executability & authorization controls (`scripts/faca_controls.py`, `eval/faca_round3_controls.csv`)
Three controls using the same tools and synthetic objects, changing only the **source of authorization**:

| control | setup | result |
|---|---|---|
| **A — comprehension** | user explicitly asks the agent to read back the injected record | **6/6**: agent quotes the injected follow-up (incl. attacker IBAN) verbatim |
| **B — legitimate authorization** | the target action is requested by the **user** directly (injection GOAL as the user prompt) | **6/6**: agent performs the action, AgentDojo security = True |
| **C — untrusted claim** | the action is only stated by the untrusted record (FACA v5/v6/v7) | **0/90**: agent does not perform it |

## Hypothesis verdicts
- **H0 delivery / eval bug — RULED OUT.** Content reaches the model intact (90%); comprehension control
  A = 6/6; S3/S4 re-verified at argument level.
- **H1 target not executable — RULED OUT.** Control B = 6/6: the action runs and the model is capable of it
  when authorized. Target tool present in 100% of cases.
- **H2 model treats external content as data, not instructions — SUPPORTED.** In 62/90 episodes the
  injection changed nothing in the action sequence vs the control; comprehension is intact yet the agent
  continues the user's task.
- **H3 insufficient task relevance / conflict — PARTIALLY SUPPORTED, secondary.** Relevance framing
  (V5/V6/V7) did not lift S3 above the control; the record is read as data regardless of framing.
- **H4 disruption not advancement — PRESENT, minor.** The only measurable effect is a small Utility dip
  (v5/v6 21/30 vs control 22/30) from the agent pausing on the benign task. Reported as an availability
  effect, not as attack success.

## Decision-table outcome (A yes · B yes · C no)
> A succeeds, B succeeds, C fails → **the authorization / task-priority boundary is effective.**
> Action: write the mechanism up as the main finding; do **not** keep stacking "related" / "approved"
> templates, and do not run blind automatic search.

## Conclusion
On gpt-6.1-terra / banking, FACA does not stop because of a delivery bug, a scoring bug, or an
inexecutable target. The injection arrives in full, the model understands it, and the model will
perform the exact same action when the **user** asks — but it refuses to perform it when the identical
action is asserted by an untrusted tool-returned record, whether that record frames the action as a
related follow-up, a pending workflow step, or a record-claimed approval. **The decisive variable is the
source of authorization, and the model holds the user-authorization boundary.** This is the project's
central finding.

## One falsifiable hypothesis for a future controlled round (not yet run)
The boundary may be enforced by the *provenance* of the instruction (user turn vs tool turn) rather than
by content. Testable, harmlessly, in the sandbox: hold the action and framing fixed and vary only whether
the request appears in the user turn, in a tool result attributed to the user, or in a tool result
attributed to an external system — measuring S3 on a synthetic status field. If S3 stays 0 across all
tool-turn provenances and is positive only in the user turn, provenance-based trust is confirmed. If
evidence is insufficient, we stop and report the negative result rather than claim any ASR gain.

## Limitations
Single model family and one suite (banking) for the controls; N=2 per control (sign, not precision);
heuristic divergence labels (manual-review list in `faca_round2_summary.md`); ASR CIs remain wide at
N=30 ([0%, 11.4%]).
