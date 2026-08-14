#!/usr/bin/env python3
"""
plot_rank_sweep.py — figure for the low-rank subsection.

Left:   singular-value energy of the tile-by-look matrix. Degree-2 detrending of an
        11-sample record projects out 3 dimensions, so the matrix is EXACTLY rank 8.
        That is why the published LRSD step at its library default reports "rank 8
        of 11": it is not truncating at all, it is returning the input.
Right:  per-tile reported depth as the retained rank is forced down. At rank 1 all
        3,481 tiles report the same depth to machine precision — a perfectly flat,
        perfectly continuous horizontal layer, from an input containing no scene.
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, steering, analytic1d

SW = json.load(open("runs/rank_sweep.json"))
obs = np.load(f"runs/obs_{SW['label']}_p{SW['patch']}_s{SW['stride']}_n{SW['n_sub']}.npy")

zgrid = np.linspace(0, SW["n_sub"] * DZ_TARGET / 2, 300)
A, _ = steering(SW["n_sub"], zgrid)
cells = zgrid / DZ_TARGET

U, sv, Vt = np.linalg.svd(obs, full_matrices=False)


def peaks(m):
    prof = np.abs(A.conj().T @ np.array([analytic1d(o) for o in m]).T) ** 2
    return cells[np.argmax(prof, axis=0)]


fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0))

ax = axes[0]
en = np.array(SW["singular_value_energy"])
ax.bar(np.arange(1, len(en) + 1), 100 * en, color="0.35")
ax.axvline(8.5, color="crimson", ls="--", lw=1.2)
ax.text(8.65, 0.92 * 100 * en.max(), "rank 8: degree-2 detrending\nof an 11-sample record\nleaves exactly 8 dimensions",
        color="crimson", fontsize=8, va="top")
ax.set_xlabel("component"); ax.set_ylabel("% of variance")
ax.set_title("A. The matrix the low-rank step acts on is already rank 8", fontsize=10)
ax.set_xticks(np.arange(1, len(en) + 1))

ax = axes[1]
for r, col in zip([1, 2, 3, 8], ["crimson", "darkorange", "seagreen", "0.35"]):
    p = peaks((U[:, :r] * sv[:r]) @ Vt[:r])
    lab = f"rank {r}" + ("  (= no truncation)" if r == 8 else "")
    if r == 1:
        ax.axvline(p[0], color=col, lw=2.2,
                   label=f"rank 1 — all {len(p)} tiles at {p[0]:.2f} cells")
    else:
        ax.hist(p, bins=np.linspace(1.0, 5.0, 120), histtype="step", lw=1.4,
                color=col, label=lab)
ax.set_xlabel("reported depth (resolution cells)")
ax.set_ylabel("tiles")
ax.set_xlim(1.0, 5.0)
ax.set_title("B. Forcing the rank down collapses every tile to one depth", fontsize=10)
ax.legend(fontsize=8, frameon=False)

fig.suptitle("Low-rank denoising manufactures a flat continuous layer from an input containing no scene",
             fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
out = "runs/rank_sweep.png"
fig.savefig(out, dpi=140, bbox_inches="tight")
print("figure ->", out)
