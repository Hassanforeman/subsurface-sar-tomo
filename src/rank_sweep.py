#!/usr/bin/env python3
"""
rank_sweep.py — how much spatial coherence does the low-rank step manufacture?

WHY THIS EXISTS
---------------
`tomogram.py` applies

    obs, _ = lrsd_denoise(obs)          # obs is (n_patch, n_look)

before inversion, following the published method. `lrsd_denoise` returns the
LOW-RANK component of the patch-by-look matrix. "Low rank across the patch axis"
means "keep only what many patches have in common". Applied to a stack of
INDEPENDENT per-tile random walks, the truncated SVD keeps the dominant shared
mode and hands it to every tile. Every tile then inverts to the same depth.

That is a mechanism for converting independent noise into a spatially coherent
horizontal layer, using nothing but a documented step of the published method.

The regularisation parameter of the LRSD step is not disclosed in any published
source, and at its library default it barely truncates (rank 8 of 11 on this
data). This script sweeps the effective rank directly so the dependence is
visible rather than hidden inside an undisclosed hyperparameter.

The input contains NO SCENE: band-limited complex noise, no satellite data.
Whatever coherence appears in the output was manufactured by the operator.

Usage
-----
  python3 src/rank_sweep.py                       # noise canvas, cached
  python3 src/rank_sweep.py --sicd data/<x>.nitf  # same sweep on a real scene
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from micromotion import detrend, lrsd_denoise
from tomogram import DZ_TARGET, steering, analytic1d
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e
from volume_render import bandlimited_slc


def collect_obs(looks, patch, stride, n_look):
    """Per-tile detrended trajectories: the matrix the low-rank step acts on."""
    H, W = looks.shape[1], looks.shape[2]
    rows = list(range(0, H - patch + 1, stride))
    cols = list(range(0, W - patch + 1, stride))
    trajs = np.zeros((len(rows) * len(cols), n_look), dtype=float)
    t0, k = time.time(), 0
    for i, r in enumerate(rows):
        for c in cols:
            tile = looks[:, r:r + patch, c:c + patch]
            trajs[k] = np.asarray(adjacent_trajectory_e(tile, dtype=np.complex128)[0],
                                  dtype=float)
            k += 1
        el = time.time() - t0
        print(f"  row {i+1}/{len(rows)}  {el:.0f}s, ~{el/((i+1)/len(rows)) - el:.0f}s left",
              flush=True)
    return np.array([detrend(t, deg=2) for t in trajs], dtype=float), len(rows), len(cols)


def stats(obs, A, cells, tag, kept=None):
    prof = np.abs(A.conj().T @ np.array([analytic1d(o) for o in obs]).T) ** 2
    peak = cells[np.argmax(prof, axis=0)]
    med = float(np.median(peak))
    # spatial coherence: what fraction of tiles land in the same depth bin as the median
    same = float(np.mean(np.abs(peak - med) < 1e-9))
    return dict(arm=tag, kept_variance=kept, n_tiles=int(len(peak)),
                peak_median=med, peak_p05=float(np.percentile(peak, 5)),
                peak_p95=float(np.percentile(peak, 95)),
                peak_std=float(np.std(peak)),
                n_distinct_depths=int(len(np.unique(peak))),
                frac_at_median=same)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sicd")
    ap.add_argument("--canvas", type=int, default=768)
    ap.add_argument("--bw-frac", type=float, default=0.80)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--stride", type=int, default=12)
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--ranks", nargs="*", type=int, default=[1, 2, 3, 5, 8, 11])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--out", default="runs/rank_sweep.json")
    args = ap.parse_args()

    zgrid = np.linspace(0, args.n_sub * DZ_TARGET / 2, 300)
    A, _ = steering(args.n_sub, zgrid)
    cells = zgrid / DZ_TARGET

    label = (os.path.basename(args.sicd).split("_SICD")[0] if args.sicd
             else f"noise_c{args.canvas}")
    cache = f"runs/obs_{label}_p{args.patch}_s{args.stride}_n{args.n_sub}.npy"
    os.makedirs("runs", exist_ok=True)

    if os.path.exists(cache):
        obs0 = np.load(cache)
        print(f"loaded cached trajectories {obs0.shape} from {cache}")
    else:
        if args.sicd:
            import sarpy.io.complex as sicd_io
            print(f"loading {args.sicd}")
            img = np.asarray(sicd_io.open(args.sicd)[:, :], dtype=np.complex128)
            if args.max_rows:
                img = img[:args.max_rows, :]
        else:
            print(f"synthesising {args.canvas}x{args.canvas} band-limited speckle "
                  f"(bw_frac={args.bw_frac}) — NO SCENE, NO SATELLITE DATA")
            img = bandlimited_slc(args.canvas, args.bw_frac,
                                  np.random.default_rng(args.seed))
        print(f"image {img.shape}; decomposing {args.n_sub} sub-apertures ...", flush=True)
        looks, _ = decompose_subapertures_w(img, n_sub=args.n_sub, overlap=args.overlap,
                                            axis=1, window="hann", dtype=np.complex128)
        del img
        obs0, nr, nc = collect_obs(looks, args.patch, args.stride, A.shape[0])
        del looks
        np.save(cache, obs0)
        print(f"cached trajectories -> {cache}  ({nr}x{nc} tiles)")

    rows = [stats(obs0, A, cells, "no low-rank step (published pipeline as run here)")]

    U, sv, Vt = np.linalg.svd(obs0, full_matrices=False)
    tot = float((sv ** 2).sum())
    for r in args.ranks:
        if r > len(sv):
            continue
        kept = float((sv[:r] ** 2).sum() / tot)
        rows.append(stats((U[:, :r] * sv[:r]) @ Vt[:r], A, cells,
                          f"truncated to rank {r}", kept=kept))

    print("\n  applying LRSD at its library default ...", flush=True)
    lo, _ = lrsd_denoise(obs0)
    rows.append(stats(lo, A, cells,
                      f"LRSD default (effective rank "
                      f"{int(np.linalg.matrix_rank(lo, tol=1e-8))} of {min(lo.shape)})"))

    hdr = f"{'arm':<52}{'var%':>7}{'median':>9}{'5-95 pct':>16}{'std':>7}{'#depths':>9}{'%@med':>8}"
    print("\n" + "=" * len(hdr))
    print(f"RANK SWEEP — {label}, {rows[0]['n_tiles']} tiles, {args.n_sub} looks")
    print("=" * len(hdr))
    print(hdr)
    print("-" * len(hdr))
    for d in rows:
        kv = f"{100*d['kept_variance']:.1f}" if d['kept_variance'] is not None else "—"
        print(f"{d['arm']:<52}{kv:>7}{d['peak_median']:>9.2f}"
              f"{d['peak_p05']:>8.2f}-{d['peak_p95']:<8.2f}{d['peak_std']:>7.2f}"
              f"{d['n_distinct_depths']:>9}{100*d['frac_at_median']:>7.0f}%")
    print("=" * len(hdr))
    print("\n'#depths' is how many DISTINCT depth bins the tiles report, of 300 available.")
    print("'%@med' is the share of tiles reporting exactly the median depth.")
    print("A perfectly flat continuous layer is #depths = 1 and %@med = 100.")

    json.dump(dict(label=label, source="sicd" if args.sicd else "noise",
                   n_sub=args.n_sub, patch=args.patch, stride=args.stride,
                   singular_value_energy=[float(s**2/tot) for s in sv],
                   arms=rows), open(args.out, "w"), indent=1)
    print(f"\nsummary -> {args.out}")


if __name__ == "__main__":
    main()
