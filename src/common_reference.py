#!/usr/bin/env python3
"""
common_reference.py — pre-registered test I (docs/PREREGISTRATION_COMMON_REFERENCE_2026-10-07.md).

Question (hostile panel 1a): is the shallow, surface-pinned tomogram peak specific to ADJACENT-PAIR
ACCUMULATION (the running total, np.cumsum), or does it also appear when every look is registered to one
common reference look with no running total?

Configuration is identical to E8 / test H except the tracker: 512 centre crop, patch 64, 24 patches on the
centre row, n_sub 11, overlap 0.8, Hann, degree-2 detrend, 300 bins, guard 2 cells. Reference look = the
centre look (index 5). PRIMARY estimator = plain normalised cross-correlation + parabolic refine
(est_ncc_parabolic): in design checks it was the only existing estimator that recovered a planted shift across
the whole aperture on persistent scatterers. SECONDARY = the pipeline's phase correlation (descriptive).

Part 1 (synthetic, fixed seeds): expected depth curves for white and random-walk trajectory noise (analytic);
common-reference tomograms of MOTION-FREE scenes (speckle + persistent point scatterers at three strengths)
and of the same scenes with a planted genuine smooth shift; pure speckle as the untrackable case.
Part 2 (Giza): per-scene trackability control, common-reference peak, comparison with the Part 1 nulls.

  python3.13 src/common_reference.py            # full run (sarpy) -> runs/common_reference.json
  python3 src/common_reference.py --selftest    # quick synthetic check, no SICD
"""
import argparse, glob, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, contrast, tomogram_from_observations, metric_depth_axis
from micromotion import detrend
from sensitivity_sweep import (decompose_subapertures_w, adjacent_trajectory_e, est_phasecorr_parabolic,
                               est_ncc_parabolic, fourier_shift_p)
from volume_render import bandlimited_slc
from derive_depth_constant import _Hmat

N_SUB, OVERLAP, PATCH, N_PATCH, CROP = 11, 0.8, 64, 24, 512
REF = N_SUB // 2
GUARD, BW = 2.0, 0.80
PLANT_AMP, PLANT_CYC = 0.5, 2          # trackability control: 2-cycle sinusoid, 0.5 px
CTRL_R, CTRL_N = 0.9, 20               # pass = r >= 0.9 with the planted shift in >= 20/24 patches
SCR_AMPS = (5.0, 15.0, 30.0)           # point-scatterer strengths for the motion-free nulls
SIGNAL_PX = (0.1, 0.3)                 # planted genuine smooth shift (1.5 cycles) for the signal arm
N_NULL, N_SIG, SEED = 50, 25, 20261007
ESTIMATORS = {"ncc": est_ncc_parabolic, "phasecorr": est_phasecorr_parabolic}
_, DZ_PHYS = metric_depth_axis(np.array([0.0]), 6000.0, 22000.0, 650e3, 42e3)
Z = np.linspace(0, N_SUB * DZ_TARGET / 2, 300)


# ---------------------------------------------------------------- pipeline pieces
def patches(img, shift_seq=None):
    looks, _ = decompose_subapertures_w(img, n_sub=N_SUB, overlap=OVERLAP, axis=1, window="hann",
                                        dtype=np.complex128)
    r0 = img.shape[0] // 2 - PATCH // 2
    out = []
    for cc in np.linspace(0, img.shape[1] - PATCH, N_PATCH).astype(int):
        lp = looks[:, r0:r0 + PATCH, cc:cc + PATCH]
        if shift_seq is not None:
            lp = np.array([fourier_shift_p(lp[k], 0.0, shift_seq[k]) for k in range(N_SUB)])
        out.append(lp)
    return out


def cr_trajectory(lp, est="ncc"):
    fn, ref = ESTIMATORS[est], np.abs(lp[REF])
    return np.array([0.0 if k == REF else fn(ref, np.abs(lp[k]))[1] for k in range(N_SUB)])


def adj_trajectory(lp):
    return np.asarray(adjacent_trajectory_e(lp, estimator="phasecorr", dtype=np.complex128)[0], float)


def peak_cells(arr):
    obs = np.array([detrend(t, deg=2) for t in arr])
    T = tomogram_from_observations(obs, Z)
    return float(Z[int(np.argmax(T.sum(0)))] / DZ_TARGET), float(contrast(T))


def common_mode(tr):
    """Patch-mean trajectory energy relative to its sampling noise (~1 if patches share nothing)."""
    m = tr.mean(0); v = tr.var(0, ddof=1)
    return float(len(tr) * np.sum(m ** 2) / max(np.sum(v), 1e-12))


def cr_stats(ps, est="ncc"):
    tr = np.array([cr_trajectory(lp, est) for lp in ps])
    pk, c = peak_cells(tr)
    return dict(peak=pk, contrast=c, pinned=bool(pk <= GUARD), common_mode=common_mode(tr),
                sd_profile=tr.std(0).round(4).tolist())


