#!/usr/bin/env python3
"""
sensitivity_sweep.py — configuration sensitivity of the null result.

WHY THIS EXISTS
---------------
On the Malanga interview thread (28 Jul 2026) a commenter posting as F. Biondi
raised three configuration objections to this reproduction:

  1. "Which coregistrator are you using? DORIS or GeFolki?"
  2. "Remain in Double precision at all times and never work in Float32."
  3. "Which filtering strategy on the sub-apertures? I suggest a Hamming window."

and, in a follow-up, the general principle that a failed reproduction may reflect
"one or more configuration choices that are left to the user alone" rather than a
defect in the original method.

This module answers all three empirically. It re-runs the ENTIRE pipeline —
sub-aperture decomposition, coregistration, micro-motion estimation, inversion,
null test, positive control, surface-leakage check — across a grid of:

    window     x  numerical precision  x  shift estimator (coregistrator)

and reports, for each cell, whether the verdict changes.

DESIGN COMMITMENT (this must be able to fail)
---------------------------------------------
Nothing here privileges the published result. The reported statistic is an
empirical permutation p-value, computed identically in every cell. If any
configuration produces an above-null, non-surface-pinned, leakage-clean detection,
this script prints it as such and the paper's conclusion needs revisiting. That is
the point of running it.

A STRONGER NULL THAN THE PAPER'S
--------------------------------
tomogram.py compares real contrast against ONE shuffled null. Here the null is a
distribution over `--n-perm` permutations, giving a proper empirical p-value and
z-score. This is a strict tightening, not a loosening.

USAGE
-----
  # validate the harness itself (no data, no network):
  python3 src/sensitivity_sweep.py --selftest

  # synthetic-scene sweep (no data, no network) — tests the knobs, not the site:
  python3 src/sensitivity_sweep.py --synthetic

  # the real answer (needs the Butte SICD on disk):
  python3 src/sensitivity_sweep.py --sicd data/2024-03-07-04-48-26_UMBRA-04_SICD.nitf

Deps: numpy, scipy, scikit-image, matplotlib (sarpy only for --sicd).
"""
import argparse, os, sys, json, itertools, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subaperture import fourier_shift, subpixel_shift as baseline_shift
from micromotion import detrend, match_score
from tomogram import (DZ_TARGET, steering, tomogram_from_observations, contrast,
                      inject_damped_resonance, leakage_correlation,
                      surface_brightness, shallow_pinned, peak_depth,
                      metric_depth_axis)


# ===========================================================================
# 1. WINDOWS — objection #3
# ===========================================================================
WINDOWS = {
    "hann":     np.hanning,      # what the paper uses
    "hamming":  np.hamming,      # what he recommends
    "blackman": np.blackman,     # lower sidelobes still (bracket)
    "rect":     np.ones,         # no taper at all (worst-case bracket)
}


# --- genuine single-precision support -------------------------------------
# numpy.fft ALWAYS promotes to double internally and returns complex128, so
# casting inputs to complex64 does not give a single-precision pipeline — it
# gives a double-precision pipeline with rounded storage. scipy.fft honours the
# input dtype and computes in single. Using it is what makes the float32 arm of
# this sweep an honest test of his objection #2 rather than a no-op.
import scipy.fft as _sfft


def _pack(dtype):
    """Return (fft, ifft, fft2, ifft2, fftshift, ifftshift, real_dtype)."""
    if np.dtype(dtype) == np.complex64:
        return (_sfft.fft, _sfft.ifft, _sfft.fft2, _sfft.ifft2,
                _sfft.fftshift, _sfft.ifftshift, np.float32)
    return (np.fft.fft, np.fft.ifft, np.fft.fft2, np.fft.ifft2,
            np.fft.fftshift, np.fft.ifftshift, np.float64)


def fourier_shift_p(img, sy, sx, dtype=np.complex128):
    """Precision-aware version of subaperture.fourier_shift."""
    _, _, f2, if2, _, _, rdt = _pack(dtype)
    H, W = img.shape
    ky = np.fft.fftfreq(H).astype(rdt)[:, None]
    kx = np.fft.fftfreq(W).astype(rdt)[None, :]
    ph = np.exp(-2j * np.pi * (ky * rdt(sy) + kx * rdt(sx))).astype(dtype)
    return if2(f2(np.asarray(img, dtype)) * ph)


