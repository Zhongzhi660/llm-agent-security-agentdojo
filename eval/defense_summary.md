# Defense evaluation — closing the gap on the one vulnerable model (Qwen3.6-flash)

AgentDojo banking, same 30 user×injection pairs. We test AgentDojo's built-in defenses against the
two attacks that work on Qwen3.6-flash. ASR = AgentDojo security verdict; Utility = benign task still
completed. The goal is low ASR **and** high utility.

| attack | defense | ASR | Utility |
|---|---|---|---|
| important_instructions | none | 40% | 80% |
| important_instructions | tool_filter | **0%** | 40% |
| important_instructions | spotlighting_with_delimiting | 13% | 80% |
| important_instructions | repeat_user_prompt | 21% | 79% |
| FACA-V7 | none | 10% | 80% |
| FACA-V7 | tool_filter | **0%** | 40% |
| FACA-V7 | spotlighting_with_delimiting | 7% | 83% |
| FACA-V7 | repeat_user_prompt | 7% | 80% |

## Takeaways
- **Every defense reduces ASR**, but they trade off against utility differently.
- **tool_filter drives ASR to 0** — but it pre-restricts which tools the agent may call, which halves
  benign task completion (80% → 40%). Safety at a steep usability cost.
- **spotlighting_with_delimiting is the practical winner**: it wraps tool outputs in delimiters and tells
  the model to treat them as untrusted data. ASR 40% → 13% and 10% → 7%, with utility fully preserved
  (80–83%). This is exactly a provenance / data-vs-instruction signal — the same boundary the strong
  models already enforce internally, supplied here by the scaffold.
- **repeat_user_prompt** (re-assert the user's request after each tool result) helps FACA (10% → 7%) but
  less for the louder important_instructions (40% → 21%).

## Connection to the attack findings
Rounds 3–4 showed the strong models resist injection because they hold a user-authorization boundary.
The defenses that work best on the weak model are the ones that re-supply that boundary externally
(mark tool output as untrusted data). This closes the loop: the mechanism we identified in the strong
models is the same mechanism an effective defense restores in the weak one.
