#!/usr/bin/env python3
"""
shape_metric_giza.py — PREREGISTRATION Part C.4 step 1: apply the pre-registered §7
shape rule to the REAL Giza volumes, against a pipeline-matched empty volume.

Pre-registration: docs/PREREGISTRATION_MINES_AND_GRANSASSO.md, Part C (rule fixed
16 Aug 2026; calibration runs/shape_metric.json). C.4 says step 1 was "not yet run —
requires the SICD". The three free Giza SICDs are now in data/.

ANALYSIS CHOICES THE PRE-REGISTRATION DID NOT SPECIFY — fixed in this file, 26 Sep
2026, BEFORE any Giza volume has been built or scored:

  PRIMARY (the result that is reported as the C.5 outcome)
  - Scenes: all three free Umbra Giza SICDs. 2023-03-08 U04 is the pre-registered
    primary Giza scene; all three are reported, none is dropped.
  - Real volume: 768 x 768 CENTRE crop of each SICD (centre crops are the convention
    throughout the paper), built with parameters IDENTICAL to the calibration volume
    runs/vol_noise_c768_p64_s24_n11.npy: n_sub 11, overlap 0.8, Hann sub-aperture
    taper, complex128, patch 64, stride 24 (-> 30 x 30 tiles), no LRSD, degree-2
    detrend, 300 depth bins, Bartlett/DFT inversion.
  - Null: the calibration's empty volume — band-limited complex speckle, 768 x 768,
    bw_frac 0.80, seed 0, through the identical pipeline.
  - Treatments: the 8 of 12 NOT excluded in advance in C.3 (excluded: tile whiten,
    whiten + log, common-mode + whiten + log, depth gain z^4).
  - Rule per treatment (verbatim C.2): architecture-like iff vrun_real > 1.5 x vrun_null
    OR ncomp_real < 0.5 x ncomp_null, statistics on voxels above the 99th percentile.
  - Scene verdict (aggregation was not specified in C.2; fixed here): ARCHITECTURE-LIKE
    if the rule fires in >= 5 of the 8 treatments (a majority), otherwise NOT.
  - In-data positive control (fixed here): the same real volume with the calibration's
    four planted shafts (plant_shafts, amp 6, seed 11). If it does not fire in >= 5 of
    8, that scene's result is INCONCLUSIVE, not negative.

  SECONDARY (reported, labelled as not pre-registered; cannot overturn the primary)
  - Null-seed spread: seeds 0-4 at bw_frac 0.80.
  - Spectrally matched null: bw_frac estimated from each real crop's spectrum.
  - Off-centre crops: up to 4 more 768 crops per scene, offset +/-1536 px diagonally.

No published figure is scored here (C.4: not before step 1 is committed).

Run:
    python3.13 src/shape_metric_giza.py            # real run (needs sarpy + scipy)
    python3.13 src/shape_metric_giza.py --selftest # synthetic check, no SICD needed
Output: runs/shape_metric_giza.json (+ runs/shape_metric_giza.png)
"""
import argparse, glob, json, os, subprocess, sys, time
import numpy as np
from scipy.ndimage import label

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, steering, analytic1d
from micromotion import detrend
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e
from volume_render import bandlimited_slc
from render_sweep import OPS, apply_ops

PCT = 99.0
CANVAS, PATCH, STRIDE, NSUB, OVERLAP, BW_NULL = 768, 64, 24, 11, 0.8, 0.80
EXCLUDED = {"tile whiten", "whiten + log", "common-mode + whiten + log", "depth gain z^4"}
INCLUDED = [n for n in OPS if n not in EXCLUDED]
MAJORITY = 5
SCENE_GLOB = "data/giza_*_SICD.nitf"
PRIMARY_SCENE = "giza_2023-03-08_UMBRA-04"


# ---- copied VERBATIM from src/shape_metric.py (the pre-registered statistic) ----
def stats(vol, pct=PCT):
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
    rng = np.random.default_rng(seed)
    v = vol.copy()
    nx, ny, nz = v.shape
    s = np.median(v) + amp * (np.percentile(v, 99) - np.median(v))
    for _ in range(n_shaft):
        cx, cy = rng.integers(3, nx - 3), rng.integers(3, ny - 3)
        z0, z1 = rng.integers(20, 80), rng.integers(200, nz - 10)
        v[cx:cx + 2, cy:cy + 2, z0:z1] += s
    return v