def decompose_subapertures_w(slc, n_sub=7, overlap=0.5, axis=1,
                             window="hann", dtype=np.complex128):
    """Sub-aperture decomposition with a selectable spectral taper and precision.

    Byte-for-byte identical to the repo's decompose_subapertures() when
    window='hann' and dtype=complex128 (verified in selftest [A]).
    """
    fft, ifft, _, _, fftshift, ifftshift, rdt = _pack(dtype)
    wfun = WINDOWS[window]
    slc = np.asarray(slc, dtype=dtype)
    N = slc.shape[axis]
    SP = fftshift(fft(slc, axis=axis), axes=axis).astype(dtype)

    band = N / (n_sub - (n_sub - 1) * overlap)
    step = band * (1 - overlap)
    looks, centroids = [], []
    for k in range(n_sub):
        c = band / 2 + k * step
        lo, hi = int(round(c - band / 2)), int(round(c + band / 2))
        lo, hi = max(0, lo), min(N, hi)
        w = np.zeros(N, dtype=rdt)
        w[lo:hi] = wfun(hi - lo).astype(rdt)
        shape = [1, 1]; shape[axis] = N
        sub = ifft(ifftshift((SP * w.reshape(shape)).astype(dtype), axes=axis), axis=axis)
        looks.append(np.asarray(sub, dtype=dtype))
        centroids.append((lo + hi) / 2 - N / 2)
    return np.array(looks, dtype=dtype), np.array(centroids)


# ===========================================================================
# 2. SHIFT ESTIMATORS ("coregistrators") — objection #1
# ===========================================================================
# All return (dy, dx) in the repo's convention: the shift of `img` relative to
# `ref`, verified against known Fourier shifts in selftest [B].

def est_phasecorr_parabolic(ref, img, rdt=np.float64):
    """Baseline (what the paper uses): FFT phase correlation + 1-D parabolic refine.
    At rdt=float64 this calls the repo's own subpixel_shift() unmodified."""
    if rdt is np.float64:
        return baseline_shift(ref, img)
    f2, if2 = _sfft.fft2, _sfft.ifft2
    F = f2(np.asarray(ref, np.complex64)); G = f2(np.asarray(img, np.complex64))
    R = F * np.conj(G)
    R = (R / (np.abs(R) + np.float32(1e-12))).astype(np.complex64)
    corr = if2(R).real
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    H, W = corr.shape
    dy = py + _par(corr[:, px], py); dx = px + _par(corr[py, :], px)
    if dy > H / 2: dy -= H
    if dx > W / 2: dx -= W
    return -dy, -dx


def _par(c, i):
    n = len(c); l, m, r = c[(i-1) % n], c[i], c[(i+1) % n]
    d = (l - 2*m + r)
    return 0.0 if d == 0 else 0.5 * (l - r) / d


def est_upsampled_dft(ref, img, rdt=np.float64, upsample=100):
    """Guizar-Sicairos et al. upsampled-DFT registration (skimage). This is the
    sub-pixel engine used inside most modern coregistration stacks, including the
    resampling stage of interferometric processors of the DORIS lineage."""
    from skimage.registration import phase_cross_correlation
    sh = phase_cross_correlation(np.asarray(ref, rdt), np.asarray(img, rdt),
                                 upsample_factor=upsample, normalization="phase")[0]
    return -float(sh[0]), -float(sh[1])


def est_ncc_parabolic(ref, img, rdt=np.float64):
    """Plain normalised cross-correlation (no phase whitening) + parabolic refine.
    Deliberately a *different* similarity metric, not just a different refinement."""
    f2, if2 = (_sfft.fft2, _sfft.ifft2) if rdt is np.float32 else (np.fft.fft2, np.fft.ifft2)
    a = np.asarray(ref, rdt); b = np.asarray(img, rdt)
    a = a - a.mean(); b = b - b.mean()
    corr = if2(f2(a) * np.conj(f2(b))).real
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    H, W = corr.shape
    dy = py + _par(corr[:, px], py); dx = px + _par(corr[py, :], px)
    if dy > H / 2: dy -= H
    if dx > W / 2: dx -= W
    return -dy, -dx


