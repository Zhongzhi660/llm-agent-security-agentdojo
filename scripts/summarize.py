"""Summarize AgentDojo logs: utility (no attack), utility under attack, and ASR per attack.
Usage: python scripts/summarize.py runs/baseline/gpt-6.1-terra [suite]"""
import json, sys
from collections import defaultdict
from pathlib import Path
import math

def wilson(k, n, z=1.96):
    """95% Wilson score interval for a binomial proportion, returned as (lo, hi)."""
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c - h), min(1.0, c + h))

root = Path(sys.argv[1]); suites = sys.argv[2:] or None
stats = defaultdict(lambda: {"n": 0, "util": 0, "sec": 0, "err": 0, "blocked": 0})
per_inj = defaultdict(lambda: [0, 0])
for f in root.glob("*/user_task_*/*/*.json"):
    suite, atk = f.parts[-4], f.parts[-2]
    if suites and suite not in suites: continue
    d = json.load(open(f))
    if "utility" not in d: continue  # run still in progress
    s = stats[(suite, atk)]
    s["blocked"] += "[BLOCKED_BY_PROVIDER_FILTER]" in json.dumps(d["messages"])
    s["n"] += 1; s["util"] += bool(d["utility"]); s["err"] += d.get("error") is not None
    if atk != "none":
        s["sec"] += bool(d["security"]); per_inj[(suite, atk, d["injection_task_id"])][0] += bool(d["security"])
        per_inj[(suite, atk, d["injection_task_id"])][1] += 1
print(f"{'suite':10}{'attack':28}{'N':>5}{'Utility':>10}{'ASR':>9}{'ASR 95% CI':>17}{'errors':>8}{'blocked':>9}")
for (suite, atk), s in sorted(stats.items()):
    asr = f"{s['sec']/s['n']:.1%}" if atk != "none" else "-"
    lo, hi = wilson(s['sec'], s['n']); ci = f"[{lo:.1%}, {hi:.1%}]" if atk != "none" else "-"
    print(f"{suite:10}{atk:28}{s['n']:>5}{s['util']/s['n']:>10.1%}{asr:>9}{ci:>17}{s['err']:>8}{s['blocked']:>9}")
if per_inj:
    print("\nASR per injection task:")
    for (suite, atk, it), (k, n) in sorted(per_inj.items()):
        print(f"  {suite}/{atk}/{it}: {k}/{n}")
