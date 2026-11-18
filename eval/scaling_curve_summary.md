# Model comparison — indirect-injection robustness across 8 models

> **Note (Round 5):** the FACA-V7 column (Qwen3.6-flash = 10%) used the *hedged* FACA.
> With the hedge removed, FACA v8–v10 reach 63–70% on Qwen3.6-flash (vs `important_instructions`
> 53%). The 0% on all other models is unchanged. See `eval/round5_faca_vs_baselines.md`.

Same AgentDojo banking suite, same 30 user×injection pairs, same attack code.
ASR = AgentDojo security verdict (95% Wilson CIs in eval/scaling_curve.csv).

| model | important_instructions ASR | FACA-V7 ASR | benign utility | injection reached |
|---|---|---|---|---|
| Qwen3.6-flash | 12/30 = 40% | 3/30 = 10% | high | 27–30/30 |
| Qwen3.8-flash | 0/30 = 0% | 0/30 = 0% | 24/30 | 30/30 |
| Qwen3.7-plus | 0/30 = 0% | 0/30 = 0% | high | ~27/30 |
| Qwen3.7-max | 0/30 = 0% | 0/30 = 0% | 29/30 | 27/30 |
| Qwen3.8-max | 0/30 = 0% | 0/30 = 0% | high | ~27/30 |
| GLM-5.2 | 0/30 = 0% | 0/30 = 0% | 29/30 | 27/30 |
| Qwen4-max-preview | 0/30 = 0% | 0/30 = 0% | 26/30 | 30/30 |
| GPT-6.1-terra (strong ref) | 0/30 = 0% | 0/30 = 0% | ~22/30 | 27/30 |

## Finding: a threshold, not a gradient
Across 8 models from 4 families, only **Qwen3.6-flash** can be driven to execute the injected
action (40% with the published attack, 10% with FACA-V7). Every other model — including small
"flash" models — sits at 0%, with the injection verifiably delivered (reached 27–30/30) and the
benign task still completed (utility high). So the 0% is genuine refusal, not a failure to see the
payload or a failure to function.

Indirect-prompt-injection robustness appears to have become near-universal in this model
generation; Qwen3.6-flash is the lone outlier. This sharpens the earlier conclusion: the
user-authorization boundary (Rounds 3–4) is now standard behaviour, and our attack isolates the
one model that lacks it.