def est_optical_flow(ref, img, rdt=np.float64):
    """Dense optical flow (TV-L1), averaged to a global shift. The Lucas-Kanade /
    variational-flow family — the lineage GeFolki belongs to. Slow; included because
    it is the closest available stand-in for the specific tool he named."""
    from skimage.registration import optical_flow_tvl1
    a = np.asarray(ref, rdt); b = np.asarray(img, rdt)
    a = (a - a.min()) / (np.ptp(a) + 1e-12)
    b = (b - b.min()) / (np.ptp(b) + 1e-12)
    v, u = optical_flow_tvl1(a, b, attachment=15, num_warp=3)
    return float(np.median(v)), float(np.median(u))


ESTIMATORS = {
    "phasecorr":  est_phasecorr_parabolic,   # paper baseline
    "upsampdft":  est_upsampled_dft,         # DORIS-lineage sub-pixel engine
    "ncc":        est_ncc_parabolic,         # different similarity metric
    "opticalflow": est_optical_flow,         # GeFolki-lineage (slow)
}


def adjacent_trajectory_e(looks, estimator="phasecorr", dtype=np.complex128):
    """Repo's adjacent_trajectory() with a pluggable shift estimator + precision."""
    fn = ESTIMATORS[estimator]
    rdt = np.float32 if np.dtype(dtype) == np.complex64 else np.float64
    N = len(looks)
    inc = np.zeros(N, dtype=rdt); coh = np.ones(N)
    for k in range(1, N):
        dy, dx = fn(np.abs(looks[k - 1]), np.abs(looks[k]), rdt)
        inc[k] = dx
        aligned = fourier_shift_p(looks[k], -dy, -dx, dtype=dtype)
        coh[k] = match_score(looks[k - 1], aligned)
    return np.cumsum(inc), coh


# ===========================================================================
# 3. OBSERVATIONS under a given configuration
# ===========================================================================
def patch_observations_cfg(slc, cols, row, patch, n_sub, overlap,
                           window, dtype, estimator):
    looks, _ = decompose_subapertures_w(slc, n_sub=n_sub, overlap=overlap, axis=1,
                                        window=window, dtype=dtype)
    obs, quals = [], []
    for cc in cols:
        lp = looks[:, row:row+patch, cc:cc+patch]
        traj, q = adjacent_trajectory_e(lp, estimator=estimator, dtype=dtype)
        obs.append(detrend(traj, deg=2))
        quals.append(float(np.mean(q[1:])))
    return np.array(obs, dtype=float), quals


# ===========================================================================
# 4. PERMUTATION NULL — stronger than the paper's single shuffle
# ===========================================================================
def permutation_null(obs, zgrid, n_perm, seed=0):
    """Empirical null distribution of the contrast statistic."""
    rng = np.random.default_rng(seed)
    out = np.empty(n_perm)
    for i in range(n_perm):
        sh = np.array([r[rng.permutation(len(r))] for r in obs])
        out[i] = contrast(tomogram_from_observations(sh, zgrid))
    return out


def evaluate(obs, bright, zgrid, n_perm=200, seed=0):
    """Full control battery for one configuration. Returns a plain dict."""
    T = tomogram_from_observations(obs, zgrid)
    c_real = contrast(T)
    nulls = permutation_null(obs, zgrid, n_perm, seed=seed)

    # one-sided empirical p-value, add-one corrected (never reports p=0)
    p = (1 + int(np.sum(nulls >= c_real))) / (1 + n_perm)
    z = (c_real - nulls.mean()) / (nulls.std() + 1e-12)

    # hardened positive control: damped resonance, off the steering basis
    z_deep = 0.7 * zgrid[-1]
    amp = 4 * np.std(obs)
    Ti = tomogram_from_observations(
        inject_damped_resonance(obs, zgrid, z_deep, amp), zgrid)
    pc_z = peak_depth(Ti, zgrid)
    pc_c = contrast(Ti)
    pc_p = (1 + int(np.sum(nulls >= pc_c))) / (1 + n_perm)
    pc_ok = bool(abs(pc_z - z_deep) <= 3 * DZ_TARGET and pc_p < 0.05)

    pinned, pkfrac, shen = shallow_pinned(T)
    leak = leakage_correlation(T, bright) if bright is not None else float("nan")

    # --- the PAPER's own criterion, reproduced exactly for comparability ---
    # tomogram.py: above = contrast(T) > 5 * contrast(one shuffled null)
    rng1 = np.random.default_rng(0)
    sh1 = np.array([r[rng1.permutation(len(r))] for r in obs])
    c_null1 = contrast(tomogram_from_observations(sh1, zgrid))
    ratio_paper = float(c_real / (c_null1 + 1e-12))
    paper_detect = bool(ratio_paper > 5.0 and not pinned)

    # --- the stricter permutation criterion added here ---
    perm_detect = bool(p < 0.05 and not pinned and (np.isnan(leak) or leak <= 0.5))

    return dict(
        contrast_real=float(c_real),
        null_mean=float(nulls.mean()), null_p95=float(np.percentile(nulls, 95)),
        p_value=float(p), z_score=float(z),
        ratio_paper=ratio_paper, PAPER_DETECT=paper_detect,
        pos_ctrl_ok=pc_ok, pos_ctrl_z_err=float(abs(pc_z - z_deep)),
        pos_ctrl_p=float(pc_p),
        surface_pinned=bool(pinned), peak_frac=float(pkfrac),
        leakage=float(leak),
        DETECTION=perm_detect,
    )


