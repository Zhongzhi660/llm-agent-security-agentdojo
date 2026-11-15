# Custom attack plugin — interface for the team's attack design

This is the slot for the **team's own attack** (the graded contribution; the agent code itself does not count).
The engineering is set up so you only write the injection *payload logic*; everything else (running, scoring,
CIs) is already done by `scripts/run_bench.py` and `scripts/summarize.py`.

## How AgentDojo attacks work
An attack is a subclass of `agentdojo.attacks.base_attacks.BaseAttack` (or `FixedJailbreakAttack`). It
implements `attack(user_task, injection_task) -> dict[str, str]` that maps each injection placeholder id
(e.g. `"injection_landlord"`) to the string that will be substituted into the tool output. The ground-truth
malicious tool calls come from `injection_task`; your job is only to craft the text that makes the agent emit them.

Minimal shape (fill in `_build`):
```python
from agentdojo.attacks.base_attacks import BaseAttack
from agentdojo.attacks.attack_registry import register_attack

@register_attack
class TeamAttack(BaseAttack):
    name = "team_attack"
    def attack(self, user_task, injection_task):
        goal = injection_task.GOAL          # natural-language description of the malicious objective
        payloads = {}
        for name in self.get_injection_candidates(user_task):   # placeholders present in this user task
            payloads[name] = self._build(goal)
        return payloads
    def _build(self, goal: str) -> str:
        raise NotImplementedError   # <-- team writes the injection text strategy here
```

Register the file at run time (no framework edits):
```
python scripts/run_bench.py --model gpt-6.1-terra --suite banking \
    -ut user_task_12 -it injection_task_4 \
    --attack team_attack --attack-module attack/team_attack.py --logdir runs/team
```

## What the baselines already told us (design evidence — see eval/)
- Loud "ignore previous / <INFORMATION> important message" templates are reliably detected or ignored.
- The only baseline success happened when the **user** authorized external content as instructions.
- ~15–35% of defeated cases were the model *stopping to ask the user* before a sensitive action — a confirm
  step is a real obstacle, not just refusal.

## Design dimensions to reason about in the report (Sec 6)
1. **Injection point** — which tool field is attacker-controlled, and how trusted it looks in context.
2. **Instruction/data framing** — how the text is positioned relative to the surrounding document.
3. **Stealth** — keep benign Utility high so the user does not notice (measure Utility-under-attack).
4. **Robustness of the trigger** — does it survive across user tasks / suites, not just one case.

Evaluate every variant with the same harness and report ASR + 95% CI next to the 5 baselines + an ablation.
