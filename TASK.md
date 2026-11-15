# Course Project: LLM Agent Security (Attack / Defense)

## Objective
- Understand the design philosophy of LLM agents and how they are applied to specific tasks
- Reveal potential risks in LLM agents and/or develop countermeasures

## Guidelines
1. Find 1-2 LLM agents of interest. Understand their tasks and how they work. Download code, go through the pipeline. ($20 OpenAI API fund per team)
2. Think about a common risk — how can the agent be attacked?
3. Implement the attack; if it fails, analyze why and refine until a few successful cases.
4. Defense teams: identify a general attack applicable to the selected agents, then develop the defense.
5. Prepare presentation and final report.

## Presentation (Zoom, 25-30 min + 5-10 min QA, everyone presents; Nov 4/10/11/12/17/18/19)
1. Introduction + roadmap
2. Review of the agents: task, input/output, structure (all modules), inference pipeline, brief performance
3. Proposed attack/defense
   - Attack category + brief review
   - Threat model: attacker, victim, concrete objectives, assumptions & capabilities
   - Attack overview: main steps, technical challenges per step, high-level techniques
   - Attack details: motivation per step (why expected to work), detailed design
   - Defense: threat model, the attack defended against, defense techniques
4. Evaluation: dataset (where test examples are sampled from) + metrics; expected results & reasoning; (optional) results, demos
5. Conclusion: summary, takeaways, next steps / plan if it doesn't work

## Final report
- Presentation content + experimental results & discussion + per-member contribution list
- Deadline: Dec 9, 2026, midnight ET (no late submissions)
- 9 pages incl. figures/tables (references and appendix don't count), NeurIPS template
- AI-detection: >=60% AI-generated text triggers human inspection -> write the prose yourselves
- Submit attack/defense code with the report (NOT just the original agent code)
- Score = team_score x contribution_factor (100% / 50% / 0%)
