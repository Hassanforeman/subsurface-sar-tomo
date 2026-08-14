#!/usr/bin/env python3
"""
decision_robustness.py — how safe is this paper's own decision statistic?

THE RULE UNDER TEST
-------------------
Every verdict in this paper rests on two criteria applied together:

    (a) contrast(T) > 5 x contrast(alignment null)      "above null"
    (b) peak depth within 2 resolution cells of the surface   "surface-pinned"

Criterion (a) alone is the kind of confidence figure the published work reports.
Criterion (b) is this paper's addition.

The alignment null preserves each patch's depth profile EXACTLY and randomises
only whether patches agree on a depth. That makes it invariant to *where* each
patch peaks. So any operation that sharpens each patch's own depth profile —
without transferring one bit of information between patches — raises the
numerator and leaves the denominator alone.

THE EXPERIMENT
--------------
Take an input containing NO SCENE: band-limited complex noise, no satellite data,
tiled and pushed through the identical pipeline. Draw independent 24-patch blocks
— the analysis geometry used for every site in this paper — and score each block
under four preprocessing arms:

  none                 the pipeline as run everywhere else in this paper
  LRSD default         the authors' own low-rank/sparse denoising step
  [1,2,1]/4 smoother   a three-tap per-patch low-pass filter. Acts on each patch
                       INDEPENDENTLY. Transfers no information between patches.
                       As innocuous a preprocessing step as exists.
  per-patch rescale    each patch multiplied by its own random constant. A
                       depth-neutral control: changes amplitudes, not profiles.

If the trivially benign smoother clears the 5x rule on empty data, then criterion
(a) is not a safe detection statistic, and the verdicts in this paper are carried
by criterion (b). That is a limitation of this paper's method, reported here.
"""
import argparse, json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from micromotion import lrsd_denoise
from tomogram import (DZ_TARGET, tomogram_from_observations, contrast,
                      alignment_null, pinned_absolute, metric_depth_axis)


def smooth121(M):
    P = np.pad(M, ((0, 0), (1, 1)), mode="edge")
    return 0.25 * P[:, :-2] + 0.5 * P[:, 1:-1] + 0.25 * P[:, 2:]


ARMS = [("none",               lambda B, r: B),
        ("LRSD default",       lambda B, r: lrsd_denoise(B)[0]),
        ("[1,2,1]/4 smoother", lambda B, r: smooth121(B)),
        ("per-patch rescale",  lambda B, r: B * r.uniform(0.5, 2.0, (B.shape[0], 1)))]

ap = argparse.ArgumentParser()
ap.add_argument("--obs", default="runs/obs_noise_c768_p64_s12_n11.npy")
ap.add_argument("--n-patch", type=int, default=24)
ap.add_argument("--n-block", type=int, default=200)
ap.add_argument("--n-perm", type=int, default=64)
ap.add_argument("--guard-cells", type=float, default=2.0)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--out", default="runs/decision_robustness.json")
a = ap.parse_args()

OBS = np.load(a.obs)
n_look = OBS.shape[1]
zgrid = np.linspace(0, n_look * DZ_TARGET / 2, 300)
cells = zgrid / DZ_TARGET
rng = np.random.default_rng(a.seed)

# how much of each block does the LRSD step actually remove? (block-level, which is
# the operator the experiment applies — its threshold depends on matrix shape)
rem, lead0, lead1, ranks = [], [], [], []