# ===========================================================================
# 5. THE SWEEP
# ===========================================================================
def run_sweep(slc, n_sub, patch, n_patch, overlap, windows, dtypes, estimators,
              n_perm, seed, label):
    global n_perm_used
    n_perm_used = n_perm
    H, W = slc.shape
    row = H // 2 - patch // 2
    cols = np.linspace(0, W - patch, n_patch).astype(int)
    bright = surface_brightness(slc, row, cols, patch)
    zgrid = np.linspace(0, n_sub * DZ_TARGET / 2, 300)

    rows = []
    combos = list(itertools.product(windows, dtypes, estimators))
    print(f"\n{'='*104}")
    print(f"SENSITIVITY SWEEP — {label}")
    print(f"  {len(combos)} configurations x {n_perm} permutations each "
          f"| n_sub={n_sub} patch={patch} n_patch={n_patch} overlap={overlap}")
    print(f"{'='*104}")
    hdr = (f"{'window':<9} {'prec':<8}{'coregistrator':<13}{'qual':>6}"
           f"{'contrast':>9}{'null_mu':>8}{'ratio':>7}{'z':>7}{'p':>8}"
           f"{'posctl':>7}{'pin':>6}{'leak':>6}   {'paper>5x':<9}{'perm p<.05'}")
    print(hdr); print("-" * 118)

    for win, dt, est in combos:
        t0 = time.time()
        dtype = np.complex64 if dt == "float32" else np.complex128
        obs, quals = patch_observations_cfg(slc, cols, row, patch, n_sub,
                                            overlap, win, dtype, est)
        r = evaluate(obs, bright, zgrid, n_perm=n_perm, seed=seed)
        r.update(window=win, precision=dt, coregistrator=est,
                 mean_quality=float(np.mean(quals)), secs=round(time.time() - t0, 1))
        rows.append(r)

        print(f"{win:<9} {dt:<8}{est:<13}{r['mean_quality']:>6.2f}"
              f"{r['contrast_real']:>9.2f}{r['null_mean']:>8.2f}{r['ratio_paper']:>7.2f}"
              f"{r['z_score']:>7.1f}{r['p_value']:>8.3f}"
              f"{('ok' if r['pos_ctrl_ok'] else 'FAIL'):>7}"
              f"{('yes' if r['surface_pinned'] else 'no'):>6}{r['leakage']:>6.2f}   "
              f"{('DETECT' if r['PAPER_DETECT'] else 'no'):<9}"
              f"{('DETECT' if r['DETECTION'] else 'no')}")

    print("-" * 118)
    n_paper = sum(r["PAPER_DETECT"] for r in rows)
    n_perm = sum(r["DETECTION"] for r in rows)
    n_pc = sum(r["pos_ctrl_ok"] for r in rows)
    ratios = np.array([r["ratio_paper"] for r in rows])
    print(f"SUMMARY over {len(rows)} configurations:")
    print(f"  paper criterion (contrast > 5x single shuffled null): {n_paper}/{len(rows)} detect")
    print(f"  permutation criterion (p < 0.05, {n_perm_used} perms):        {n_perm}/{len(rows)} detect")
    print(f"  injected positive control recovered:                  {n_pc}/{len(rows)}")
    print(f"  contrast ratio across configurations: min={ratios.min():.2f} "
          f"median={np.median(ratios):.2f} max={ratios.max():.2f} "
          f"(spread {ratios.max()-ratios.min():.2f})")

    verdicts = set(r["PAPER_DETECT"] for r in rows)
    if len(verdicts) == 1:
        print(f"  -> VERDICT IS INVARIANT across every window, precision and coregistrator"
              f" tested: {'DETECT' if verdicts.pop() else 'no detection'}.")
    else:
        print("  -> !! The verdict CHANGES with configuration. This is the outcome that would")
        print("     vindicate the objection. Inspect the disagreeing rows before reporting.")
    if n_pc < len(rows):
        print("  -> !! A positive control FAILED somewhere: that configuration is genuinely")
        print("     broken and its null result carries no weight. Report it as such.")
    return rows


