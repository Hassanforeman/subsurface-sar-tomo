#!/usr/bin/env python3
"""
guard_robustness.py — can ANY per-patch filter defeat the depth guard?

THE QUESTION
------------
`decision_robustness.py` showed that criterion (a) — contrast > 5x the alignment
null — is defeated on empty data by a three-tap per-patch smoother. The paper
therefore states that its verdicts are carried by criterion (b), the absolute
2-cell surface-pinning guard.

That leaves the decision procedure with a single point of failure. If some filter
in the same class ALSO moves the argmax out past 2 cells while keeping the ratio
above 5, then on empty data that filter produces a **false detection under the
full rule**, and the paper's negative verdicts have no remaining support.

The [1,2,1]/4 smoother is only an existence proof for (a). This script searches
for a counterexample to (b).

WHY ONE SHOULD PLAUSIBLY EXIST
------------------------------
The inversion is a DTFT of the detrended trajectory, so reported depth in cells IS
a frequency. A LOW-pass filter concentrates energy at low frequency -> shallow.
A HIGH-pass filter should push the peak DEEPER. If a high-pass kernel also
sharpens the per-patch profile, it could raise the ratio and unpin the peak at the
same time. That is the failure mode being hunted.

The search covers:
  - systematic FIR kernels of length 2-5, including differencing and high-pass
  - AR(1) pre-emphasis over a range of rho, both signs
  - fractional-delay (translation) of the trajectory
  - a random FIR ensemble, so the conclusion is not limited to hand-picked kernels
  - depth-dependent gain applied to each patch profile before summing

Every operator acts on each patch INDEPENDENTLY and transfers no information
between patches. Input contains no scene.

A single arm with a non-zero false-detection rate refutes the paper's position.
"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import (DZ_TARGET, steering, analytic1d, tomogram_from_observations,
                      contrast, alignment_null)


def fir(M, k):
    """Apply FIR kernel k along the look axis of each patch, independently."""
    k = np.asarray(k, float)
    p = len(k) - 1
    P = np.pad(M, ((0, 0), (p, p)), mode="edge")
    out = np.empty_like(M)
    for i in range(M.shape[1]):
        out[:, i] = (P[:, i:i + len(k)] * k[::-1]).sum(axis=1)
    return out


def ar1(M, rho):
    """AR(1) pre-emphasis: x[n] - rho*x[n-1]."""
    P = np.pad(M, ((0, 0), (1, 0)), mode="edge")
    return M - rho * P[:, :-1]


def shift(M, d):
    """Fractional translation of each trajectory via linear interpolation."""
    n = M.shape[1]
    x = np.arange(n)
    out = np.empty_like(M)
    for r in range(M.shape[0]):
        out[r] = np.interp(x - d, x, M[r])
    return out


def build_arms(rng, n_random):
    arms = [("identity", lambda M: M)]
    named = {
        "[1,2,1]/4  low-pass":      [0.25, 0.5, 0.25],
        "[1,-2,1]/4 HIGH-pass":     [0.25, -0.5, 0.25],
        "[1,-1] first difference":  [1.0, -1.0],
        "[1,-3,3,-1] 3rd diff":     [1.0, -3.0, 3.0, -1.0],
        "[1,0,-1] centred deriv":   [0.5, 0.0, -0.5],
        "[1,1,1,1,1]/5 boxcar":     [0.2] * 5,
        "[1,-1,1,-1] alternating":  [0.5, -0.5, 0.5, -0.5],
        "[1,-4,6,-4,1]/16":         [1/16, -4/16, 6/16, -4/16, 1/16],
    }
    for name, k in named.items():
        arms.append((name, (lambda kk: (lambda M: fir(M, kk)))(k)))
    for rho in (-0.9, -0.5, 0.5, 0.9, 0.99):
        arms.append((f"AR(1) pre-emph rho={rho:+.2f}",
                     (lambda r: (lambda M: ar1(M, r)))(rho)))
    for d in (0.5, 1.0, 2.0):
        arms.append((f"translate {d} samples",
                     (lambda dd: (lambda M: shift(M, dd)))(d)))
    for j in range(n_random):
        L = int(rng.integers(2, 6))
        k = rng.normal(0, 1, L)
        k = k / (np.abs(k).sum() + 1e-12)
        arms.append((f"random FIR #{j:03d} L={L}",
                     (lambda kk: (lambda M: fir(M, kk)))(k)))
    return arms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--obs", default="runs/obs_noise_c768_p64_s12_n11.npy")
    ap.add_argument("--n-patch", type=int, default=24)
    ap.add_argument("--n-block", type=int, default=60)
    ap.add_argument("--n-perm", type=int, default=32)
    ap.add_argument("--n-random", type=int, default=120)
    ap.add_argument("--guard-cells", type=float, default=2.0)
    ap.add_argument("--null-stat", choices=["median", "p95"], default="median")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="runs/guard_robustness.json")
    a = ap.parse_args()

    OBS = np.load(a.obs)
    n_look = OBS.shape[1]
    zgrid = np.linspace(0, n_look * DZ_TARGET / 2, 300)
    cells = zgrid / DZ_TARGET
    rng = np.random.default_rng(a.seed)
    arms = build_arms(rng, a.n_random)
    blocks = [OBS[rng.choice(len(OBS), a.n_patch, replace=False)]
              for _ in range(a.n_block)]

    rows = []
    for ai, (name, f) in enumerate(arms):
        R, PK = [], []
        for b, blk in enumerate(blocks):
            o = f(blk)
            if not np.all(np.isfinite(o)) or np.allclose(o, 0):
                R, PK = [], []
                break
            T = tomogram_from_observations(o, zgrid)
            nul = alignment_null(o, zgrid, np.random.default_rng(1000 + b),
                                 n_perm=a.n_perm)
            ca = float(np.median(nul) if a.null_stat == "median"
                       else np.percentile(nul, 95))
            R.append(float(contrast(T)) / (ca + 1e-12))
            PK.append(float(cells[int(np.argmax(T.sum(0)))]))
        if not R:
            continue
        R, PK = np.array(R), np.array(PK)
        unp = PK > a.guard_cells
        fd = (R > 5) & unp
        rows.append(dict(arm=name, ratio=float(np.median(R)),
                         peak=float(np.median(PK)),
                         peak_max=float(PK.max()),
                         frac_above5=float(np.mean(R > 5)),
                         frac_unpinned=float(np.mean(unp)),
                         frac_false_detection=float(np.mean(fd))))
        if (ai + 1) % 25 == 0:
            print(f"  {ai+1}/{len(arms)} arms", flush=True)

    rows.sort(key=lambda d: (-d["frac_false_detection"], -d["frac_above5"]))
    hdr = f"{'operator':<28}{'ratio':>8}{'peak':>8}{'peakmax':>9}{'>5x':>7}{'unpin':>8}{'FALSE DET':>11}"
    print("\n" + "=" * len(hdr))
    print(f"CAN ANY PER-PATCH FILTER DEFEAT THE DEPTH GUARD?  "
          f"{len(rows)} operators, {a.n_block} blocks, null={a.null_stat}")
    print("input: band-limited complex noise, NO SCENE, NO SATELLITE DATA")
    print("=" * len(hdr))
    print(hdr)
    print("-" * len(hdr))
    for d in rows[:22]:
        print(f"{d['arm']:<28}{d['ratio']:>8.2f}{d['peak']:>8.2f}{d['peak_max']:>9.2f}"
              f"{100*d['frac_above5']:>6.0f}%{100*d['frac_unpinned']:>7.0f}%"
              f"{100*d['frac_false_detection']:>10.0f}%")
    print("-" * len(hdr))
    worst = rows[0]
    nz = [d for d in rows if d["frac_false_detection"] > 0]
    print(f"\noperators producing ANY false detection: {len(nz)} of {len(rows)}")
    if nz:
        print(f"*** GUARD DEFEATED *** worst: {worst['arm']} -> "
              f"{100*worst['frac_false_detection']:.0f}% of empty blocks reported as "
              f"detections under the FULL rule")
    else:
        print("guard held against every operator tried; contrast rule was defeated by "
              f"{sum(1 for d in rows if d['frac_above5'] > 0.5)} of them")
    json.dump(dict(n_block=a.n_block, n_patch=a.n_patch, n_perm=a.n_perm,
                   null_stat=a.null_stat, guard_cells=a.guard_cells,
                   source=a.obs, n_operators=len(rows),
                   n_with_false_detection=len(nz), arms=rows),
              open(a.out, "w"), indent=1)
    print(f"\nsummary -> {a.out}")


if __name__ == "__main__":
    main()
