#!/usr/bin/env python3
"""
shape_metric.py — a pre-registered discriminator for "does this volume contain
shaft-like architecture?", and the reason it must be scored against a matched null.

WHY THIS EXISTS
---------------
Section 7 reports that a common-mode-subtraction rendering of a volume built from
random numbers produces "discrete, vertically elongated bodies", then declines to
say whether they resemble the published figures, because "looks like" from one
pair of eyes is the failure mode this paper accuses the original work of. Settling
it needs a statistic fixed in advance.

WHAT HAPPENED WHEN THAT WAS TRIED
---------------------------------
The first design calibrated an ABSOLUTE threshold on two synthetic controls:
isotropically-smoothed Gaussian noise as the negative, synthetic shafts and
chambers as the positive. It separated them perfectly (0/5 and 5/5).

Applied to the real thing it classified **9 of 12 renderings of an EMPTY pipeline
volume as architecture-like — including the raw volume with no rendering at all.**

The rule was not wrong about those volumes; the calibration was against the wrong
null. A tomogram's depth axis is a DTFT of a smooth accumulated trajectory, so
every tile's profile is smooth in depth BY CONSTRUCTION. Above-threshold voxels
therefore form long vertical runs whether or not anything is there. Isotropically
smoothed noise has no such property, so it is not the right negative control.

This is the paper's own central result turned on the paper: an absolute threshold
is not a detection rule. The null has to be matched.

THE CORRECTED DESIGN
--------------------
Score every statistic on TWO volumes processed identically - same pipeline, same
rendering, same threshold - differing only in whether a structure was planted:

    negative : the pipeline run on an input containing no scene
    positive : the same volume with vertical shafts planted into it

and report the SEPARATION, not an absolute value. A statistic that cannot separate
those two cannot settle section 7 either.

Run:  python3 src/shape_metric.py
"""
import json, os, sys
import numpy as np
from scipy.ndimage import gaussian_filter, label

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PCT = 99.0
VOL = "runs/vol_noise_c768_p64_s24_n11.npy"


def stats(vol, pct=PCT):
    """vrun: median contiguous depth extent at a map position.
       elong: median z-extent / horizontal extent of connected components.
       ncomp: number of connected components (architecture is few and large).
       span: fraction of the depth axis occupied."""
    thr = np.percentile(vol, pct)
    M = vol > thr
    if not M.any():
        return dict(vrun=0.0, elong=0.0, ncomp=0, span=0.0, n_vox=0)
    runs = []
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            col = M[i, j]
            if not col.any():
                continue
            best = r = 0
            for v in col:
                r = r + 1 if v else 0
                best = max(best, r)
            runs.append(best)
    lab, n = label(M)
    el = []
    for k in range(1, n + 1):
        idx = np.argwhere(lab == k)
        if len(idx) < 8:
            continue
        el.append((np.ptp(idx[:, 2]) + 1) / (max(np.ptp(idx[:, 0]), np.ptp(idx[:, 1])) + 1))
    zs = np.where(M.any(axis=(0, 1)))[0]
    return dict(vrun=float(np.median(runs)) if runs else 0.0,
                elong=float(np.median(el)) if el else 0.0,
                ncomp=int(n), span=float((zs[-1] - zs[0] + 1) / M.shape[2]),
                n_vox=int(M.sum()))


def plant_shafts(vol, n_shaft=4, amp=6.0, seed=11):
    """Plant vertical shafts into an existing volume, so the positive and negative
    differ ONLY in the planted structure."""
    rng = np.random.default_rng(seed)
    v = vol.copy()
    nx, ny, nz = v.shape
    s = np.median(v) + amp * (np.percentile(v, 99) - np.median(v))
    for _ in range(n_shaft):
        cx, cy = rng.integers(3, nx - 3), rng.integers(3, ny - 3)
        z0, z1 = rng.integers(20, 80), rng.integers(200, nz - 10)
        v[cx:cx + 2, cy:cy + 2, z0:z1] += s
    return v


if not os.path.exists(VOL):
    sys.exit(f"{VOL} not present - run src/render_sweep.py first")

from render_sweep import OPS, apply_ops

V = np.load(VOL)
VP = plant_shafts(V)
print(f"volume {V.shape} from an input containing no scene; positive arm is the same "
      f"volume with 4 shafts planted\n")

hdr = (f"{'rendering treatment':<28}{'vrun-':>8}{'vrun+':>8}{'x':>6}"
       f"{'ncomp-':>8}{'ncomp+':>8}{'x':>7}{'separates':>11}")
print("=" * len(hdr))
print("MATCHED-NULL SHAPE TEST  ('-' = empty arm, '+' = planted arm)")
print("=" * len(hdr))
print(hdr)
print("-" * len(hdr))
res = {}
for name in OPS:
    de, dp = stats(apply_ops(V, OPS[name])), stats(apply_ops(VP, OPS[name]))
    rv = dp["vrun"] / (de["vrun"] + 1e-9)
    rc = de["ncomp"] / (dp["ncomp"] + 1e-9)
    sep = rv > 1.5 or rc > 2.0
    res[name] = dict(empty=de, planted=dp, vrun_ratio=float(rv),
                     ncomp_ratio=float(rc), separates=bool(sep))
    print(f"{name:<28}{de['vrun']:>8.0f}{dp['vrun']:>8.0f}{rv:>6.1f}"
          f"{de['ncomp']:>8}{dp['ncomp']:>8}{rc:>7.1f}{'YES' if sep else 'no':>11}")
print("=" * len(hdr))
ok = sum(1 for v in res.values() if v["separates"])
print(f"\n{ok} of {len(res)} treatments separate a planted volume from an empty one.")
print("For those treatments the statistic is usable; for the rest it is not.")
print("\nPRE-REGISTERED RULE for section 7, fixed here before any published figure is")
print("scored again: a real volume is called architecture-like only if its vrun exceeds")
print("1.5x, or its component count falls below half, that of a PIPELINE-MATCHED volume")
print("built from an input containing no scene, under the identical rendering treatment.")
print("No absolute threshold is used, because an absolute threshold classified 9 of 12")
print("renderings of an empty volume as architecture-like.")

json.dump(dict(pct=PCT, volume=VOL, n_shaft=4, amp=6.0,
               rule="vrun_ratio > 1.5 OR ncomp_ratio > 2.0, against a pipeline-matched "
                    "empty volume under the identical treatment",
               treatments=res),
          open("runs/shape_metric.json", "w"), indent=1)
print("\nresults -> runs/shape_metric.json")