# ===========================================================================
# 6. HARNESS SELF-TEST (no data, no network)
# ===========================================================================
def _speckle(N, frac, rng):
    b = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
    f = np.fft.fftfreq(N)
    m = ((np.abs(f)[:, None] < frac) & (np.abs(f)[None, :] < frac)).astype(float)
    return np.fft.ifft2(np.fft.fft2(b) * m)


def selftest():
    rng = np.random.default_rng(0)
    ok = {}

    print("[A] windowed decomposition reproduces the repo's function exactly (hann/complex128):")
    from subaperture import decompose_subapertures as repo_decomp
    slc = _speckle(128, 0.35, rng)
    L0, c0 = repo_decomp(slc, n_sub=7, overlap=0.5, axis=1)
    L1, c1 = decompose_subapertures_w(slc, n_sub=7, overlap=0.5, axis=1,
                                      window="hann", dtype=np.complex128)
    d = np.max(np.abs(L0 - L1))
    ok["A"] = d < 1e-12 and np.allclose(c0, c1)
    print(f"   max |repo - sweep| = {d:.2e}  -> {'PASS' if ok['A'] else 'FAIL'}")

    print("\n[B] every estimator recovers known sub-pixel shifts in the repo's sign convention:")
    base = _speckle(128, 0.25, rng)
    ok["B"] = True
    for name in ESTIMATORS:
        errs = []
        for (sy, sx) in [(0.0, 2.0), (0.0, -1.4), (0.0, 0.6)]:
            mov = fourier_shift(base, sy, sx)
            ry, rx = ESTIMATORS[name](np.abs(base), np.abs(mov))
            errs.append(abs(rx - sx))
        e = max(errs)
        # optical flow is a dense/regularised estimator: looser but must still track sign
        thr = 0.60 if name == "opticalflow" else 0.20
        good = e < thr
        ok["B"] &= good
        print(f"   {name:<12} max azimuth err {e:.3f} px (thr {thr})  -> {'PASS' if good else 'FAIL'}")

    print("\n[E] the float32 arm is genuinely single-precision (not a silent no-op):")
    # numpy.fft would promote to double and make the float32 arm meaningless. If this
    # FAILS, every float32 row in the sweep is fake and must not be reported.
    L64, _ = decompose_subapertures_w(slc, n_sub=9, overlap=0.8, window="hann",
                                      dtype=np.complex128)
    L32, _ = decompose_subapertures_w(slc, n_sub=9, overlap=0.8, window="hann",
                                      dtype=np.complex64)
    is64 = L64.dtype == np.complex128
    is32 = L32.dtype == np.complex64
    diff = float(np.max(np.abs(L64 - L32)) / (np.max(np.abs(L64)) + 1e-30))
    ok["E"] = is64 and is32 and (1e-9 < diff < 1e-2)
    print(f"   dtypes {L64.dtype}/{L32.dtype}; relative divergence = {diff:.2e} "
          f"(want 1e-9..1e-2)  -> {'PASS' if ok['E'] else 'FAIL'}")

    print("\n[C] permutation p-value is calibrated (uniform under the null):")
    # observations that are pure noise -> p should be ~uniform, not systematically small
    ps = []
    for s in range(12):
        r = np.random.default_rng(100 + s)
        obs = r.standard_normal((24, 9))
        zg = np.linspace(0, 9 * DZ_TARGET / 2, 300)
        T = tomogram_from_observations(obs, zg)
        nulls = permutation_null(obs, zg, 100, seed=s)
        ps.append((1 + int(np.sum(nulls >= contrast(T)))) / 101)
    frac_sig = np.mean(np.array(ps) < 0.05)
    ok["C"] = frac_sig <= 0.25          # 12 trials: allow up to 3 by chance
    print(f"   {len(ps)} noise-only trials, fraction with p<0.05 = {frac_sig:.2f} "
          f"(want <=0.25)  -> {'PASS' if ok['C'] else 'FAIL'}")
    print(f"   p-values: {np.round(ps,3).tolist()}")

    print("\n[D] the harness CAN detect: injected reflector must come back p<0.05:")
    r = np.random.default_rng(5)
    obs = 0.02 * r.standard_normal((24, 9))
    zg = np.linspace(0, 9 * DZ_TARGET / 2, 300)
    _, Kz = steering(9, zg)
    obs = obs + 1.0 * np.cos(Kz * (0.5 * zg[-1]))
    res = evaluate(obs, None, zg, n_perm=200, seed=1)
    ok["D"] = res["p_value"] < 0.05
    print(f"   p = {res['p_value']:.4f}, z = {res['z_score']:.1f}  -> {'PASS' if ok['D'] else 'FAIL'}")
    print("   (a sweep that cannot detect anything would prove nothing)")

    print("\n" + "=" * 60)
    allok = all(ok.values())
    print("SENSITIVITY-HARNESS SELF-TEST:", "PASS" if allok else "FAIL", ok)
    print("=" * 60)
    return allok


