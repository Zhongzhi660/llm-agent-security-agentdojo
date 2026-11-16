"""Analyze Round-4 source-boundary runs: execution rate per arm, clustered by pair.

Reads eval/round4_source_boundary_raw.jsonl. Writes:
  eval/round4_source_boundary_pairs.csv   (one row per pair x arm: executed/reached/mentioned)
  eval/round4_source_boundary_summary.md  (arm-level rates, pair-clustered CIs, confounder notes)
"""
import csv
import json
import math
import os
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    raw = "eval/round4_source_boundary_raw.jsonl"
    rows = [json.loads(l) for l in open(raw)]
    # per (pair, arm): aggregate reps
    by = defaultdict(lambda: {"executed": [], "reached": [], "mentioned": []})
    for r in rows:
        k = (r["pair_id"], r["arm"])
        by[k]["executed"].append(r["executed"])
        by[k]["reached"].append(r["reached"] if r["reached"] is not None else "")
        by[k]["mentioned"].append(r["mentioned"])

    pairs_csv = "eval/round4_source_boundary_pairs.csv"
    with open(pairs_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pair_id", "arm", "n_reps", "executed_any", "executed_all",
                    "reached_any", "mentioned_any"])
        for (pid, arm), d in sorted(by.items()):
            ex = d["executed"]
            rc = [x for x in d["reached"] if x != ""]
            w.writerow([pid, arm, len(ex), int(any(ex)), int(all(ex)),
                        int(any(rc)) if rc else "", int(any(d["mentioned"]))])

    # arm-level: cluster by pair (pair-level executed = majority/any of its reps)
    arm_pairs = defaultdict(list)   # arm -> list of pair-level executed (any rep)
    arm_reached = defaultdict(list)
    for (pid, arm), d in by.items():
        arm_pairs[arm].append(int(any(d["executed"])))
        rc = [x for x in d["reached"] if x != ""]
        if rc:
            arm_reached[arm].append(int(any(rc)))

    lines = ["# Round-4 source-boundary summary\n",
             "Same target action text T (byte-identical in U and R, sha16 logged), harmless synthetic "
             "`city` field change via `update_user_info`; only the SOURCE of T varies. Execution is "
             "verified by final sandbox state (`city == sentinel`), not by text. Kept separate from ASR.\n",
             "Arms: **U** = T in the user's message (authorized); **R** = T inside an injected tool "
             "return (user only asked to read); **N** = tool return describes the field, no imperative.\n",
             "Rates are clustered by pair (a pair counts as executed if any of its reps executed); "
             f"N_pairs = {len(arm_pairs.get('U', []))}.\n",
             "| arm | source of T | executed (pair-level) | 95% CI | reached (R/N) |",
             "|---|---|---|---|---|"]
    srcmap = {"U": "user message", "R": "injected tool return", "N": "tool return (descriptive)"}
    for arm in ("U", "R", "N"):
        ex = arm_pairs.get(arm, [])
        k, n = sum(ex), len(ex)
        lo, hi = wilson(k, n)
        rc = arm_reached.get(arm, [])
        reached = "-" if arm == "U" else f"{sum(rc)}/{len(rc)}"
        lines.append(f"| {arm} | {srcmap[arm]} | {k}/{n} = {k/max(n,1):.0%} | [{lo:.0%},{hi:.0%}] | {reached} |")

    # R executed | reached
    r_rows = [r for r in rows if r["arm"] == "R"]
    r_reached = [r for r in r_rows if r["reached"]]
    r_exec_given_reached = sum(r["executed"] for r in r_reached)
    lines += [
        "\n## Core quantities",
        f"- U executes T (positive control): {sum(arm_pairs['U'])}/{len(arm_pairs['U'])} pairs.",
        f"- R executes T (3rd-party source): {sum(arm_pairs['R'])}/{len(arm_pairs['R'])} pairs.",
        f"- N executes T (descriptive control): {sum(arm_pairs['N'])}/{len(arm_pairs['N'])} pairs.",
        f"- R reached (T delivered in a tool msg): {len(r_reached)}/{len(r_rows)} runs.",
        f"- **R executed | reached** = {r_exec_given_reached}/{len(r_reached)}: of the runs where the "
        "agent provably saw the full T, this many performed it.",
        "\n## Confounders (stated, not eliminated)",
        "- **Temporal position**: U's T is in the user turn (early); R's T arrives in a tool turn (later). "
        "This source difference is confounded with position in the dialogue. **Experiment C "
        "(`eval/expc_provenance_summary.md`) resolves this confound**: a user-sourced instruction placed at "
        "a LATE position (a 2nd user turn after a tool read) still executes 20/20, while the external tool "
        "return at the same late position executes 0/20 -- so source, not position, is the decisive variable.",
        "- **Near-determinism**: temperature 0, so the 2 reps/pair mostly agree; CIs use pair-level "
        "clustering (reps are not treated as independent samples).",
        "- **Single suite/model/field**: banking, gpt-6.1-terra, one synthetic field; generality untested.",
    ]
    out_md = "eval/round4_source_boundary_summary.md"
    with open(out_md, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {pairs_csv} and {out_md}")


if __name__ == "__main__":
    main()