def control(img, est="ncc"):
    shifts = PLANT_AMP * np.sin(2 * np.pi * PLANT_CYC * np.arange(N_SUB) / N_SUB)
    target = shifts - shifts[REF]
    r = np.array([np.corrcoef(cr_trajectory(lp, est), target)[0, 1] for lp in patches(img, shifts)])
    good = int(np.sum(r >= CTRL_R))
    return dict(estimator=est, patches_recovered=good, passed=good >= CTRL_N, median_r=float(np.median(r)))


# ---------------------------------------------------------------- synthetic scenes
def point_scene(rng, amp=15.0, n_pts=3):
    """Speckle plus persistent point scatterers (n_pts per patch), band-limited like the speckle. No motion."""
    img = bandlimited_slc(CROP, BW, rng)
    n = int(round(CROP * BW)); lo = CROP // 2 - n // 2
    pts = np.zeros((CROP, CROP), complex); r0 = CROP // 2 - PATCH // 2
    for cc in np.linspace(0, CROP - PATCH, N_PATCH).astype(int):
        for _ in range(n_pts):
            pts[r0 + rng.integers(8, 56), cc + rng.integers(8, 56)] = \
                amp * np.std(img) * n * np.exp(2j * np.pi * rng.random())
    S = np.fft.fftshift(np.fft.fft2(pts)); m = np.zeros(S.shape); m[lo:lo + n, lo:lo + n] = 1
    return img + np.fft.ifft2(np.fft.ifftshift(S * m)) / n


def expected_curve(C, deg=2, nz=2000):
    """E[P(z)] for trajectory covariance C (the derive_depth_constant formula, general C)."""
    n = C.shape[0]; t = np.arange(n)
    V = np.vander(t, deg + 1, increasing=True).astype(float); R = np.eye(n) - V @ np.linalg.pinv(V)
    S = _Hmat(n) @ (R @ C @ R.T) @ _Hmat(n).conj().T
    z = np.linspace(0, n * DZ_TARGET / 2, nz)
    G = np.exp(-1j * np.outer(np.arange(n) * 2 * np.pi / (n * DZ_TARGET), z))
    P = np.einsum("kz,kl,lz->z", G, S, np.conj(G)).real
    return z / DZ_TARGET, P


def summarise(rows):
    pk = np.array([r["peak"] for r in rows]); cm = np.array([r["common_mode"] for r in rows])
    return dict(n=len(rows), peaks=pk.round(3).tolist(), peak_q05=float(np.quantile(pk, .05)),
                peak_median=float(np.median(pk)), peak_q95=float(np.quantile(pk, .95)),
                pinned_frac=float(np.mean(pk <= GUARD)), common_mode=cm.round(2).tolist(),
                common_mode_median=float(np.median(cm)), common_mode_q95=float(np.quantile(cm, .95)))


def part1(n_null=N_NULL, n_sig=N_SIG, seed=SEED, verbose=True):
    out = {}
    t = np.arange(N_SUB)
    for nm, C in (("random_walk", np.minimum.outer(t, t) + 1.0), ("white", np.eye(N_SUB))):
        z, P = expected_curve(C)
        out[f"analytic_{nm}"] = dict(expected_peak_cells=float(z[P.argmax()]),
                                     guard_max_over_max=float(P[z <= GUARD].max() / P.max()))
    rng = np.random.default_rng(seed)
    out["speckle_untrackable"] = summarise([cr_stats(patches(bandlimited_slc(CROP, BW, rng)))
                                            for _ in range(n_null)])
    for amp in SCR_AMPS:
        out[f"motion_free_amp{int(amp)}"] = summarise([cr_stats(patches(point_scene(rng, amp)))
                                                       for _ in range(n_null)])
    k = np.arange(N_SUB)
    for a in SIGNAL_PX:
        seq = a * np.sin(2 * np.pi * 1.5 * k / N_SUB)
        out[f"planted_signal_{a}px"] = summarise([cr_stats(patches(point_scene(rng, 15.0), seq))
                                                  for _ in range(n_sig)])
    if verbose:
        for key, v in out.items():
            if key.startswith("analytic"):
                print(f"  {key}: expected peak {v['expected_peak_cells']:.2f} cells, "
                      f"best power inside the guard / global best {v['guard_max_over_max']:.2f}")
            else:
                print(f"  {key}: peak median {v['peak_median']:.2f} [{v['peak_q05']:.2f}, {v['peak_q95']:.2f}], "
                      f"pinned {100*v['pinned_frac']:.0f}%, common-mode median {v['common_mode_median']:.1f} "
                      f"(q95 {v['common_mode_q95']:.1f})", flush=True)
    return out


