#!/usr/bin/env python3
"""Figure for section 5.5: both decision criteria, on data containing no scene."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = json.load(open("runs/guard_confirm.json"))
arms = D["arms"]
LAB = {"none": "no preprocessing\n(this paper)",
       "LRSD default": "the authors' own\ndenoising step",
       "low-pass [1,2,1]/4": "low-pass\n[1,2,1]/4",
       "high-pass [1,-2,1]/4": "high-pass\n[1,−2,1]/4",
       "searched kernel": "kernel found by\ndirect search"}
COL = {"none": "0.35", "LRSD default": "darkorange", "low-pass [1,2,1]/4": "seagreen",
       "high-pass [1,-2,1]/4": "steelblue", "searched kernel": "crimson"}
names = [a["arm"] for a in arms]

fig, ax = plt.subplots(1, 2, figsize=(11.6, 4.5))
xs = np.arange(len(arms))

a0 = ax[0]
a0.bar(xs, [a["ratio_med"] for a in arms], color=[COL[n] for n in names], width=.62)
a0.axhline(5, color="crimson", lw=1.3)
a0.text(len(arms) - .45, 5.35, "5× rule", color="crimson", fontsize=8.5, ha="right")
for i, a in enumerate(arms):
    a0.text(i, a["ratio_med"] + .35, f"{a['ratio_med']:.2f}", ha="center", fontsize=8.5)
a0.set_xticks(xs); a0.set_xticklabels([LAB[n] for n in names], fontsize=8)
a0.set_ylabel("contrast / alignment-null ratio")
a0.set_title("A. Criterion (a) — the contrast rule", fontsize=10)

a1 = ax[1]
a1.bar(xs, [a["peak"] for a in arms], color=[COL[n] for n in names], width=.62)
a1.axhline(2.0, color="crimson", lw=1.3)
a1.text(len(arms) - .45, 2.12, "2-cell depth guard", color="crimson", fontsize=8.5, ha="right")
for i, a in enumerate(arms):
    a1.text(i, a["peak"] + .12, f"{a['peak']:.2f}", ha="center", fontsize=8.5)
a1.set_xticks(xs); a1.set_xticklabels([LAB[n] for n in names], fontsize=8)
a1.set_ylabel("reported peak depth (resolution cells)")
a1.set_title("B. Criterion (b) — the depth guard", fontsize=10)

for i, a in enumerate(arms):
    if a["false_med"] > 0:
        for axx in (a0, a1):
            axx.patches[i].set_edgecolor("black")
            axx.patches[i].set_linewidth(2.0)

fig.suptitle("On an input containing no scene, one searched kernel clears BOTH criteria "
             "in 200 of 200 blocks (outlined bar)", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("runs/guard_confirm.png", dpi=140, bbox_inches="tight")
print("figure -> runs/guard_confirm.png")
for a in arms:
    print(f"  {a['arm']:<24} ratio {a['ratio_med']:6.2f}  peak {a['peak']:.2f}  "
          f"false {100*a['false_med']:3.0f}%  (p95 null: {100*a['false_p95']:3.0f}%)")
