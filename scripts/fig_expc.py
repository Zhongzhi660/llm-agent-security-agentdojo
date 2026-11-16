"""Figure for Experiment C: source vs dialogue-position decoupling."""
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("eval/expc_provenance_pairs.csv")))
ex = defaultdict(lambda: [0, 0])  # arm -> [executed_pairs, n_pairs]
for r in rows:
    ex[r["arm"]][0] += int(r["executed_any"])
    ex[r["arm"]][1] += 1

arms = ["U1", "U2", "Rext", "Ruser"]
labels = ["U1\nuser / early", "U2\nuser / LATE", "Rext\nexternal / late", "Ruser\nclaims-user / late"]
rates = [ex[a][0] / ex[a][1] * 100 for a in arms]
# user-sourced = green, external/untrusted = red
colors = ["#1F9D64", "#1F9D64", "#E03E3E", "#E03E3E"]

fig, ax = plt.subplots(figsize=(6.4, 3.4))
bars = ax.bar(range(len(arms)), rates, color=colors, width=0.62)
ax.set_xticks(range(len(arms)))
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Executed target action (% of pairs)")
ax.set_ylim(0, 112)
ax.set_title("Experiment C: source decides, not dialogue position\n"
             "(byte-identical action T; gpt-6.1-terra, banking, N=20 pairs)", fontsize=9.5)
for i, a in enumerate(arms):
    ax.text(i, rates[i] + 2, f"{ex[a][0]}/{ex[a][1]}", ha="center", fontsize=8.5, fontweight="bold")

# bracket the decisive late-position contrast U2 vs Rext
y = 104
ax.plot([1, 1, 2, 2], [y - 2, y, y, y - 2], color="#14172A", lw=1.1)
ax.text(1.5, y + 0.5, "same late position\nsource flipped", ha="center", va="bottom",
        fontsize=7.5, color="#14172A")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("report/figs/expc_provenance.png", dpi=150)
print("Wrote report/figs/expc_provenance.png", {a: tuple(ex[a]) for a in arms})