# ---------------------------------------------------------------------------------


def build_volume(img):
    """Identical to render_sweep.py's volume path (no LRSD)."""
    zgrid = np.linspace(0, NSUB * DZ_TARGET / 2, 300)
    A, _ = steering(NSUB, zgrid)
    looks, _ = decompose_subapertures_w(img, n_sub=NSUB, overlap=OVERLAP, axis=1,
                                        window="hann", dtype=np.complex128)
    H, W = looks.shape[1], looks.shape[2]
    rows = list(range(0, H - PATCH + 1, STRIDE))
    cols = list(range(0, W - PATCH + 1, STRIDE))
    obs = []
    for r in rows:
        for c in cols:
            t = np.asarray(adjacent_trajectory_e(looks[:, r:r + PATCH, c:c + PATCH],
                                                 dtype=np.complex128)[0], dtype=float)
            obs.append(detrend(t, deg=2))
    V = np.array([np.abs(A.conj().T @ analytic1d(o)) ** 2 for o in obs])
    return V.reshape(len(rows), len(cols), -1)


def null_volume(bw=BW_NULL, seed=0):
    return build_volume(bandlimited_slc(CANVAS, bw, np.random.default_rng(seed)))


def score(real, null):
    """Pre-registered rule, per included treatment."""
    out, fires = {}, 0
    for name in INCLUDED:
        sr, sn = stats(apply_ops(real, OPS[name])), stats(apply_ops(null, OPS[name]))
        rv = sr["vrun"] / (sn["vrun"] + 1e-9)
        rc = sn["ncomp"] / (sr["ncomp"] + 1e-9)
        arch = bool(rv > 1.5 or rc > 2.0)
        fires += arch
        out[name] = dict(real=sr, null=sn, vrun_ratio=float(rv), ncomp_ratio=float(rc),
                         architecture_like=arch)
    return out, fires


def estimate_bw(img):
    """Occupied spectral fraction (mean of the two axes), for the SECONDARY null."""
    P = np.abs(np.fft.fftshift(np.fft.fft2(img))) ** 2
    fr = []
    for ax in (0, 1):
        m = P.mean(axis=ax)
        m = np.convolve(m, np.ones(9) / 9, mode="same")
        fr.append(float((m > 0.1 * m.max()).mean()))
    return float(np.clip(np.mean(fr), 0.3, 1.0))


def read_crop(path, r0, c0, n=CANVAS):
    from sarpy.io.complex.converter import open_complex
    rd = open_complex(path)
    return np.asarray(rd[r0:r0 + n, c0:c0 + n], dtype=np.complex128), rd.data_size


def crop_origins(R, C, n=CANVAS, off=1536):
    rc, cc = R // 2 - n // 2, C // 2 - n // 2
    cand = [(rc, cc)] + [(rc + dr, cc + dc) for dr in (-off, off) for dc in (-off, off)]
    return [(r, c) for r, c in cand if 0 <= r and r + n <= R and 0 <= c and c + n <= C]


def verdict(fires, pc_fires):
    if pc_fires < MAJORITY:
        return "INCONCLUSIVE (positive control failed)"
    return "ARCHITECTURE-LIKE" if fires >= MAJORITY else "NOT architecture-like"


def line(tag, fires, pc):
    print(f"  {tag:<34} rule fires {fires}/8   planted-shaft control {pc}/8   -> "
          f"{verdict(fires, pc)}", flush=True)


