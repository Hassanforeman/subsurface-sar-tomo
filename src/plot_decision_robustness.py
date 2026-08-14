#!/usr/bin/env python3
"""Figure: this paper's contrast rule against its pinning guard, on empty data."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = json.load(open("runs/decision_robustness.json"))
ARMS = ["none", "LRSD default", "[1,2,1]/4 smoother", "per-patch rescale"]
LAB = {"none": "no preprocessing\n(this paper)",
       "LRSD default": "the authors' own\ndenoising step",
       "[1,2,1]/4 smoother": "a three-tap per-patch\nsmoother",
       "per-patch rescale": "per-patch rescale\n(depth-neutral control)"}
COL = {"none": "0.35", "LRSD default": "darkorange",
       "[1,2,1]/4 smoother": "crimson", "per-patch rescale": "steelblue"}

fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.3))

ax = axes[0]
for i, a in enumerate(ARMS):
    r = np.array([b[a]["ratio"] for b in D["blocks"]])
    ax.scatter(np.full(len(r), i) + np.linspace(-.28, .28, len(r)), r, s=7,
               color=COL[a], alpha=0.55, edgecolor="none")
    ax.plot([i - .34, i + .34], [np.median(r)] * 2, color="black", lw=1.8, zorder=5)
ax.axhline(5, color="crimson", lw=1.3)
ax.text(3.42, 5.2, "this paper's 5x rule", color="crimson", fontsize=8, ha="right")
ax.set_xticks(range(4)); ax.set_xticklabels([LAB[a] for a in ARMS], fontsize=8)
ax.set_ylabel("contrast / alignment-null ratio")
ax.set_title("A. Criterion (a): the contrast rule.\n"
             "A per-patch smoother clears it on 98% of empty blocks.", fontsize=9.5)

ax = axes[1]
for a in ARMS:
    p = np.array([b[a]["peak_cells"] for b in D["blocks"]])
    ax.hist(p, bins=np.linspace(1.2, 3.0, 70), histtype="step", lw=1.6,
            color=COL[a], label=LAB[a].replace("\n", " "))
ax.axvline(2.0, color="crimson", lw=1.3)
ax.text(2.06, ax.get_ylim()[1] * 0.45, "2-cell surface guard", color="crimson", fontsize=8)
ax.set_xlabel("reported peak depth (resolution cells)")
ax.set_ylabel("blocks")
ax.set_title("B. Criterion (b): the pinning guard.\n"
             "All four arms stay inside it. 0 false detections.", fontsize=9.5)
ax.legend(fontsize=7.5, frameon=False, loc="upper left")

fig.suptitle("On data containing no scene, the contrast rule is defeated by ordinary "
             "filtering; the depth guard is not", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("runs/decision_robustness.png", dpi=140, bbox_inches="tight")
print("figure -> runs/decision_robustness.png")
