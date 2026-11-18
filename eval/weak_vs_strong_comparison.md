# Weak vs Strong model — same attacks, same 30 banking train pairs

> **Note (Round 5):** the weak-model FACA figure below (v7 = 10%) used the *hedged* FACA
> that undercut its own authorization claim. After removing that hedge, FACA v8–v10 reach
> 63–70% on Qwen3.6-flash and beat the strongest baseline (`important_instructions`, 53%).
> See `eval/round5_faca_vs_baselines.md` for the current weak-model numbers.

Same AgentDojo banking suite, same 30 (user_task × injection_task) pairs, same attack code.
ASR = AgentDojo security verdict. 95% Wilson CI in brackets.

| attack | gpt-6.1-terra (strong) | qwen3.6-flash (weak) |
|---|---|---|
| important_instructions (published) | 0/30 = 0.0% [0%,11.4%] | 12/30 = 40.0% [25%,58%] |
| FACA-v7 (ours) | 0/30 = 0.0% [0%,11.4%] | 3/30 = 10.0% [3.5%,26%] |
| control (benign record) | 0/30 = 0.0% [0%,11.4%] | 0/30 = 0.0% [0%,11.4%] |

(Wider probe, qwen3.6-flash, user_task_0..9 × inj 0/4/8: important_instructions ASR 17/30 = 56.7%.)

## What this establishes
1. **Our attack code works.** The identical injection that scores ~0 on gpt-6.1-terra succeeds on a
   weaker model (40% with the published attack), so the 0% on the strong model is a property of the
   MODEL, not a bug in the harness or payloads.
2. **FACA is a real-but-weaker attack.** FACA-v7 reaches 10% on the weak model (vs 0% strong). It is
   deliberately quieter than important_instructions (40% weak), which matches its design: it blends in,
   so it is both less detectable and less compelling — on a weak model that trades off to lower ASR.
3. **Control stays 0 on both models.** The benign same-format record never triggers the action, so the
   weak-model successes are driven by the injected imperative, not by format/length.
4. **Robustness is model-scale/training dependent.** gpt-6.1-terra resists every attack here; a smaller
   model does not. This frames the Round-3/4 finding: the strong model's user-authorization boundary is
   exactly what the weak model lacks.

## Note
deepseek-v4.1-flash was also available but produced tool-call outputs AgentDojo could not parse into
completed trajectories (utility/security = None); excluded. qwen3.6-flash is the weak-model baseline.