def git_rev():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def figure(real, null, title, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    show = ["raw", "common-mode removed", "z-blur", "gain z^4 + z-blur + gamma"]
    fig, ax = plt.subplots(2, len(show), figsize=(4.2 * len(show), 7.5), facecolor="black")
    for j, name in enumerate(show):
        for i, (V, lab) in enumerate([(real, "REAL Giza"), (null, "EMPTY (no scene)")]):
            Vt = apply_ops(V, OPS[name])
            sl = Vt[:, Vt.shape[1] // 2, :].T
            ax[i, j].imshow(sl / (sl.max() + 1e-30), aspect="auto", cmap="inferno",
                            origin="upper", vmin=0, vmax=1)
            ax[i, j].set_title(f"{lab}\n{name}", color="white", fontsize=9)
            ax[i, j].set_xticks([]); ax[i, j].set_yticks([])
    fig.suptitle(title + "\nvertical slice through the volume; depth increases downward",
                 color="white", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(out, dpi=110, facecolor="black")
    print(f"figure -> {out}")


def main_real():
    scenes = sorted(glob.glob(SCENE_GLOB))
    if not scenes:
        sys.exit(f"no SICDs matching {SCENE_GLOB}")
    t0 = time.time()
    print("building the pre-registered null (bw 0.80, seed 0) ...", flush=True)
    N0 = null_volume()
    null_cache = {0: N0}
    res = dict(prereg="docs/PREREGISTRATION_MINES_AND_GRANSASSO.md Part C",
               script="src/shape_metric_giza.py", git=git_rev(), pct=PCT,
               params=dict(canvas=CANVAS, patch=PATCH, stride=STRIDE, n_sub=NSUB,
                           overlap=OVERLAP, window="hann", null_bw=BW_NULL, null_seed=0),
               included=INCLUDED, excluded=sorted(EXCLUDED), majority=MAJORITY,
               primary={}, secondary={})
    print("\nPRIMARY (pre-registered rule, centre crop vs seed-0 null)")
    fig_done = False
    for p in scenes:
        name = os.path.basename(p).split("_SICD")[0]
        _, (R, C) = read_crop(p, 0, 0, 1)
        origins = crop_origins(R, C)
        img, _ = read_crop(p, *origins[0])
        V = build_volume(img)
        sc, fires = score(V, N0)
        _, pc = score(plant_shafts(V), N0)
        res["primary"][name] = dict(crop_origin=list(map(int, origins[0])), shape=[R, C],
                                    fires=fires, positive_control_fires=pc,
                                    verdict=verdict(fires, pc), treatments=sc)
        line(name + (" [prereg primary]" if name == PRIMARY_SCENE else ""), fires, pc)
        if name == PRIMARY_SCENE or not fig_done:
            figure(V, N0, f"{name}: real centre crop vs pipeline-matched empty volume",
                   "runs/shape_metric_giza.png")
            fig_done = name == PRIMARY_SCENE

        # ---- SECONDARY ----
        sec = dict(null_seeds={}, spectral_null={}, offcentre={})
        for s in range(5):
            if s not in null_cache:
                null_cache[s] = null_volume(seed=s)
            sec["null_seeds"][s] = score(V, null_cache[s])[1]
        bw = estimate_bw(img)
        Nb = null_volume(bw=bw)
        sec["spectral_null"] = dict(bw=bw, fires=score(V, Nb)[1],
                                    positive_control_fires=score(plant_shafts(V), Nb)[1])
        for (r, c) in origins[1:]:
            Vo = build_volume(read_crop(p, r, c)[0])
            sec["offcentre"][f"{r},{c}"] = dict(fires=score(Vo, N0)[1],
                                                positive_control_fires=score(plant_shafts(Vo), N0)[1])
        res["secondary"][name] = sec
        print(f"    secondary: fires vs null seeds 0-4 = {list(sec['null_seeds'].values())}; "
              f"vs spectral null (bw {bw:.2f}) = {sec['spectral_null']['fires']}/8; "
              f"off-centre = {[d['fires'] for d in sec['offcentre'].values()]}", flush=True)

    json.dump(res, open("runs/shape_metric_giza.json", "w"), indent=1)
    print(f"\nresults -> runs/shape_metric_giza.json   ({time.time()-t0:.0f}s)")
    print("Report the PRIMARY lines as the C.5 result. Secondary cannot overturn them.")


def selftest():
    """Decision-logic check with no SICD: a second empty volume must NOT be called
    architecture-like; the same volume with planted shafts MUST be."""
    N0 = null_volume(seed=0)
    Nx = null_volume(seed=7)
    _, f_empty = score(Nx, N0)
    _, f_plant = score(plant_shafts(Nx), N0)
    ok = f_empty < MAJORITY and f_plant >= MAJORITY
    print(f"[A] independent empty volume: rule fires {f_empty}/8 (want <{MAJORITY})")
    print(f"[B] same volume + planted shafts: rule fires {f_plant}/8 (want >={MAJORITY})")
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    os.makedirs("runs", exist_ok=True)
    sys.exit(0 if selftest() else 1) if a.selftest else main_real()
