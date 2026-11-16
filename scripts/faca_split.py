"""Deterministic 60/20/20 train/val/test split by user_task_id (per suite).

All injection cases of a given user task stay in the same split. Frozen by a fixed
seed so the test set never changes. Prints or returns the split.

Usage: python scripts/faca_split.py [suite]   (default: all four)
"""
import random
import sys

SUITES = {"banking": 16, "slack": 21, "travel": 20, "workspace": 40}
SEED = 20241115


def split(suite: str, n: int):
    ids = [f"user_task_{i}" for i in range(n)]
    rng = random.Random(f"{SEED}:{suite}")
    rng.shuffle(ids)
    n_tr = round(n * 0.6)
    n_va = round(n * 0.2)
    return {"train": sorted(ids[:n_tr], key=lambda s: int(s.split("_")[-1])),
            "val": sorted(ids[n_tr:n_tr + n_va], key=lambda s: int(s.split("_")[-1])),
            "test": sorted(ids[n_tr + n_va:], key=lambda s: int(s.split("_")[-1]))}


def get(suite: str):
    return split(suite, SUITES[suite])


if __name__ == "__main__":
    which = sys.argv[1:] or list(SUITES)
    for s in which:
        sp = get(s)
        print(f"\n== {s} (n={SUITES[s]}) ==")
        for k in ("train", "val", "test"):
            print(f"  {k:5} ({len(sp[k])}): {' '.join(t.split('_')[-1] for t in sp[k])}")
