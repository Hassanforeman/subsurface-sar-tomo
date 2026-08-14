#!/usr/bin/env python3
"""
render_sweep.py — can ANY visualisation of the artifact volume look like the
published figures?

WHY THIS EXISTS
---------------
The disclosed method's numbers are reproduced (fixed peak near 1.7 resolution
cells, contrast scaling with trajectory length, exact 1/f depth scaling, noise
reproducing every signature). What is NOT reproduced is the published *appearance*:
vertically extended shafts, conduits and chambers spanning kilometres of depth, at
Giza and at Vesuvius alike.

The 2022 papers document no part of the visualisation pipeline — no renderer, no
isosurface, no threshold, no dynamic range, no colour scale, no depth gain. So the
most economical remaining hypothesis is that the published appearance is produced
by post-processing and rendering choices applied to a volume like the one this
pipeline produces.

That hypothesis is testable, and this script tests it the only honest way: fix the
volume, sweep the rendering, and see whether ANY member of a broad family of
standard visualisation operations turns the artifact into something that looks
like the published figures.

The critical structural fact to defeat is that this pipeline's energy is confined
to roughly 1.5-3 of 300 depth bins. To produce kilometre-deep shafts, a rendering
operation must REDISTRIBUTE ENERGY IN DEPTH. The sweep therefore includes the
operations that could do that:

  - depth gain          compensating the 1/z falloff, which fills the empty deep end
  - per-tile whitening  removing each tile's own scale, so weak tiles look as bright
                        as strong ones
  - common-mode removal subtracting the depth profile shared by all tiles, which is
                        what the surface pin IS
  - log / gamma mapping compressing dynamic range so the deep tail becomes visible
  - z-anisotropic blur  smoothing along depth, which turns blobs into columns
  - z-stretch           plotting depth on an exaggerated axis

Each is a defensible thing an analyst might do. The question is whether any of them,
alone or combined, manufactures architecture out of an empty volume.

If none does, the gap between this reproduction and the published imagery is
evidence that something outside the disclosed method is required — which is a
stronger statement than "I could not reproduce it".

Usage
-----
  python3 src/render_sweep.py --source noise --canvas 768 --stride 24
  python3 src/render_sweep.py --sicd data/<scene>.nitf --stride 128
"""
import argparse, json, os, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, steering, analytic1d
from micromotion import detrend, lrsd_denoise
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e
from volume_render import bandlimited_slc


# ---------------------------------------------------------------- operations
def op_none(V, **k):
    return V

def op_depth_gain(V, power=2.0, **k):
    """Multiply by z^power. An analyst compensating geometric spreading would do
    this; it is also the single most effective way to move energy into the deep
    end of a volume that has none."""
    z = np.arange(V.shape[2], dtype=float)
    return V * (z ** power)[None, None, :]

def op_whiten_tile(V, **k):
    """Divide each tile's profile by its own maximum, so weak tiles are as bright
    as strong ones. Removes all amplitude information; keeps only shape."""
    m = V.max(axis=2, keepdims=True)
    return V / (m + 1e-30)

def op_common_mode(V, **k):
    """Subtract the depth profile shared by every tile. The surface pin IS that
    shared profile, so this is the natural way to 'see past' it."""
    mu = V.mean(axis=(0, 1), keepdims=True)
    return np.clip(V - mu, 0, None)

def op_log(V, **k):
    return np.log10(V / (np.median(V) + 1e-30) + 1.0)

def op_gamma(V, g=0.2, **k):
    Vn = V / (V.max() + 1e-30)
    return Vn ** g

def op_zblur(V, sz=6.0, **k):
    """Smooth along depth only: turns isolated bright voxels into columns."""
    return gaussian_filter(V, sigma=(0.8, 0.8, sz))

OPS = {
    "raw":            [op_none],
    "log":            [op_log],
    "gamma 0.2":      [op_gamma],
    "depth gain z^2": [op_depth_gain],
    "depth gain z^4": [lambda V, **k: op_depth_gain(V, power=4.0)],
    "tile whiten":    [op_whiten_tile],
    "common-mode removed": [op_common_mode],
    "z-blur":         [op_zblur],
    "whiten + log":   [op_whiten_tile, op_log],
    "common-mode + gain z^2": [op_common_mode, op_depth_gain],
    "common-mode + whiten + log": [op_common_mode, op_whiten_tile, op_log],
    "gain z^4 + z-blur + gamma": [lambda V, **k: op_depth_gain(V, power=4.0),
                                  op_zblur, op_gamma],
}


def apply_ops(V, ops):
    out = V.astype(float).copy()
    for f in ops:
        out = f(out)
    return out