def verdict(scenes, p1):
    """Two pre-registered readings: (A) does the peak pin without accumulation; (B) is there a common
    (scene-wide) look-dependent shift beyond the largest motion-free null q95."""
    tr = {n: s for n, s in scenes.items() if s["control_ncc"]["passed"]}
    if len(tr) < 2:
        return ("NOT TRACKABLE: fewer than 2 Giza scenes pass the common-reference control; this filter bank "
                "cannot register these scenes across the aperture, so the test cannot separate the mechanisms")
    pinned = sum(s["cr_ncc"]["pinned"] for s in tr.values())
    cm_crit = max(p1[f"motion_free_amp{int(a)}"]["common_mode_q95"] for a in SCR_AMPS)
    cm_hits = sum(s["cr_ncc"]["common_mode"] > cm_crit for s in tr.values())
    a = ("A=PIN WITHOUT ACCUMULATION: the shallow peak is not specific to the running total"
         if pinned >= 2 else
         "A=ACCUMULATION-DEPENDENT: trackable scenes do not pin without the running total")
    b = (f"B=COMMON SHIFT PRESENT in {cm_hits} trackable scene(s) (scene-wide; cause unknown; not a subsurface indicator)"
         if cm_hits >= 2 else "B=NO COMMON SHIFT beyond motion-free tracking noise")
    return f"{a} | {b}"


# ---------------------------------------------------------------- runs
def main_real():
    from sarpy.io.complex.converter import open_complex
    from shape_metric_giza import git_rev
    res = dict(prereg="docs/PREREGISTRATION_COMMON_REFERENCE_2026-10-07.md", script="src/common_reference.py",
               git=git_rev(), reference_look=REF, guard_cells=GUARD, seed=SEED)
    print("Part 1 (synthetic) ...", flush=True)
    res["part1"] = p1 = part1()
    res["scenes"] = {}
    print("Part 2 (Giza) ...", flush=True)
    for p in sorted(glob.glob("data/giza_*_SICD.nitf")):
        name = os.path.basename(p).split("_SICD")[0]
        rd = open_complex(p); R, C = rd.data_size
        r0, c0 = R // 2 - CROP // 2, C // 2 - CROP // 2
        img = np.asarray(rd[r0:r0 + CROP, c0:c0 + CROP], dtype=np.complex128)
        ps = patches(img)
        ad = np.array([adj_trajectory(lp) for lp in ps])
        inc = np.array([np.concatenate([[0.0], np.diff(t)]) for t in ad])
        s = dict(cr_ncc=cr_stats(ps, "ncc"), cr_phasecorr=cr_stats(ps, "phasecorr"),
                 control_ncc=control(img, "ncc"), control_phasecorr=control(img, "phasecorr"),
                 peak_cumsum=peak_cells(ad)[0], peak_increments=peak_cells(inc)[0])
        s["pct_in_motion_free"] = {f"amp{int(a)}": float(np.mean(
            np.array(p1[f"motion_free_amp{int(a)}"]["peaks"]) <= s["cr_ncc"]["peak"])) for a in SCR_AMPS}
        res["scenes"][name] = s
        c = s["cr_ncc"]
        print(f"{name}: control {s['control_ncc']['patches_recovered']}/24 "
              f"({'TRACKABLE' if s['control_ncc']['passed'] else 'not trackable'}) | CR peak {c['peak']:.2f} "
              f"({'PIN' if c['pinned'] else 'clear'}), common-mode {c['common_mode']:.1f} | CR(phasecorr) "
              f"{s['cr_phasecorr']['peak']:.2f} | cumsum {s['peak_cumsum']:.2f} | increments "
              f"{s['peak_increments']:.2f}", flush=True)
    res["overall"] = verdict(res["scenes"], p1)
    print(f"\nOVERALL: {res['overall']}")
    os.makedirs("runs", exist_ok=True)
    json.dump(res, open("runs/common_reference.json", "w"), indent=1)
    print("-> runs/common_reference.json")


def selftest():
    ok = True
    for nm, img, want in (("speckle", bandlimited_slc(CROP, BW, np.random.default_rng(1)), False),
                          ("point scatterers", point_scene(np.random.default_rng(7)), True)):
        c = control(img)
        print(f"[{nm}] trackability control {c['patches_recovered']}/24 (expected {'pass' if want else 'fail'})")
        ok &= (c["passed"] == want)
    p1 = part1(n_null=8, n_sig=6, seed=3)
    ok &= abs(p1["analytic_random_walk"]["expected_peak_cells"] - 1.71) < 0.05
    ok &= p1["planted_signal_0.3px"]["common_mode_median"] > p1["motion_free_amp15"]["common_mode_q95"]
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(0 if selftest() else 1) if a.selftest else main_real()
