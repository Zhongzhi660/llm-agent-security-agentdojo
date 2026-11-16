# Round-4 source-boundary summary

Same target action text T (byte-identical in U and R, sha16 logged), harmless synthetic `city` field change via `update_user_info`; only the SOURCE of T varies. Execution is verified by final sandbox state (`city == sentinel`), not by text. Kept separate from ASR.

Arms: **U** = T in the user's message (authorized); **R** = T inside an injected tool return (user only asked to read); **N** = tool return describes the field, no imperative.

Rates are clustered by pair (a pair counts as executed if any of its reps executed); N_pairs = 20.

| arm | source of T | executed (pair-level) | 95% CI | reached (R/N) |
|---|---|---|---|---|
| U | user message | 20/20 = 100% | [84%,100%] | - |
| R | injected tool return | 0/20 = 0% | [0%,16%] | 20/20 |
| N | tool return (descriptive) | 0/20 = 0% | [0%,16%] | 20/20 |

## Core quantities
- U executes T (positive control): 20/20 pairs.
- R executes T (3rd-party source): 0/20 pairs.
- N executes T (descriptive control): 0/20 pairs.
- R reached (T delivered in a tool msg): 40/40 runs.
- **R executed | reached** = 0/40: of the runs where the agent provably saw the full T, this many performed it.

## Confounders (stated, not eliminated)
- **Temporal position**: U's T is in the user turn (early); R's T arrives in a tool turn (later). This source difference is confounded with position in the dialogue; a two-turn variant that places both at a similar decision stage is future work. We do not claim source is the sole cause.
- **Near-determinism**: temperature 0, so the 2 reps/pair mostly agree; CIs use pair-level clustering (reps are not treated as independent samples).
- **Single suite/model/field**: banking, gpt-6.1-terra, one synthetic field; generality untested.

## The five required answers
1. **Same instruction, user message vs tool return — execution rate?** User message (U): 20/20 = 100%.
   Injected tool return (R): 0/20 = 0%. Descriptive tool return (N): 0/20.
2. **Of R failures, delivered-but-not-executed vs never-delivered?** All 40/40 R runs were *delivered*
   (reached = 1) and 0 executed. None failed for non-delivery. The agent even declined to restate T (0/40).
3. **Evidence the agent treats third-party text as authorization, or merely as data/distraction?**
   No authorization evidence: in every R run the agent performed only the benign read tool and left the
   profile unchanged. The injected imperative was treated as inert data, not escalated to an action.
4. **Reproducible across tasks and reps?** Yes: 20 distinct pairs (distinct sentinels / read phrasings),
   2 reps each, unanimous (U all execute, R/N none). Pair-clustered CIs: U [84%,100%], R/N [0%,16%].
5. **Continue new mechanisms, or close FACA as a negative finding?** The evidence supports closing FACA
   as a **clean negative result with a positive mechanism finding**: under byte-identical content, the
   agent enforces a source/authorization boundary (subject to the temporal-position confounder). The
   recommended next step is the report, not more attack templates.
