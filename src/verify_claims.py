#!/usr/bin/env python3
"""
verify_claims.py — numerical support for two claims that had none.

An audit found two statements in the paper with no file behind them:

  1. section 5.2: "direct evaluation agrees with the reference implementation to
     one part in 10^13". Asserted, never measured.
  2. section 5.5: the pure synthetic random-walk rank sweep "(1, 19, 78, 141, 208)",
     the control showing the rank behaviour owes nothing to SAR. Run inline once
     and never written down.

This script measures both and writes runs/verify_claims.json.
"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from micromotion import detrend
from tomogram import DZ_TARGET, steering, analytic1d

out = {}

# ---- 1. is the inverter a DTFT of the analytic residual, evaluated on the grid? ----
# invert_patch computes |A^H . analytic1d(r)|^2. Evaluate the same quantity directly
# from the definition and compare.
rng = np.random.default_rng(0)
worst = 0.0
for n_look in (11, 24, 64, 128):
    zgrid = np.linspace(0, n_look * DZ_TARGET / 2, 300)
    A, Kz = steering(n_look, zgrid)
    for _ in range(20):
        r = rng.normal(0, 1, n_look)
        r = detrend(r, deg=2)
        pipeline = np.abs(A.conj().T @ analytic1d(r)) ** 2
        # Direct evaluation from the definition. A[l, j] = exp(i Kz[l] z[j]) with
        # Kz[l] = l * 2pi/(n_look * DZ). So (A^H x)[j] = sum_l x[l] exp(-i Kz[l] z[j])
        # -- a discrete-time Fourier transform of the analytic residual sampled at
        # the frequency z[j] * 2pi/(n_look * DZ), evaluated on the depth grid.
        z_an = analytic1d(r)
        dKz = 2 * np.pi / (n_look * DZ_TARGET)
        ell = np.arange(n_look)
        direct = np.array([abs(np.sum(z_an * np.exp(-1j * dKz * ell * zg))) ** 2
                           for zg in zgrid])
        rel = np.abs(pipeline - direct).max() / (np.abs(direct).max() + 1e-300)
        worst = max(worst, float(rel))
out["dtft_identity_worst_relative_error"] = worst
print(f"[1] inverter vs direct DTFT evaluation")
print(f"    worst relative error over 80 trials, n_look in (11,24,64,128): {worst:.3e}")
print(f"    -> agreement to about one part in 10^{-np.log10(worst):.0f}")

# ---- 2. pure synthetic random walks: the rank sweep with no SAR pipeline ----
zg = np.linspace(0, 11 * DZ_TARGET / 2, 300)
A11, _ = steering(11, zg)
cells = zg / DZ_TARGET
W = np.cumsum(np.random.default_rng(0).normal(0, 1, (3481, 11)), axis=1)
M = np.array([detrend(x, deg=2) for x in W])
U, sv, Vt = np.linalg.svd(M, full_matrices=False)
en = (sv ** 2) / (sv ** 2).sum()
cum = np.cumsum(en)
sweep = []
for r in (1, 2, 3, 5, 8):
    m = (U[:, :r] * sv[:r]) @ Vt[:r]
    prof = np.abs(A11.conj().T @ np.array([analytic1d(o) for o in m]).T) ** 2
    pk = cells[np.argmax(prof, axis=0)]
    sweep.append(dict(rank=r, variance_kept=float(cum[r - 1]),
                      n_distinct_depths=int(len(np.unique(pk))),
                      median_cells=float(np.median(pk))))
out["pure_walk_rank_sweep"] = sweep
print(f"\n[2] pure synthetic random walks - no image, no sub-apertures, no SAR pipeline")
print(f"    {'rank':>5}{'var kept':>11}{'#depths':>10}{'median':>9}")
for d in sweep:
    print(f"    {d['rank']:>5}{100*d['variance_kept']:>10.1f}%{d['n_distinct_depths']:>10}"
          f"{d['median_cells']:>9.2f}")
print(f"    distinct-depth tuple: ({', '.join(str(d['n_distinct_depths']) for d in sweep)})")

json.dump(out, open("runs/verify_claims.json", "w"), indent=1)
print("\nsummary -> runs/verify_claims.json")
