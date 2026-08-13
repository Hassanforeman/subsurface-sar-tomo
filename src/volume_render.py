#!/usr/bin/env python3
"""
volume_render.py — build a 3-D tomographic volume and render it the way the
published Giza figures are rendered.

WHY THIS EXISTS
---------------
The published work's public impact is visual: 3-D renderings in which shaft-like
and chamber-like forms appear beneath the plateau. The 2022 paper documents no
part of that visualisation pipeline — no rendering method, no isosurface, no
threshold, no dynamic range, no colour scale. Its 3-D figures (34-50) share one
caption: "Tags association from tomography to 3D model. (a): 3D model of
Khnum-Khufu. (b): Tomographic reconstruction (magnitude)."

Our own figures are 2-D cross-sections over 24 patches, which cannot look like
architecture no matter what the pipeline is doing. That is a plotting difference,
not a physics difference, and it lets the comparison be waved away.

This closes that gap. It tiles a scene (or a synthetic canvas containing NO
SCENE), runs the identical published pipeline per tile, stacks the per-tile depth
profiles into a 3-D volume, thresholds it, and renders it in perspective.

The decisive run is `--source noise`: a 3-D "tomogram" built from random numbers,
with no satellite data of any kind, rendered exactly as a real one would be.
Whatever that picture shows, the method would show for a scene containing nothing.

Thresholding a noisy 3-D volume reliably produces connected filamentary blobs that
human vision reads as designed structure. That is a known perceptual effect, and
it is testable rather than rhetorical.

Usage
-----
  # from random numbers - no data required, runs anywhere
  python3 src/volume_render.py --source noise --canvas 1024 --stride 24

  # from a real scene
  python3 src/volume_render.py --sicd data/<scene>.nitf --stride 128

  # sweep the threshold, since the threshold is undocumented in the original
  python3 src/volume_render.py --source noise --percentiles 90 95 97 99
"""
import argparse, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from micromotion import detrend
from tomogram import DZ_TARGET, steering, analytic1d, metric_depth_axis
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e


def bandlimited_slc(canvas, bw_frac, rng):
    """Complex image whose spectrum is white inside a centred band, zero outside —
    i.e. speckle with realistic resolution-cell correlation, and NO SCENE."""
    if bw_frac >= 1.0:
        return (rng.normal(0, 1, (canvas, canvas))
                + 1j * rng.normal(0, 1, (canvas, canvas))).astype(np.complex128)
    n = max(2, int(round(canvas * bw_frac)))
    spec = np.zeros((canvas, canvas), dtype=np.complex128)
    lo = canvas // 2 - n // 2
    spec[lo:lo + n, lo:lo + n] = (rng.normal(0, 1, (n, n))
                                  + 1j * rng.normal(0, 1, (n, n)))
    img = np.fft.ifft2(np.fft.ifftshift(spec))
    return (img / (np.abs(img).std() + 1e-30)).astype(np.complex128)


def build_volume(looks, patch, stride, A, nz_keep):
    H, W = looks.shape[1], looks.shape[2]
    rows = list(range(0, H - patch + 1, stride))
    cols = list(range(0, W - patch + 1, stride))
    vol = np.zeros((len(rows), len(cols), nz_keep), dtype=float)
    t0 = time.time()
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            tile = looks[:, r:r + patch, c:c + patch]
            traj = np.asarray(adjacent_trajectory_e(tile, dtype=np.complex128)[0],
                              dtype=float)
            prof = np.abs(A.conj().T @ analytic1d(detrend(traj, deg=2))) ** 2
            vol[i, j] = prof[:nz_keep]
        el = time.time() - t0
        frac = (i + 1) / len(rows)
        print(f"  row {i+1}/{len(rows)}  {el:.0f}s, ~{el/frac - el:.0f}s left",
              flush=True)
    return vol, rows, cols