rows = []
for b in range(a.n_block):
    blk = OBS[rng.choice(len(OBS), a.n_patch, replace=False)]
    rec = {}
    for tag, f in ARMS:
        o = f(blk, np.random.default_rng(5000 + b))
        if tag == "LRSD default":
            rem.append(float(np.linalg.norm(o - blk) / np.linalg.norm(blk)))
            for X, acc in ((blk, lead0), (o, lead1)):
                sv = np.linalg.svd(X, compute_uv=False)
                acc.append(float(sv[0] ** 2 / (sv ** 2).sum()))
            ranks.append(int(np.linalg.matrix_rank(o, tol=1e-8)))
        T = tomogram_from_observations(o, zgrid)
        c = float(contrast(T))
        ca = float(np.median(alignment_null(o, zgrid, np.random.default_rng(1000 + b),
                                            n_perm=a.n_perm)))
        pk = float(cells[int(np.argmax(T.sum(0)))])
        rec[tag] = dict(contrast=c, align=ca, ratio=c / (ca + 1e-12), peak_cells=pk,
                        pinned=bool(pk <= a.guard_cells))
    rows.append(rec)
    if (b + 1) % 25 == 0:
        print(f"  {b+1}/{a.n_block} blocks", flush=True)


def col(tag, k):
    return np.array([r[tag][k] for r in rows])


print("\n" + "=" * 92)
print(f"IS THE 5x CONTRAST RULE SAFE?  {a.n_block} blocks of {a.n_patch} patches, "
      f"{n_look} looks")
print(f"input: {os.path.basename(a.obs)} — band-limited complex noise, NO SCENE, "
      f"NO SATELLITE DATA")
print("=" * 92)
print(f"{'preprocessing arm':<22}{'contrast':>10}{'null':>8}{'RATIO':>9}"
      f"{'clears 5x':>11}{'peak':>8}{'pinned':>9}{'DETECTED':>11}")
print("-" * 92)
for tag, _ in ARMS:
    r = col(tag, "ratio")
    pin = col(tag, "pinned")
    det = (r > 5) & (~pin.astype(bool))
    print(f"{tag:<22}{np.median(col(tag,'contrast')):>10.2f}"
          f"{np.median(col(tag,'align')):>8.2f}{np.median(r):>9.2f}"
          f"{f'{100*np.mean(r>5):.0f}%':>11}{np.median(col(tag,'peak_cells')):>8.2f}"
          f"{f'{100*np.mean(pin):.0f}%':>9}{f'{100*np.mean(det):.0f}%':>11}")
print("=" * 92)
print("'clears 5x' = would be reported as above-null on data containing nothing.")
print("'pinned'    = caught by this paper's absolute 2-cell surface guard.")
print("'DETECTED'  = clears 5x AND escapes the guard: a false detection under this")
print("              paper's full rule. The guard is what stands between the two.")
print(f"\nLRSD at block level ({a.n_patch}x{n_look}): removes "
      f"{100*np.median(rem):.1f}% of the block by norm "
      f"(range {100*np.min(rem):.0f}-{100*np.max(rem):.0f}%); leading component "
      f"{100*np.median(lead0):.1f}% -> {100*np.median(lead1):.1f}%; output rank "
      f"{np.median(ranks):.0f} of {min(a.n_patch, n_look)} "
      f"(rank fell below input rank in {100*np.mean(np.array(ranks) < 8):.0f}% of blocks).")

json.dump(dict(n_block=a.n_block, n_patch=a.n_patch, n_perm=a.n_perm, source=a.obs,
               guard_cells=a.guard_cells,
               arms={tag: dict(
                   median={k: float(np.median(col(tag, k)))
                           for k in ("contrast", "align", "ratio", "peak_cells")},
                   frac_above_5x=float(np.mean(col(tag, "ratio") > 5)),
                   frac_pinned=float(np.mean(col(tag, "pinned"))),
                   frac_false_detection=float(np.mean((col(tag, "ratio") > 5) &
                                                      (~col(tag, "pinned").astype(bool)))))
                     for tag, _ in ARMS},
               lrsd_block_level=dict(removed_median=float(np.median(rem)),
                                     removed_min=float(np.min(rem)),
                                     removed_max=float(np.max(rem)),
                                     leading_before=float(np.median(lead0)),
                                     leading_after=float(np.median(lead1)),
                                     rank_median=float(np.median(ranks)),
                                     frac_rank_below_8=float(np.mean(np.array(ranks) < 8))),
               blocks=rows), open(a.out, "w"), indent=1)
print(f"\nsummary -> {a.out}")
