# Presentation Outline (25-30 min, everyone presents). Maps 1:1 to grading rubric.

1. Title + roadmap (1 slide)
2. The agent: AgentDojo tool agent — task, input/output (1)
3. Agent modules diagram: SystemMessage→InitQuery→LLM→ToolsLoop(+defense) (1)
4. Inference pipeline walkthrough + where injection enters (1, animate the one success trajectory)
5. Benign performance table (1) [figs/utility_disruption.png blue bars]
6. Attack category: indirect prompt injection — brief review + prior ASR on 2024 models (1)
7. Threat model: attacker/victim/objective/capabilities (1)
8. Attack overview: steps + challenges + technique [TEAM] (1-2)
9. Attack details: motivation + design per step [TEAM] (1-2)
10. Evaluation setup: AgentDojo v1.2.1 suites, GPT-6.1, metrics, CIs (1)
11. Results: ASR of 5 baselines ≈0 [figs/asr_by_attack.png] (1)
12. Results: disruption-without-breach + failure-stage taxonomy (1)
13. The one success case: user authorized external content (1, demo)
14. [TEAM attack results + demo] (1-2)
15. Conclusion: takeaways + next steps (1)

Speaking split: assign slides 2-5 / 6-7,10-13 / 8-9,14 to the three members.