def render_iso(vol, cells, pcts, out, title, subtitle, smooth=1.2):
    """Solid isosurface rendering — the closest match to a CAD/visualisation
    package's output, which is how the published 3-D figures are presented."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from scipy.ndimage import gaussian_filter, zoom
    from skimage import measure

    v = vol / (vol.max() + 1e-30)
    if smooth > 0:
        v = gaussian_filter(v, sigma=(smooth, smooth, smooth * 0.6))
    v = zoom(v, (2, 2, 1), order=1)                 # upsample laterally, as a
    v = v / (v.max() + 1e-30)                       # render package would

    n = len(pcts)
    fig = plt.figure(figsize=(6.0 * n, 6.6), facecolor="black")
    dz = cells[1] - cells[0]

    for k, p in enumerate(pcts):
        thr = float(np.percentile(v, p))
        ax = fig.add_subplot(1, n, k + 1, projection="3d", facecolor="black")
        try:
            verts, faces, _, _ = measure.marching_cubes(v, level=thr)
            verts[:, 2] = verts[:, 2] * dz + cells[0]
            mesh = Poly3DCollection(verts[faces], alpha=0.9)
            depth_c = verts[faces][:, :, 2].mean(axis=1)
            norm = (depth_c - cells[0]) / (cells[-1] - cells[0] + 1e-30)
            mesh.set_facecolor(plt.cm.inferno(1.0 - norm))
            mesh.set_edgecolor("none")
            ax.add_collection3d(mesh)
            ax.set_xlim(0, v.shape[0]); ax.set_ylim(0, v.shape[1])
            ax.set_zlim(cells[0], cells[-1])
        except Exception as e:
            ax.text2D(0.1, 0.5, f"isosurface failed: {e}", color="white")
        ax.set_box_aspect((1, 1, 0.7))
        ax.invert_zaxis()
        ax.set_xlabel("north", color="0.7", fontsize=8)
        ax.set_ylabel("east", color="0.7", fontsize=8)
        ax.set_zlabel("depth (cells)", color="0.7", fontsize=8)
        ax.tick_params(colors="0.5", labelsize=7)
        for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
            pane.pane.set_facecolor("black"); pane.pane.set_alpha(1.0)
        ax.grid(False)
        ax.view_init(elev=18, azim=-58)
        ax.set_title(f"isosurface at top {100-p:g}% of voxels",
                     color="white", fontsize=11)

    fig.suptitle(title, color="white", fontsize=15, y=0.99)
    fig.text(0.5, 0.94, subtitle, color="0.75", fontsize=10, ha="center")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out, dpi=130, facecolor="black", bbox_inches="tight")
    print(f"\nfigure -> {out}")


def render(vol, cells, pcts, out, title, subtitle):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    v = vol / (vol.max() + 1e-30)
    ny, nx, nz = v.shape

    n = len(pcts)
    fig = plt.figure(figsize=(5.2 * n, 11), facecolor="black")

    for k, p in enumerate(pcts):
        thr = np.percentile(v, p)
        m = v >= thr
        yi, xi, zi = np.nonzero(m)
        w = v[m]

        ax = fig.add_subplot(2, n, k + 1, projection="3d", facecolor="black")
        ax.scatter(xi, yi, cells[zi], c=w, cmap="inferno", s=6,
                   alpha=0.55, linewidths=0, vmin=thr, vmax=1.0)
        ax.set_box_aspect((1, 1, 0.75))
        ax.invert_zaxis()
        ax.set_xlabel("east", color="0.7", fontsize=8)
        ax.set_ylabel("north", color="0.7", fontsize=8)
        ax.set_zlabel("depth (cells)", color="0.7", fontsize=8)
        ax.tick_params(colors="0.5", labelsize=7)
        for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
            pane.pane.set_facecolor("black"); pane.pane.set_alpha(1.0)
        ax.grid(False)
        ax.set_title(f"threshold: top {100-p:g}% of voxels",
                     color="white", fontsize=10)

        # maximum-intensity projection, the standard 2-D companion view
        ax2 = fig.add_subplot(2, n, n + k + 1, facecolor="black")
        mip = np.where(m, v, 0).max(axis=0).T      # depth down, east across
        ax2.imshow(mip, cmap="inferno", aspect="auto",
                   extent=[0, nx, cells[nz - 1], cells[0]],
                   vmin=0, vmax=1.0, interpolation="bilinear")
        ax2.set_xlabel("east", color="0.7", fontsize=8)
        ax2.set_ylabel("depth (cells)", color="0.7", fontsize=8)
        ax2.tick_params(colors="0.5", labelsize=7)
        for s in ax2.spines.values():
            s.set_color("0.3")
        ax2.set_title("maximum-intensity projection", color="white", fontsize=9)

    fig.suptitle(title, color="white", fontsize=15, y=0.985)
    fig.text(0.5, 0.955, subtitle, color="0.75", fontsize=10, ha="center")
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    fig.savefig(out, dpi=130, facecolor="black", bbox_inches="tight")
    print(f"\nfigure -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["noise", "sicd"], default="noise")
    ap.add_argument("--sicd")
    ap.add_argument("--canvas", type=int, default=1024,
                    help="synthetic canvas size when --source noise")
    ap.add_argument("--bw-frac", type=float, default=0.80,
                    help="occupied bandwidth of the synthetic speckle")
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--stride", type=int, default=24)
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--window", default="hann")
    ap.add_argument("--iso", action="store_true",
                    help="solid isosurface rendering instead of voxel scatter")
    ap.add_argument("--smooth", type=float, default=1.2,
                    help="gaussian sigma applied before isosurfacing")
    ap.add_argument("--nz-keep", type=int, default=300,
                    help="depth bins to keep (of 300); the deep end is empty")
    ap.add_argument("--percentiles", nargs="*", type=float, default=[95, 98, 99.5])
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out")
    args = ap.parse_args()

    zgrid = np.linspace(0, args.n_sub * DZ_TARGET / 2, 300)
    A, _ = steering(args.n_sub, zgrid)
    cells = zgrid / DZ_TARGET

    if args.source == "noise":
        label = f"noise_c{args.canvas}"
        print(f"synthesising {args.canvas}x{args.canvas} band-limited speckle "
              f"(bw_frac={args.bw_frac}) — NO SCENE, NO SATELLITE DATA")
        img = bandlimited_slc(args.canvas, args.bw_frac,
                              np.random.default_rng(args.seed))
        title = "3-D tomogram built from RANDOM NUMBERS"
        subtitle = ("no satellite data, no scene, no ground — band-limited complex "
                    "noise through the identical published pipeline")
    else:
        if not args.sicd:
            sys.exit("--source sicd requires --sicd")
        import sarpy.io.complex as sicd_io
        label = os.path.basename(args.sicd).split("_SICD")[0]
        print(f"loading {args.sicd}")
        rdr = sicd_io.open(args.sicd)
        img = rdr[:, :]
        if args.max_rows:
            img = img[:args.max_rows, :]
        img = np.asarray(img, dtype=np.complex128)
        title = f"3-D tomogram — {label}"
        subtitle = "real scene through the identical published pipeline"

    print(f"image {img.shape}; decomposing {args.n_sub} sub-apertures ...", flush=True)
    t0 = time.time()
    looks, _ = decompose_subapertures_w(img, n_sub=args.n_sub, overlap=args.overlap,
                                        axis=1, window=args.window,
                                        dtype=np.complex128)
    del img
    print(f"  done in {time.time()-t0:.0f}s; looks {looks.shape}")

    vol, rows, cols = build_volume(looks, args.patch, args.stride, A, args.nz_keep)
    print(f"volume {vol.shape}  (north x east x depth)")

    out = args.out or f"runs/volume_{label}.png"
    os.makedirs("runs", exist_ok=True)
    if args.iso:
        render_iso(vol, cells[:args.nz_keep], args.percentiles, out, title,
                   subtitle, smooth=args.smooth)
    else:
        render(vol, cells[:args.nz_keep], args.percentiles, out, title, subtitle)

    js = out.replace(".png", ".json")
    prof = vol.reshape(-1, vol.shape[2])
    peak_cells = cells[:args.nz_keep][np.argmax(prof, axis=1)]
    json.dump(dict(source=args.source, label=label, shape=list(vol.shape),
                   n_sub=args.n_sub, patch=args.patch, stride=args.stride,
                   percentiles=args.percentiles,
                   peak_cells_median=float(np.median(peak_cells)),
                   peak_cells_p05=float(np.percentile(peak_cells, 5)),
                   peak_cells_p95=float(np.percentile(peak_cells, 95))),
              open(js, "w"), indent=1)
    print(f"summary -> {js}")
    print(f"per-tile peak depth: median {np.median(peak_cells):.2f} cells "
          f"(5-95 pct {np.percentile(peak_cells,5):.2f}"
          f"-{np.percentile(peak_cells,95):.2f})")


if __name__ == "__main__":
    main()
