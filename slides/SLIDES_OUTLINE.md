# Presentation outline — 16 slides, 5 acts (~25–30 min)

Generated deck: `slides/faca_presentation.pptx` (generator `slides/build_deck.js`, pptxgenjs).
Each content slide carries a kicker (its act), one bold bottom TAKEAWAY, and a footer with page number.
Speaker notes are embedded in every slide. Author names are blank (`____`) — fill before the talk.

| # | Act | Slide | One-line message |
|---|---|---|---|
| 1 | — | Title: "Who is allowed to give the order?" | The thesis: agents bind instruction authority to the source. |
| 2 | — | The argument in five moves | The pivot is Act III (diagnose, don't stack templates). |
| 3 | I Setup | The agent + injection surface | The threat is one untrusted field on a tool result. |
| 4 | I Setup | Threat model | A deliberately weak attacker — realistic. |
| 5 | II Attacks fail | Published attacks ~0% (1/1245) | The lone success needed the user to authorize the text. |
| 6 | II Attacks fail | FACA design (V5/V6/V7) | Change only the framing, one factor at a time. |
| 7 | II Attacks fail | FACA still zero → pivot | A negative result we turn into the central question. |
| 8 | III Ask why | Hypotheses H0–H4 + controls A/B/C | Understands ✓ can do ✓ won't from untrusted source ✗. |
| 9 | III Decisive | Same action, only source differs (U/R/N) | Source of authorization is the decisive variable. |
| 10 | III Decisive | Experiment C: source vs position | Source decides, not position; structural turn-role. |
| 11 | IV Generality | Threshold across 8 models | Boundary is near-universal; one outlier. |
| 12 | IV Generality | Same task, two models (traces) | Weak wires money; strong names + refuses. |
| 13 | IV Generality | Defenses re-supply the boundary | Spotlighting = low ASR + utility kept; closes the loop. |
| 14 | V Takeaways | What we learned | One chain: fail → provenance → structural/threshold → defense. |
| 15 | V Takeaways | Limitations + next | Sign not precision; open door = adaptive provenance forgery. |
| 16 | — | Thank you / repo link | Reproducible; Q&A. |

## Rubric coverage
- Review of the agent (task/IO/modules/pipeline/benign perf): slides 3 (+ utility in takeaway).
- Attack category + threat model: slides 5, 4.
- Proposed attack (design, challenges, technique): slides 6, 7.
- Evaluation + results: slides 5, 7, 9–13.
- Root-cause / main finding: slides 8–10 (core).
- Generality + defense: slides 11–13.
- Conclusion + limitations: slides 14, 15.

## To finish before the talk
- Fill the three author names (`____`) on slides 1 and 16.
- Rehearse the Act II→III pivot (slide 7) — it is the spine of the talk.
- Optional: render to PDF (LibreOffice/PowerPoint) for a final visual pass; not available in this env.
