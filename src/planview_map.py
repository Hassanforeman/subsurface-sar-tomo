#!/usr/bin/env python3
"""
planview_map.py — build a PLAN-VIEW map of the tomogram, over a whole scene.

WHY THIS EXISTS
---------------
Biondi's published tomograms show recognisable surface morphology — you can see
the pyramids in them, which is a large part of why the method looks plausible.
Our figures are cross-sections over 24 patches (patch index across, depth down),
which cannot draw a pyramid outline no matter what the pipeline is doing. The two
are not comparable, and a referee is entitled to say so.

This tiles the FULL scene, runs the identical pipeline per tile, and maps a
depth-slice in plan view — the same kind of picture he publishes.

Three outcomes, all worth having:

  * pyramids appear  -> the visual character of his imagery is reproduced by a
    pipeline already shown to be measuring nothing. Strongest possible result.
  * pyramids do not appear -> the difference lies in his undisclosed steps, and
    that can be stated precisely instead of speculated about.
  * something else appears -> a finding.

Outputs, per depth slice, so surface and "depth" can be compared directly:
  1. surface brightness per tile   (what the scene looks like)
  2. tomogram power at the artifact depth (~1.7 cells)
  3. tomogram power at a chosen deeper slice
  4. peak-depth per tile, in cells
  5. per-tile contrast

Usage
-----
  # coarse first — a few minutes
  python3 src/planview_map.py --sicd data/<scene>.nitf --stride 256 --patch 64

  # full resolution — slow, run it once you know the coarse map is sensible
  python3 src/planview_map.py --sicd data/<scene>.nitf --stride 64 --patch 64
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from micromotion import detrend
from tomogram import (DZ_TARGET, steering, analytic1d, metric_depth_axis)
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e


def tile_grid(shape, patch, stride, margin=0):
    rows = range(margin, shape[0] - patch - margin + 1, stride)
    cols = range(margin, shape[1] - patch - margin + 1, stride)
    return list(rows), list(cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sicd", required=True)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--stride", type=int, default=256,
                    help="tile spacing in pixels; smaller = finer map, slower")
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--window", default="hann")
    ap.add_argument("--estimator", default="phasecorr")
    ap.add_argument("--deep-cells", type=float, default=6.0,
                    help="second depth slice to map, in resolution cells")
    ap.add_argument("--max-rows", type=int, default=0,
                    help="limit scene rows read (0 = whole scene)")
    ap.add_argument("--velocity", type=float, default=6000.0)
    ap.add_argument("--f-investigation", type=float, default=22000.0)
    ap.add_argument("--range-km", type=float, default=650.0)
    ap.add_argument("--aperture-km", type=float, default=42.0)
    ap.add_argument("--out")
    args = ap.parse_args()

    import sarpy.io.complex as sicd_io
    rdr = sicd_io.open(args.sicd)
    full = rdr[:, :]
    if args.max_rows:
        full = full[:args.max_rows, :]
    slc_shape = full.shape
    print(f"scene {slc_shape[0]}x{slc_shape[1]}  patch={args.patch}  stride={args.stride}")

    rows, cols = tile_grid(slc_shape, args.patch, args.stride)
    print(f"grid {len(rows)} x {len(cols)} = {len(rows)*len(cols)} tiles")

    zgrid = np.linspace(0, args.n_sub * DZ_TARGET / 2, 300)
    A, _ = steering(args.n_sub, zgrid)
    cells = zgrid / DZ_TARGET
    i_shallow = int(np.argmin(np.abs(cells - 1.7)))
    i_deep = int(np.argmin(np.abs(cells - args.deep_cells)))
    _, dz_phys = metric_depth_axis(np.array([0.0]), args.velocity, args.f_investigation,
                                   args.range_km * 1e3, args.aperture_km * 1e3)
    print(f"dz_phys={dz_phys:.2f} m; mapping slices at "
          f"{cells[i_shallow]:.2f} and {cells[i_deep]:.2f} cells")

    # Sub-aperture decomposition is done ONCE on the whole scene, exactly as the
    # per-patch pipeline does it — the looks are then sampled tile by tile.
    print("decomposing sub-apertures on the full scene ...", flush=True)
    t0 = time.time()
    looks, _ = decompose_subapertures_w(full, n_sub=args.n_sub, overlap=args.overlap,
                                        axis=1, window=args.window,
                                        dtype=np.complex128)
    del full
    print(f"  done in {time.time()-t0:.0f}s; looks {looks.shape}")

    H, W = len(rows), len(cols)
    m_surface = np.zeros((H, W))
    m_shallow = np.zeros((H, W))
    m_deep = np.zeros((H, W))
    m_peak = np.zeros((H, W))
    m_contrast = np.zeros((H, W))

    t0 = time.time()
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            tile = looks[:, r:r + args.patch, c:c + args.patch]
            traj = np.asarray(adjacent_trajectory_e(tile, estimator=args.estimator,
                                                    dtype=np.complex128)[0], dtype=float)
            prof = np.abs(A.conj().T @ analytic1d(detrend(traj, deg=2))) ** 2
            m_surface[i, j] = float(np.mean(np.abs(tile[0])))
            m_shallow[i, j] = float(prof[i_shallow])
            m_deep[i, j] = float(prof[i_deep])
            m_peak[i, j] = float(cells[int(np.argmax(prof))])
            m_contrast[i, j] = float(prof.max() / (np.median(prof) + 1e-30))
        el = time.time() - t0
        done = (i + 1) / H
        print(f"  row {i+1}/{H}  {el:.0f}s elapsed, ~{el/done - el:.0f}s left",
              flush=True)

    label = os.path.basename(args.sicd).split("_SICD")[0]
    out = args.out or f"runs/planview_{label}.png"
    os.makedirs("runs", exist_ok=True)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def show(ax, M, title, log=False):
        V = np.log1p(M) if log else M
        lo, hi = np.percentile(V, [2, 98])
        im = ax.imshow(V, cmap="inferno", vmin=lo, vmax=hi, interpolation="nearest")
        ax.set_title(title, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
        plt.colorbar(im, ax=ax, fraction=0.046)

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    show(axes[0, 0], m_surface, "surface brightness (what the scene looks like)", log=True)
    show(axes[0, 1], m_shallow, f"tomogram power at {cells[i_shallow]:.1f} cells (the artifact)", log=True)
    show(axes[0, 2], m_deep, f"tomogram power at {cells[i_deep]:.1f} cells (deeper slice)", log=True)
    show(axes[1, 0], m_peak, "peak depth per tile (cells)")
    show(axes[1, 1], m_contrast, "per-tile contrast", log=True)
    axes[1, 2].axis("off")
    r = np.corrcoef(m_surface.ravel(), m_shallow.ravel())[0, 1]
    rd = np.corrcoef(m_surface.ravel(), m_deep.ravel())[0, 1]
    axes[1, 2].text(0.02, 0.95,
                    f"scene: {label}\n\n"
                    f"tiles: {H} x {W}\n"
                    f"patch {args.patch} px, stride {args.stride} px\n"
                    f"n_sub {args.n_sub}, overlap {args.overlap}\n\n"
                    f"corr(surface, artifact slice) = {r:+.3f}\n"
                    f"corr(surface, deep slice)     = {rd:+.3f}\n\n"
                    f"peak depth: median {np.median(m_peak):.2f} cells\n"
                    f"            5-95 pct {np.percentile(m_peak,5):.2f}"
                    f" - {np.percentile(m_peak,95):.2f}\n\n"
                    "If surface morphology is visible in a DEPTH slice,\n"
                    "that is surface leakage - evidence against depth\n"
                    "recovery, not for it.",
                    va="top", family="monospace", fontsize=9)
    fig.suptitle(f"Plan-view tomogram map — {label}", fontsize=13)
    fig.tight_layout()
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"\nfigure -> {out}")

    js = out.replace(".png", ".json")
    json.dump(dict(scene=label, patch=args.patch, stride=args.stride,
                   n_sub=args.n_sub, overlap=args.overlap,
                   grid=[H, W], dz_phys=float(dz_phys),
                   slice_cells=[float(cells[i_shallow]), float(cells[i_deep])],
                   corr_surface_artifact=float(r), corr_surface_deep=float(rd),
                   peak_median=float(np.median(m_peak)),
                   peak_p05=float(np.percentile(m_peak, 5)),
                   peak_p95=float(np.percentile(m_peak, 95))),
              open(js, "w"), indent=1)
    print(f"summary -> {js}")
    print(f"\ncorr(surface brightness, artifact-depth power) = {r:+.3f}")
    print(f"corr(surface brightness, deep-slice power)     = {rd:+.3f}")


if __name__ == "__main__":
    main()
