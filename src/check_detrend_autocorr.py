"""
Does the degree-2 detrend remove the look-to-look smoothness?

WHY THIS EXISTS
---------------
The erratum sent to the PCI Archaeo recommender on 29 July 2026 justifies
replacing the shuffle null on the grounds that shuffling "destroys the
look-to-look smoothness that 80% spectral overlap guarantees even under pure
noise."

E6 (31 July) measured the lag-1 autocorrelation of the trajectories that
actually enter the inverter as **0.009** — effectively zero. Those trajectories
have had a degree-2 polynomial removed (`detrend(traj, deg=2)` in
`patch_observations_cfg`), and a degree-2 fit removes 3 of only ~11 degrees of
freedom, precisely from the smooth low-frequency end where overlap-induced
correlation would live.

So the justification in the erratum may be correct about the *raw* trajectories
and simply not about the detrended residuals. This script settles it.

WHAT IT REPORTS
---------------
Lag-1/2/3 autocorrelation for the same trajectories at three stages:
raw, degree-1 detrended, degree-2 detrended (what the pipeline uses).

Plus the same three for synthetic white noise pushed through the identical
detrending, because a degree-2 fit on a short series induces negative
correlation *by itself* — without that reference the real numbers cannot be
interpreted.

READING THE RESULT
------------------
raw high, deg-2 ~0, and noise-deg-2 ~ the same as real-deg-2
    -> the smoothness is real, the detrend removes it, and the erratum's
       claim is defensible with one clarifying phrase.

raw also ~0
    -> the overlap does NOT produce measurable look-to-look smoothness here,
       and the erratum's stated rationale must be rewritten. The alignment
       null may still be the right choice, but for the other reason: it
       preserves each patch's depth profile and randomises only cross-patch
       agreement.

    python3 src/check_detrend_autocorr.py --sicd data/<scene>.nitf
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from micromotion import detrend
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e


def autocorr(x, max_lag=3):
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    d = float(x @ x)
    if d <= 0:
        return [float("nan")] * max_lag
    return [float(x[:-k] @ x[k:]) / d for k in range(1, max_lag + 1)]


def mean_autocorr(rows, max_lag=3):
    acc = np.zeros(max_lag)
    n = 0
    for r in rows:
        a = autocorr(r, max_lag)
        if not np.any(np.isnan(a)):
            acc += a
            n += 1
    return acc / max(n, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sicd", required=True)
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--n-patch", type=int, default=24)
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--window", default="hann")
    ap.add_argument("--estimator", default="phasecorr")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    from sarpy.io.complex.converter import open_complex
    reader = open_complex(args.sicd)
    R, C = reader.data_size
    crop = min(args.crop, R, C)
    r0, c0 = R // 2 - crop // 2, C // 2 - crop // 2
    label = os.path.basename(args.sicd)
    print(f"Loading {crop}x{crop} crop from {label} ({R}x{C})")
    slc = reader[r0:r0 + crop, c0:c0 + crop]

    looks, _ = decompose_subapertures_w(slc, n_sub=args.n_sub, overlap=args.overlap,
                                        axis=1, window=args.window,
                                        dtype=np.complex128)
    H, W = slc.shape
    row = H // 2 - args.patch // 2
    cols = np.linspace(0, W - args.patch, args.n_patch).astype(int)

    raw = []
    for cc in cols:
        lp = looks[:, row:row + args.patch, cc:cc + args.patch]
        traj, _ = adjacent_trajectory_e(lp, estimator=args.estimator,
                                        dtype=np.complex128)
        raw.append(np.asarray(traj, dtype=float))
    raw = np.array(raw)

    d1 = np.array([detrend(t, deg=1) for t in raw])
    d2 = np.array([detrend(t, deg=2) for t in raw])

    rng = np.random.default_rng(args.seed)
    wn = rng.normal(0.0, 1.0, raw.shape)
    wn1 = np.array([detrend(t, deg=1) for t in wn])
    wn2 = np.array([detrend(t, deg=2) for t in wn])

    print(f"\n{'='*78}")
    print(f"Does the degree-2 detrend remove look-to-look smoothness? — {label}")
    print(f"  n_sub={args.n_sub} (trajectory length {raw.shape[1]}), "
          f"overlap={args.overlap}, patches={len(cols)}")
    print(f"{'='*78}")
    print(f"{'series':<34}{'lag-1':>12}{'lag-2':>12}{'lag-3':>12}")
    print("-" * 78)
    for name, arr in (("REAL raw trajectory", raw),
                      ("REAL detrended deg-1", d1),
                      ("REAL detrended deg-2  <-- used", d2),
                      ("white noise raw", wn),
                      ("white noise detrended deg-1", wn1),
                      ("white noise detrended deg-2", wn2)):
        a = mean_autocorr(arr)
        print(f"{name:<34}{a[0]:>12.3f}{a[1]:>12.3f}{a[2]:>12.3f}")
    print("-" * 78)

    r_raw = mean_autocorr(raw)[0]
    r_d2 = mean_autocorr(d2)[0]
    n_d2 = mean_autocorr(wn2)[0]
    print(f"\nraw lag-1 = {r_raw:.3f};  after deg-2 detrend = {r_d2:.3f};  "
          f"white noise after the same detrend = {n_d2:.3f}")
    if r_raw > 0.2 and abs(r_d2 - n_d2) < 0.1:
        print("\n  -> The smoothness IS present in the raw trajectories and is removed by")
        print("     the degree-2 detrend. The erratum's rationale is defensible, but must")
        print("     say 'in the raw trajectories' explicitly.")
    elif r_raw <= 0.2:
        print("\n  -> The raw trajectories are NOT measurably smooth. The erratum's stated")
        print("     rationale does not hold and must be rewritten. Justify the alignment")
        print("     null by what it actually does: preserve each patch's depth profile and")
        print("     randomise only cross-patch agreement.")
    else:
        print("\n  -> Mixed: inspect the table by hand before writing anything.")


if __name__ == "__main__":
    main()