# ---------------------------------------------------------------- diagnostics
def vertical_extent(V, pct=99.0):
    """Of the voxels above `pct`, how many depth bins do they span, and what
    fraction of the depth axis is that? A published-looking shaft needs a LARGE
    number. Also returns the median vertical run length per tile column, which is
    what 'a shaft' actually means: contiguous depth extent at one map position."""
    thr = np.percentile(V, pct)
    M = V > thr
    if not M.any():
        return dict(span_frac=0.0, n_bins=0, median_run=0.0, max_run=0, n_vox=0)
    zs = np.where(M.any(axis=(0, 1)))[0]
    runs = []
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            col = M[i, j]
            if not col.any():
                continue
            r, best = 0, 0
            for v in col:
                r = r + 1 if v else 0
                best = max(best, r)
            runs.append(best)
    runs = np.array(runs) if runs else np.array([0])
    return dict(span_frac=float((zs[-1] - zs[0] + 1) / M.shape[2]),
                n_bins=int(len(np.where(M.any(axis=(0, 1)))[0])),
                median_run=float(np.median(runs)), max_run=int(runs.max()),
                n_vox=int(M.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["noise", "sicd"], default="noise")
    ap.add_argument("--sicd")
    ap.add_argument("--canvas", type=int, default=768)
    ap.add_argument("--bw-frac", type=float, default=0.80)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--stride", type=int, default=24)
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--lrsd", action="store_true")
    ap.add_argument("--pct", type=float, default=99.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--out", default="runs/render_sweep.png")
    a = ap.parse_args()

    zgrid = np.linspace(0, a.n_sub * DZ_TARGET / 2, 300)
    A, _ = steering(a.n_sub, zgrid)

    label = (os.path.basename(a.sicd).split("_SICD")[0] if a.sicd
             else f"noise_c{a.canvas}")
    vcache = f"runs/vol_{label}_p{a.patch}_s{a.stride}_n{a.n_sub}{'_lrsd' if a.lrsd else ''}.npy"
    os.makedirs("runs", exist_ok=True)

    if os.path.exists(vcache):
        V = np.load(vcache)
        print(f"loaded cached volume {V.shape} from {vcache}")
    else:
        if a.sicd:
            import sarpy.io.complex as sicd_io
            print(f"loading {a.sicd}")
            img = np.asarray(sicd_io.open(a.sicd)[:, :], dtype=np.complex128)
            if a.max_rows:
                img = img[:a.max_rows, :]
        else:
            print(f"synthesising {a.canvas}x{a.canvas} band-limited speckle — NO SCENE")
            img = bandlimited_slc(a.canvas, a.bw_frac, np.random.default_rng(a.seed))
        print(f"image {img.shape}; decomposing {a.n_sub} sub-apertures ...", flush=True)
        looks, _ = decompose_subapertures_w(img, n_sub=a.n_sub, overlap=a.overlap,
                                            axis=1, window="hann", dtype=np.complex128)
        del img
        H, W = looks.shape[1], looks.shape[2]
        rows = list(range(0, H - a.patch + 1, a.stride))
        cols = list(range(0, W - a.patch + 1, a.stride))
        trajs = np.zeros((len(rows) * len(cols), a.n_sub), dtype=float)
        t0, k = time.time(), 0
        for i, r in enumerate(rows):
            for c in cols:
                trajs[k] = np.asarray(
                    adjacent_trajectory_e(looks[:, r:r+a.patch, c:c+a.patch],
                                          dtype=np.complex128)[0], dtype=float)
                k += 1
            print(f"  row {i+1}/{len(rows)}  {time.time()-t0:.0f}s", flush=True)
        del looks
        obs = np.array([detrend(t, deg=2) for t in trajs], dtype=float)
        if a.lrsd:
            obs, _ = lrsd_denoise(obs)
        V = np.array([np.abs(A.conj().T @ analytic1d(o)) ** 2 for o in obs])
        V = V.reshape(len(rows), len(cols), -1)
        np.save(vcache, V)
        print(f"cached volume {V.shape} -> {vcache}")

    base = vertical_extent(V, a.pct)
    print(f"\nBASELINE (raw volume, top {100-a.pct:.1f}%): depth span "
          f"{100*base['span_frac']:.1f}% of the axis, median vertical run "
          f"{base['median_run']:.0f} bins\n")

    names = list(OPS)
    res = {}
    fig, axes = plt.subplots(3, 4, figsize=(16.5, 11.0), facecolor="black")
    for ax, name in zip(axes.ravel(), names):
        Vt = apply_ops(V, OPS[name])
        d = vertical_extent(Vt, a.pct)
        res[name] = d
        thr = np.percentile(Vt, a.pct)
        # north-south vertical slice through the middle of the volume, the view in
        # which a shaft would be unmistakable
        sl = Vt[:, Vt.shape[1] // 2, :].T
        ax.imshow(sl / (sl.max() + 1e-30), aspect="auto", cmap="inferno",
                  origin="upper", vmin=0, vmax=1)
        ax.set_title(f"{name}\nspan {100*d['span_frac']:.0f}% of depth axis, "
                     f"median run {d['median_run']:.0f} bins",
                     color="white", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("0.4")
    fig.suptitle("Twelve standard visualisation treatments of ONE volume built from "
                 f"{'random numbers — no scene, no satellite data' if not a.sicd else label}\n"
                 "vertical slice through the volume; depth increases downward",
                 color="white", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(a.out, dpi=115, facecolor="black", bbox_inches="tight")
    print(f"figure -> {a.out}")

    w = max(len(n) for n in names) + 2
    print("\n" + "=" * (w + 46))
    print(f"{'treatment':<{w}}{'depth span':>12}{'median run':>13}{'max run':>10}{'voxels':>11}")
    print("-" * (w + 46))
    for n in names:
        d = res[n]
        print(f"{n:<{w}}{100*d['span_frac']:>11.0f}%{d['median_run']:>13.0f}"
              f"{d['max_run']:>10}{d['n_vox']:>11}")
    print("=" * (w + 46))
    print("A published-looking shaft requires a LARGE median vertical run at a fixed")
    print("map position. The depth axis here is 300 bins.")
    json.dump(dict(label=label, source=a.source, pct=a.pct, lrsd=a.lrsd,
                   baseline=base, treatments=res),
              open(a.out.replace(".png", ".json"), "w"), indent=1)


if __name__ == "__main__":
    main()
