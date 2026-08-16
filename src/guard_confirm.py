#!/usr/bin/env python3
"""
guard_confirm.py — regenerates every row of Table 4 in one run.

WHY THIS EXISTS
---------------
Table 4 was previously assembled from three separate runs at different seeds, and
two of its source files had no generating script in the repository. An audit
flagged both. This script produces the whole table in a single pass, with one
seed, one block set, and one permutation count, and writes the file the paper
cites.

Every arm is a per-patch operator applied to each analysis patch INDEPENDENTLY:
it transfers no information between patches. Input contains no scene - it is
band-limited complex speckle pushed through the identical published pipeline.

Both null conventions are reported: the median of the alignment null (used
throughout the paper) and its 95th percentile (the more conservative choice a
reviewer might prefer).

  python3 src/guard_confirm.py
"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from micromotion import lrsd_denoise
from tomogram import (DZ_TARGET, tomogram_from_observations, contrast, alignment_null)
from guard_robustness import fir

ARMS = [
    ("none",                       None),
    ("LRSD default",               "lrsd"),
    ("low-pass [1,2,1]/4",         [0.25, 0.5, 0.25]),
    ("high-pass [1,-2,1]/4",       [0.25, -0.5, 0.25]),
    ("searched kernel",            [-0.169, 0.159, -0.312, 0.182, -0.178]),
]

ap = argparse.ArgumentParser()
ap.add_argument("--obs", default="runs/obs_noise_c768_p64_s12_n11.npy")
ap.add_argument("--n-patch", type=int, default=24)
ap.add_argument("--n-block", type=int, default=200)
ap.add_argument("--n-perm", type=int, default=64)
ap.add_argument("--guard-cells", type=float, default=2.0)
ap.add_argument("--seed", type=int, default=4242)
ap.add_argument("--out", default="runs/guard_confirm.json")
a = ap.parse_args()

OBS = np.load(a.obs)
n_look = OBS.shape[1]
zgrid = np.linspace(0, n_look * DZ_TARGET / 2, 300)
cells = zgrid / DZ_TARGET
rng = np.random.default_rng(a.seed)
BLOCKS = [OBS[rng.choice(len(OBS), a.n_patch, replace=False)] for _ in range(a.n_block)]

rows = []
for tag, k in ARMS:
    rm, rp, pk = [], [], []
    for b, blk in enumerate(BLOCKS):
        o = blk if k is None else (lrsd_denoise(blk)[0] if k == "lrsd" else fir(blk, k))
        T = tomogram_from_observations(o, zgrid)
        c = float(contrast(T))
        nul = alignment_null(o, zgrid, np.random.default_rng(31000 + b), n_perm=a.n_perm)
        rm.append(c / (float(np.median(nul)) + 1e-12))
        rp.append(c / (float(np.percentile(nul, 95)) + 1e-12))
        pk.append(float(cells[int(np.argmax(T.sum(0)))]))
    rm, rp, pk = np.array(rm), np.array(rp), np.array(pk)
    unp = pk > a.guard_cells
    rows.append(dict(arm=tag, ratio_med=float(np.median(rm)), ratio_p95=float(np.median(rp)),
                     peak=float(np.median(pk)),
                     clears5_med=float(np.mean(rm > 5)), clears5_p95=float(np.mean(rp > 5)),
                     unpinned=float(np.mean(unp)),
                     false_med=float(np.mean((rm > 5) & unp)),
                     false_p95=float(np.mean((rp > 5) & unp))))
    print(f"  {tag} done", flush=True)

hdr = (f"{'per-patch operator':<24}{'ratio':>8}{'peak':>7}{'clears5x':>10}"
       f"{'unpinned':>10}{'FALSE':>8}{'clears5x':>10}{'FALSE':>8}")
print("\n" + "=" * len(hdr))
print(f"TABLE 4 — {a.n_block} blocks of {a.n_patch} patches, {a.n_perm} permutations, "
      f"seed {a.seed}, guard {a.guard_cells} cells")
print("input: band-limited complex noise — NO SCENE, NO SATELLITE DATA")
print("=" * len(hdr))
print(f"{'':24}{'---- median null ----':>33}{'  ---- 95th pct null ----':>26}")
print(hdr)
print("-" * len(hdr))
for d in rows:
    print(f"{d['arm']:<24}{d['ratio_med']:>8.2f}{d['peak']:>7.2f}"
          f"{100*d['clears5_med']:>9.0f}%{100*d['unpinned']:>9.0f}%{100*d['false_med']:>7.0f}%"
          f"{100*d['clears5_p95']:>9.0f}%{100*d['false_p95']:>7.0f}%")
print("=" * len(hdr))
json.dump(dict(n_block=a.n_block, n_patch=a.n_patch, n_perm=a.n_perm, seed=a.seed,
               guard_cells=a.guard_cells, source=a.obs, arms=rows),
          open(a.out, "w"), indent=1)
print(f"\nsummary -> {a.out}")