# ===========================================================================
# 7. Entry points
# ===========================================================================
def synthetic_scene(N=512, seed=3, kind="blobs"):
    """Synthetic SLCs containing NO subsurface reflector. The correct answer for both
    is 'no detection'; anything else is a false positive of the test procedure.

      kind='speckle' — homogeneous correlated speckle only. The cleanest possible
                       negative control: no structure of any kind.
      kind='blobs'   — speckle modulated by bright surface structure, which imposes a
                       smooth look-dependent shift. Tests whether a purely SURFACE
                       feature can beat the shuffle null and the guards.
    """
    rng = np.random.default_rng(seed)
    slc = _speckle(N, 0.30, rng)
    if kind == "speckle":
        return slc
    yy, xx = np.mgrid[0:N, 0:N]
    bright = 1.0 + 3.0 * np.exp(-(((xx - N*0.35)**2 + (yy - N*0.5)**2) / (2 * (N*0.06)**2)))
    bright += 2.0 * np.exp(-(((xx - N*0.7)**2 + (yy - N*0.45)**2) / (2 * (N*0.05)**2)))
    return slc * bright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--synthetic", action="store_true",
                    help="run the sweep on a synthetic no-target scene")
    ap.add_argument("--scene", default="blobs", choices=["blobs", "speckle"],
                    help="synthetic scene type (see synthetic_scene docstring)")
    ap.add_argument("--sicd", help="real SICD .nitf")
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--n-patch", type=int, default=24)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--windows", nargs="*", default=["hann", "hamming", "blackman", "rect"])
    ap.add_argument("--precisions", nargs="*", default=["float64", "float32"])
    ap.add_argument("--estimators", nargs="*", default=["phasecorr", "upsampdft", "ncc"],
                    help="add 'opticalflow' for the GeFolki-lineage estimator (slow)")
    ap.add_argument("--out", default="runs/sensitivity_sweep.json")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    if args.sicd:
        from sarpy.io.complex.converter import open_complex
        reader = open_complex(args.sicd)
        R, C = reader.data_size
        r0, c0 = R//2 - args.crop//2, C//2 - args.crop//2
        print(f"Loading {args.crop}x{args.crop} crop from {os.path.basename(args.sicd)} ({R}x{C})")
        slc = reader[r0:r0+args.crop, c0:c0+args.crop]
        label = os.path.basename(args.sicd)
    elif args.synthetic:
        slc = synthetic_scene(N=args.crop, kind=args.scene)
        label = (f"SYNTHETIC no-target scene [{args.scene}]"
                 + (" — speckle + bright surface structure" if args.scene == "blobs"
                    else " — homogeneous speckle, no structure at all"))
    else:
        ap.error("choose --selftest, --synthetic, or --sicd")

    rows = run_sweep(slc, args.n_sub, args.patch, args.n_patch, args.overlap,
                     args.windows, args.precisions, args.estimators,
                     args.n_perm, args.seed, label)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(dict(label=label, n_sub=args.n_sub, patch=args.patch,
                       n_patch=args.n_patch, overlap=args.overlap,
                       n_perm=args.n_perm, seed=args.seed, rows=rows), f, indent=2)
    print(f"\nresults -> {args.out}")


if __name__ == "__main__":
    main()
