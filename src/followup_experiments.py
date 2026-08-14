#!/usr/bin/env python3
"""
followup_experiments.py — close the four open criticisms from adversarial review.

Each experiment answers a specific objection raised against
docs/SENSITIVITY_RESPONSE_BIONDI.md on 29 July 2026.

  E1  SCALE-INVARIANT n_sub COMPARISON
      Objection: `zgrid = linspace(0, n_sub*DZ_TARGET/2, 300)` makes the depth axis
      extent scale with n_sub while the bin count stays fixed, so contrast
      (peak/median) is not comparable across n_sub. The 194x claim was withdrawn.
      Fix: evaluate every n_sub on ONE FIXED depth window (0 .. 11*DZ_TARGET/2),
      which lies inside the unambiguous range of every configuration tested, with a
      fixed bin count. Report both the native and the fixed-window statistic so the
      size of the confound is visible rather than argued about.

  E2  A GUARD THAT DOES NOT CHANGE MEANING WHEN THE AXIS STRETCHES
      Objection: shallow_pinned() flags a peak in the shallowest 5% OF THE AXIS. The
      same 3 m feature is flagged at n_sub=128 (2.2% of a 135 m axis) and clears at
      n_sub=32 (8.9% of a 33.8 m axis). The cutoff is an unjustified constant.
      Fix: flag on ABSOLUTE depth, in units of the depth-resolution cell dz_phys =
      (v/f)*R/(2A). A peak within `--guard-cells` cells of the surface is
      surface-pinned regardless of how long the axis is.

  E3  A CORRECTLY-SPECIFIED NULL
      Objection: shuffling look order destroys the look-to-look smoothness that 80%
      sub-aperture overlap guarantees even under pure speckle, so the shuffle null is
      mis-specified and the permutation p-value is anti-conservative.
      Fix: the ALIGNMENT null. Compute each patch's tomogram, then circularly shift
      each patch's depth profile by an independent random offset before summing. This
      preserves every patch's own spectral shape EXACTLY — smoothness, peakedness,
      surface concentration — and destroys only the agreement between patches about
      WHICH depth. That is the scientific question: do independent patches concur on a
      depth? Contrast under this null is the honest reference.

  E4  IS THE BUTTE WINDOW GRADIENT INTER-LOOK LEAKAGE?
      Objection: the leakage reading is an inference. Competing explanation: stronger
      tapers cut each look's effective bandwidth, lowering SNR, so weaker residuals
      under Blackman/Hann are expected even for a real signal.
      Fix: measure the correlation structure of the DETRENDED RESIDUAL TRAJECTORIES
      that actually enter the inverter (not the complex looks, not the magnitude
      images) as a function of window, and test whether it tracks the statistic. If
      the statistic rises with inter-look correlation, leakage is supported. If it
      rises while correlation is flat, it is not.

Usage
-----
  python3 src/followup_experiments.py --selftest
  python3 src/followup_experiments.py --sicd data/<komati>_SICD.nitf --experiment nsub
  python3 src/followup_experiments.py --sicd data/<butte>_SICD.nitf  --experiment leakage
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import (DZ_TARGET, steering, analytic1d, contrast,
                      tomogram_from_observations, metric_depth_axis,
                      surface_brightness, leakage_correlation, shallow_pinned)
from sensitivity_sweep import patch_observations_cfg, WINDOWS

# Fixed comparison window: the unambiguous half-range of the SMALLEST n_sub tested,
# so every configuration is evaluated over a depth interval it can actually resolve.
NSUB_REF = 11
ZGRID_FIXED = np.linspace(0, NSUB_REF * DZ_TARGET / 2, 300)


# ===========================================================================
# E3 — the alignment null
# ===========================================================================
def per_patch_tomograms(obs, zgrid):
    A, _ = steering(obs.shape[1], zgrid)
    return np.array([np.abs(A.conj().T @ analytic1d(r)) ** 2 for r in obs])


def alignment_null(obs, zgrid, n_perm=200, seed=0):
    """Preserve every patch's own depth profile exactly; randomise only the depth at
    which each patch's profile sits. Destroys cross-patch agreement, nothing else."""
    rng = np.random.default_rng(seed)
    Tp = per_patch_tomograms(obs, zgrid)
    nz = Tp.shape[1]
    out = np.empty(n_perm)
    for i in range(n_perm):
        shifted = np.array([np.roll(t, int(rng.integers(nz))) for t in Tp])
        out[i] = contrast(shifted)
    return out


def shuffle_null(obs, zgrid, n_perm=200, seed=0):
    """The paper's original null, for side-by-side comparison."""
    rng = np.random.default_rng(seed)
    out = np.empty(n_perm)
    for i in range(n_perm):
        sh = np.array([r[rng.permutation(len(r))] for r in obs])
        out[i] = contrast(tomogram_from_observations(sh, zgrid))
    return out


# ===========================================================================
# E2 — a scale-stable surface-pinning guard
# ===========================================================================
def peak_depth_m(T, zgrid, dz_phys):
    z_m = zgrid * (dz_phys / DZ_TARGET)
    return float(z_m[int(np.argmax(T.sum(0)))])


def pinned_absolute(T, zgrid, dz_phys, guard_cells=2.0):
    """Surface-pinned iff the peak lies within `guard_cells` depth-resolution cells
    of the surface. Independent of how long the depth axis happens to be."""
    pk = peak_depth_m(T, zgrid, dz_phys)
    return bool(pk <= guard_cells * dz_phys), pk


# ===========================================================================
# E4 — inter-look correlation of the residual trajectories
# ===========================================================================
def interlook_autocorr(obs, max_lag=3):
    """Mean autocorrelation of the detrended residual trajectories across look index.
    Returns (lag-1, lag-2). Leakage between overlapping sub-apertures should raise these."""
    n_look = obs.shape[1]
    rhos = np.zeros(max_lag + 1)
    counts = 0
    for x in obs:
        x = x - x.mean()
        d = float(x @ x)
        if d <= 0:
            continue
        counts += 1
        for k in range(1, max_lag + 1):
            rhos[k] += float(x[:-k] @ x[k:]) / d
    if counts == 0:
        return float("nan"), float("nan")
    rhos /= counts
    # Bartlett-style effective sample size along the look axis
    # NB: an effective-sample-size estimate is unstable here — deg-2 detrending on a
    # short look axis drives lag-2/3 negative and the Bartlett denominator through zero.
    # Report the raw lags instead; they are what the leakage hypothesis predicts.
    return float(rhos[1]), float(rhos[2])


# ===========================================================================
# E1 + E2 — the n_sub experiment
# ===========================================================================
def experiment_nsub(slc, counts, patch, n_patch, overlap, window, estimator,
                    n_perm, guard_cells, velocity, f_invest, range_km, aperture_km,
                    label):
    H, W = slc.shape
    row = H // 2 - patch // 2
    cols = np.linspace(0, W - patch, n_patch).astype(int)
    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)

    print(f"\n{'='*112}")
    print(f"E1+E2+E3 — sub-aperture count, on a FIXED depth window — {label}")
    print(f"  window={window} coregistrator={estimator} patch={patch} n_patch={n_patch} "
          f"overlap={overlap}")
    print(f"  fixed comparison window: 0–{ZGRID_FIXED[-1]*(dz_phys/DZ_TARGET):.1f} m "
          f"(unambiguous at every n_sub tested); dz_phys={dz_phys:.2f} m")
    print(f"  guard: peak within {guard_cells:g} depth cells ({guard_cells*dz_phys:.1f} m) "
          f"of the surface = surface-pinned")
    print(f"{'='*112}")
    print(f"{'n_sub':>6}{'native C':>10}{'fixedC':>9}{'shufNull':>10}{'alignNull':>11}"
          f"{'C/shuf':>9}{'C/align':>9}{'peak m':>9}{'old 5%':>9}{'new abs':>9}  verdict")
    print("-" * 112)

    rows = []
    for n in counts:
        obs, quals = patch_observations_cfg(slc, cols, row, patch, n, overlap,
                                            window, np.complex128, estimator)
        z_native = np.linspace(0, n * DZ_TARGET / 2, 300)
        T_native = tomogram_from_observations(obs, z_native)
        T_fixed = tomogram_from_observations(obs, ZGRID_FIXED)

        c_native = contrast(T_native)
        c_fixed = contrast(T_fixed)
        shuf = shuffle_null(obs, ZGRID_FIXED, n_perm=n_perm, seed=0)
        algn = alignment_null(obs, ZGRID_FIXED, n_perm=n_perm, seed=0)
        r_shuf = c_fixed / (np.median(shuf) + 1e-12)
        r_algn = c_fixed / (np.median(algn) + 1e-12)

        old_pin, old_frac, _ = shallow_pinned(T_native)
        new_pin, pk_m = pinned_absolute(T_native, z_native, dz_phys, guard_cells)

        verdict = ("surface-pinned artifact" if new_pin else
                   ("above alignment null → investigate" if r_algn > 5 else
                    "no detection"))
        rows.append(dict(n_sub=n, c_native=float(c_native), c_fixed=float(c_fixed),
                         shuf_med=float(np.median(shuf)), align_med=float(np.median(algn)),
                         ratio_shuffle=float(r_shuf), ratio_align=float(r_algn),
                         peak_m=pk_m, old_pinned=bool(old_pin),
                         old_peak_frac=float(old_frac), new_pinned=bool(new_pin),
                         quality=float(np.mean(quals)), verdict=verdict))
        print(f"{n:>6}{c_native:>10.2f}{c_fixed:>9.2f}{np.median(shuf):>10.2f}"
              f"{np.median(algn):>11.2f}{r_shuf:>9.2f}{r_algn:>9.2f}{pk_m:>9.1f}"
              f"{('PIN' if old_pin else 'clear'):>9}{('PIN' if new_pin else 'clear'):>9}"
              f"  {verdict}")

    print("-" * 112)
    cn = np.array([r["c_native"] for r in rows]); cf = np.array([r["c_fixed"] for r in rows])
    ra = np.array([r["ratio_align"] for r in rows])
    print(f"native contrast spread : {cn.min():.2f} – {cn.max():.2f}  ({cn.max()/cn.min():.1f}x)"
          f"   <- NOT comparable across n_sub")
    print(f"fixed-window spread    : {cf.min():.2f} – {cf.max():.2f}  ({cf.max()/cf.min():.1f}x)"
          f"   <- comparable; this is the honest number")
    print(f"vs alignment null      : {ra.min():.2f} – {ra.max():.2f}"
          f"   detections at >5x: {int((ra>5).sum())}/{len(ra)}")
    old_flags = sum(r["old_pinned"] for r in rows); new_flags = sum(r["new_pinned"] for r in rows)
    print(f"surface-pinning guard  : old 5%-of-axis rule flags {old_flags}/{len(rows)}; "
          f"absolute {guard_cells:g}-cell rule flags {new_flags}/{len(rows)}")
    if new_flags > old_flags:
        print("  -> the absolute guard catches shallow peaks the fractional rule let through.")
    return rows


# ===========================================================================
# E5 — is the peak depth a property of the METHOD or of the PATCH GEOMETRY?
#
# Every result so far used one geometry: 512x512 centre crop, 64-px patches,
# 24 patches, 0.8 overlap. The peak lands ~1.2-1.9 depth cells down at every
# site and every n_sub. Before claiming that is a property of the method, vary
# the geometry one factor at a time and see whether the peak cell moves.
#
#   peak cell stays put  -> the artifact is general; the depth is pipeline-fixed
#   peak cell tracks geometry -> we have identified the MECHANISM, which is
#                                a stronger result, not a weaker one
# ===========================================================================
def experiment_geometry(load_crop, combos, n_sub, window, estimator, n_perm,
                        guard_cells, velocity, f_invest, range_km, aperture_km,
                        label):
    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z_native = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    axis_m = z_native[-1] * (dz_phys / DZ_TARGET)

    print(f"\n{'='*118}")
    print(f"E5 — does the peak depth move when the PATCH GEOMETRY changes? — {label}")
    print(f"  n_sub={n_sub} window={window} coregistrator={estimator} "
          f"dz_phys={dz_phys:.2f} m  axis=0–{axis_m:.1f} m")
    print(f"  guard: peak within {guard_cells:g} cells ({guard_cells*dz_phys:.1f} m) = surface-pinned")
    print(f"  baseline geometry is crop=512 patch=64 n_patch=24 overlap=0.8")
    print(f"{'='*118}")
    print(f"{'varying':<12}{'crop':>6}{'patch':>7}{'nPatch':>8}{'ovl':>6}"
          f"{'C':>9}{'alignN':>9}{'C/align':>9}{'peak m':>9}{'peak cells':>12}"
          f"{'%axis':>8}{'guard':>8}")
    print("-" * 118)

    rows = []
    cache = {}
    for varying, crop, patch, n_patch, overlap in combos:
        if patch >= crop:
            print(f"{varying:<12}{crop:>6}{patch:>7}{n_patch:>8}{overlap:>6.2f}"
                  f"{'  skipped: patch >= crop':>50}")
            continue
        if crop not in cache:
            cache[crop] = load_crop(crop)
        slc = cache[crop]
        H, W = slc.shape
        row0 = H // 2 - patch // 2
        cols = np.linspace(0, W - patch, n_patch).astype(int)

        obs, quals = patch_observations_cfg(slc, cols, row0, patch, n_sub, overlap,
                                            window, np.complex128, estimator)
        T = tomogram_from_observations(obs, z_native)
        c = float(contrast(T))
        algn = alignment_null(obs, z_native, n_perm=n_perm, seed=0)
        r_algn = c / (float(np.median(algn)) + 1e-12)
        pinned, pk_m = pinned_absolute(T, z_native, dz_phys, guard_cells)
        pk_cells = pk_m / dz_phys
        pct = 100.0 * pk_m / axis_m if axis_m > 0 else float("nan")

        rows.append(dict(varying=varying, crop=crop, patch=patch, n_patch=n_patch,
                         overlap=overlap, contrast=c, align_med=float(np.median(algn)),
                         ratio_align=float(r_algn), peak_m=float(pk_m),
                         peak_cells=float(pk_cells), peak_pct_axis=float(pct),
                         pinned=bool(pinned), quality=float(np.mean(quals))))
        print(f"{varying:<12}{crop:>6}{patch:>7}{n_patch:>8}{overlap:>6.2f}"
              f"{c:>9.2f}{np.median(algn):>9.2f}{r_algn:>9.2f}{pk_m:>9.1f}"
              f"{pk_cells:>12.2f}{pct:>7.1f}%{('PIN' if pinned else 'clear'):>8}")

    print("-" * 118)
    if rows:
        pc = np.array([r["peak_cells"] for r in rows])
        ra = np.array([r["ratio_align"] for r in rows])
        print(f"peak depth in CELLS    : {pc.min():.2f} – {pc.max():.2f}  "
              f"(spread {pc.max()/max(pc.min(),1e-9):.2f}x, sd {pc.std():.2f})")
        print(f"vs alignment null      : {ra.min():.2f} – {ra.max():.2f}"
              f"   detections at >5x: {int((ra>5).sum())}/{len(ra)}")
        print(f"surface-pinned         : {sum(r['pinned'] for r in rows)}/{len(rows)}")
        # per-factor drift: does any single factor move the peak?
        print("\nper-factor peak-cell range (is the peak tracking any one knob?):")
        for f in sorted(set(r["varying"] for r in rows)):
            sub = [r["peak_cells"] for r in rows if r["varying"] == f]
            print(f"  {f:<12} {min(sub):.2f} – {max(sub):.2f}   (n={len(sub)})")
        if pc.max() - pc.min() < 1.0:
            print("\n  -> peak cell is STABLE across geometry: the depth is a property of the\n"
                  "     method, not of the patch layout. The invariance claim survives.")
        else:
            print("\n  -> peak cell MOVES with geometry. Identify which factor drives it: that\n"
                  "     is the mechanism generating the artifact, and it is the better result.")
    return rows


# ===========================================================================
# E6 — does the inverter need DATA to produce its peak?
#
# E5 showed the peak sits at ~1.7 depth cells regardless of site, sensor,
# sub-aperture count or patch geometry. If that position is a property of the
# inversion rather than of the scene, then feeding the inverter synthetic
# noise -- no satellite data at all -- must place the peak in the same band.
#
#   same band  -> on the ONLY quantity carrying the depth claim, real data is
#                 indistinguishable from noise
#   different  -> something in the real data does influence the peak, and the
#                 invariance argument needs qualifying
#
# Two noise models are used. White noise is the strict null. AR(1) noise with
# the lag-1 correlation measured from the real trajectories is the fair null:
# 80% sub-aperture overlap guarantees look-to-look smoothness even under pure
# noise, so white noise alone would be an unrealistically easy target.
# ===========================================================================
def experiment_noise(slc, n_sub, patch, n_patch, overlap, window, estimator,
                     n_trials, guard_cells, velocity, f_invest, range_km,
                     aperture_km, label, seed=0):
    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z = np.linspace(0, n_sub * DZ_TARGET / 2, 300)

    H, W = slc.shape
    row0 = H // 2 - patch // 2
    cols = np.linspace(0, W - patch, n_patch).astype(int)

    # RAW trajectories, before the degree-2 detrend the pipeline applies.
    # The AR coefficient must be measured HERE: after detrending, a deg-2 fit on
    # an ~11-point series forces negative correlation, so the post-detrend value
    # (~0.009 on Bingham) badly understates the real look-to-look smoothness
    # (~0.431 raw). Using the post-detrend number collapses the "fair" null into
    # the white-noise null and makes the test far too easy.
    from micromotion import detrend as _detrend
    from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e
    looks, _ = decompose_subapertures_w(slc, n_sub=n_sub, overlap=overlap, axis=1,
                                        window=window, dtype=np.complex128)
    raw = []
    for cc in cols:
        lp = looks[:, row0:row0 + patch, cc:cc + patch]
        traj, _q = adjacent_trajectory_e(lp, estimator=estimator, dtype=np.complex128)
        raw.append(np.asarray(traj, dtype=float))
    raw = np.array(raw)
    rho1_raw, _ = interlook_autocorr(raw)

    obs = np.array([_detrend(t, deg=2) for t in raw], dtype=float)
    T_real = tomogram_from_observations(obs, z)
    pk_real = peak_depth_m(T_real, z, dz_phys) / dz_phys
    c_real = float(contrast(T_real))
    rho1, rho2 = interlook_autocorr(obs)

    # the band spanned by every real run in this study (5 sites, 2 sensors,
    # 8 sub-aperture counts, 13 geometries, 2 constant sets)
    BAND = (1.2, 1.9)

    print(f"\n{'='*104}")
    print(f"E6 — does the peak survive when the DATA is replaced by noise? — {label}")
    print(f"  n_sub={n_sub} patch={patch} n_patch={n_patch} overlap={overlap} "
          f"window={window} coreg={estimator}")
    print(f"  dz_phys={dz_phys:.2f} m   trials={n_trials}   seed={seed}")
    print(f"  real data: contrast={c_real:.2f}  peak={pk_real:.2f} cells")
    print(f"  lag-1 autocorr:  RAW trajectories = {rho1_raw:.3f}   "
          f"after deg-2 detrend = {rho1:.3f}")
    print(f"  NOTE: synthetic series are generated at the RAW correlation and then put")
    print(f"        through the SAME deg-2 detrend as the real data, so the comparison")
    print(f"        is like-for-like. A deg-2 fit on a short series forces negative")
    print(f"        correlation, so post-detrend values must be read against the noise")
    print(f"        reference, not against zero.")
    print(f"  reference band from every real run in this study: "
          f"{BAND[0]:.1f}–{BAND[1]:.1f} cells")
    print(f"{'='*104}")
    print(f"{'input':<22}{'peak median':>13}{'5-95 pct':>18}{'sd':>8}"
          f"{'in band':>10}{'contrast med':>14}")
    print("-" * 104)

    rng = np.random.default_rng(seed)
    sd_raw = float(np.std(raw))

    def _ar(a_, shape, rng_):
        e = rng_.normal(0.0, 1.0, shape)
        if a_ <= 0:
            return e
        x = np.empty_like(e)
        x[:, 0] = e[:, 0]
        for k in range(1, shape[1]):
            x[:, k] = a_ * x[:, k - 1] + np.sqrt(1.0 - a_ * a_) * e[:, k]
        return x

    # Calibrate the AR coefficient so the SYNTHETIC series reproduces the OBSERVED
    # sample lag-1, rather than simply setting a = rho1_raw. Sample autocorrelation
    # on an ~11-point series is biased low, so a = 0.43 yields a sample lag-1 of
    # only ~0.25 — which would leave the "fair" null still easier than reality.
    cal_rng = np.random.default_rng(seed + 1)
    a, best = 0.0, 1e9
    for cand in np.linspace(0.0, 0.95, 20):
        m = np.mean([interlook_autocorr(_ar(cand, raw.shape, cal_rng))[0]
                     for _ in range(30)])
        if abs(m - rho1_raw) < best:
            a, best = float(cand), abs(m - rho1_raw)
    print(f"  AR coefficient calibrated to a={a:.2f} so synthetic sample lag-1 "
          f"matches the observed {rho1_raw:.3f}")
    out = {}
    for kind in ("white -> detrend", f"AR(1) r={a:.2f} -> detrend"):
        pks = np.empty(n_trials)
        cs = np.empty(n_trials)
        for i in range(n_trials):
            e = sd_raw * _ar(a if kind.startswith("AR(1)") else 0.0, raw.shape, rng)
            e = np.array([_detrend(t, deg=2) for t in e], dtype=float)
            T = tomogram_from_observations(e, z)
            pks[i] = peak_depth_m(T, z, dz_phys) / dz_phys
            cs[i] = float(contrast(T))
        frac = float(np.mean((pks >= BAND[0]) & (pks <= BAND[1])))
        out[kind] = dict(peaks=pks.tolist(), contrasts=cs.tolist(),
                         median=float(np.median(pks)), sd=float(pks.std()),
                         p05=float(np.percentile(pks, 5)),
                         p95=float(np.percentile(pks, 95)),
                         in_band=frac, contrast_median=float(np.median(cs)))
        print(f"{kind:<22}{np.median(pks):>13.2f}"
              f"{f'{np.percentile(pks,5):.2f} – {np.percentile(pks,95):.2f}':>18}"
              f"{pks.std():>8.2f}{100*frac:>9.0f}%{np.median(cs):>14.2f}")

    print(f"{'REAL DATA':<22}{pk_real:>13.2f}{'—':>18}{'—':>8}"
          f"{'100%' if BAND[0] <= pk_real <= BAND[1] else '—':>10}{c_real:>14.2f}")
    print("-" * 104)

    best = max(out.values(), key=lambda d: d["in_band"])["in_band"]
    if best > 0.5:
        print("  -> The inverter places its peak in the same depth band with NO DATA AT ALL.")
        print("     On the quantity that carries the depth claim, real scenes are")
        print("     indistinguishable from noise. The depth is generated by the method.")
    else:
        print("  -> Noise does NOT reproduce the peak position. Something in the real")
        print("     data influences it; the invariance claim must be qualified.")
    return dict(real=dict(peak_cells=float(pk_real), contrast=c_real,
                          lag1_raw=float(rho1_raw), lag1_detrended=float(rho1),
                          lag2_detrended=float(rho2)),
                band=list(BAND), trials=n_trials, models=out)


# ===========================================================================
# E7 — the PRINCIPLED null: derive the correlation instead of fitting it
#
# E6 matched an AR(1) coefficient to the observed lag-1. That is open to the
# charge of tuning a null until it reproduces the observation -- the exact
# move this study criticises. E7 removes the fitted parameter entirely.
#
# Feed COMPLEX WHITE NOISE -- a synthetic SLC with no scene, no structure,
# nothing -- through the IDENTICAL pipeline: the same sub-aperture
# decomposition at the same overlap, the same coregistration, the same
# degree-2 detrend, the same inversion. The look-to-look correlation then
# EMERGES from the overlap rather than being supplied.
#
# Sweeping overlap turns the mechanism from an assertion into a measurement:
# if the peak converges on ~1.7 cells and the contrast rises toward the real
# value as overlap increases, the artifact is produced by spectral overlap
# and nothing else.
# ===========================================================================
def experiment_synthetic(n_sub, patch, n_patch, overlaps, window, estimator,
                         n_trials, guard_cells, velocity, f_invest, range_km,
                         aperture_km, canvas, real_peak=None, real_contrast=None,
                         seed=0):
    from micromotion import detrend as _detrend
    from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e

    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    rng = np.random.default_rng(seed)

    print(f"\n{'='*104}")
    print(f"E7 — complex white noise through the IDENTICAL pipeline (no scene at all)")
    print(f"  canvas={canvas}x{canvas} n_sub={n_sub} patch={patch} n_patch={n_patch} "
          f"window={window} coreg={estimator}")
    print(f"  dz_phys={dz_phys:.2f} m   trials per overlap={n_trials}   seed={seed}")
    print(f"  NOTHING is fitted here: the look-to-look correlation emerges from the")
    print(f"  overlap parameter, it is not supplied.")
    if real_peak is not None:
        print(f"  real-data reference: peak={real_peak:.2f} cells  contrast={real_contrast:.2f}")
    print(f"{'='*104}")
    print(f"{'overlap':>9}{'raw lag-1':>12}{'peak median':>14}{'5-95 pct':>18}"
          f"{'sd':>8}{'contrast med':>14}{'pinned':>9}")
    print("-" * 104)

    rows = []
    for ov in overlaps:
        pks, cs, lags = [], [], []
        for _ in range(n_trials):
            slc = (rng.normal(0, 1, (canvas, canvas))
                   + 1j * rng.normal(0, 1, (canvas, canvas))).astype(np.complex128)
            looks, _ = decompose_subapertures_w(slc, n_sub=n_sub, overlap=ov, axis=1,
                                                window=window, dtype=np.complex128)
            row0 = canvas // 2 - patch // 2
            cols = np.linspace(0, canvas - patch, n_patch).astype(int)
            raw = []
            for cc in cols:
                lp = looks[:, row0:row0 + patch, cc:cc + patch]
                traj, _q = adjacent_trajectory_e(lp, estimator=estimator,
                                                 dtype=np.complex128)
                raw.append(np.asarray(traj, dtype=float))
            raw = np.array(raw)
            lags.append(interlook_autocorr(raw)[0])
            obs = np.array([_detrend(t, deg=2) for t in raw], dtype=float)
            T = tomogram_from_observations(obs, z)
            pks.append(peak_depth_m(T, z, dz_phys) / dz_phys)
            cs.append(float(contrast(T)))
        pks, cs = np.array(pks), np.array(cs)
        pinned = float(np.mean(pks <= guard_cells))
        rows.append(dict(overlap=float(ov), lag1_raw=float(np.mean(lags)),
                         peak_median=float(np.median(pks)),
                         p05=float(np.percentile(pks, 5)),
                         p95=float(np.percentile(pks, 95)),
                         peak_sd=float(pks.std()),
                         contrast_median=float(np.median(cs)),
                         pinned_frac=pinned))
        print(f"{ov:>9.2f}{np.mean(lags):>12.3f}{np.median(pks):>14.2f}"
              f"{f'{np.percentile(pks,5):.2f} – {np.percentile(pks,95):.2f}':>18}"
              f"{pks.std():>8.2f}{np.median(cs):>14.2f}{100*pinned:>8.0f}%")

    print("-" * 104)
    if real_peak is not None:
        print(f"{'REAL':>9}{0.431:>12.3f}{real_peak:>14.2f}{'—':>18}{'—':>8}"
              f"{real_contrast:>14.2f}{'—':>9}")
        print("-" * 104)
    hi = [r for r in rows if r["overlap"] >= 0.79]
    lo = [r for r in rows if r["overlap"] <= 0.01]
    if hi and lo:
        pk_lo, pk_hi = lo[0]["peak_median"], hi[0]["peak_median"]
        c_lo, c_hi = lo[0]["contrast_median"], hi[0]["contrast_median"]
        print(f"\n  overlap 0.00 -> peak {pk_lo:.2f} cells, contrast {c_lo:.2f}, "
              f"raw lag-1 {lo[0]['lag1_raw']:.3f}")
        print(f"  overlap 0.80 -> peak {pk_hi:.2f} cells, contrast {c_hi:.2f}, "
              f"raw lag-1 {hi[0]['lag1_raw']:.3f}")

        if real_peak is not None and abs(pk_hi - real_peak) < 0.3:
            print("\n  -> Pure noise reproduces the real peak position with NOTHING FITTED.")
        # Does the peak depend on overlap at all? This is the question the first
        # version of this verdict failed to ask, and it produced a wrong conclusion.
        if abs(pk_hi - pk_lo) < 0.3:
            print("\n  -> The peak is present at ZERO overlap and barely moves across the")
            print("     whole range. Spectral overlap is therefore NOT the source of the")
            print("     peak. Note the raw lag-1 is already high at overlap 0.00 — the")
            print("     look-to-look correlation does not come from the overlap either.")
            print("     Candidate: adjacent_trajectory_e returns np.cumsum(inc), so the")
            print("     trajectory is a random walk and smooth by construction.")
            print("     Run --experiment increments (E8) to test that directly.")
        else:
            print("\n  -> The peak DOES move with overlap; spectral overlap is implicated.")
        if c_hi > c_lo * 1.15:
            print(f"\n  -> Overlap does raise the CONTRAST ({c_lo:.2f} -> {c_hi:.2f}), so it")
            print("     amplifies the artifact without creating it.")
        for r in rows:
            if r["contrast_median"] > 5.0:
                print(f"\n  -> WARNING: at overlap {r['overlap']:.2f} pure noise reaches "
                      f"contrast {r['contrast_median']:.2f}, above the manuscript's own")
                print("     >5x detection rule. The method returns a formal detection on")
                print("     data containing nothing.")
    return rows


# ===========================================================================
# E8 — is the artifact the CUMULATIVE SUM?
#
# adjacent_trajectory_e returns np.cumsum(inc): the trajectory is a running
# total of adjacent-look displacement estimates. A running total of
# independent increments is a random walk, which is smooth by construction
# and strongly autocorrelated regardless of sub-aperture overlap. E7 showed
# the peak survives at ZERO overlap, which points here.
#
# The control matters: inc and cumsum(inc) have the SAME length (inc[0]=0),
# so the steering matrix is identical and the only difference is the running
# total. inc is recovered exactly as concatenate([[0], diff(traj)]).
#
#   peak vanishes on increments -> the cumulative sum generates the artifact
#   peak survives               -> the cumsum hypothesis is wrong
# ===========================================================================
def experiment_increments(slc, n_sub, patch, n_patch, overlap, window, estimator,
                          n_trials, guard_cells, velocity, f_invest, range_km,
                          aperture_km, canvas, label, seed=0):
    from micromotion import detrend as _detrend
    from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e

    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    rng = np.random.default_rng(seed)

    def trajectories(img):
        looks, _ = decompose_subapertures_w(img, n_sub=n_sub, overlap=overlap, axis=1,
                                            window=window, dtype=np.complex128)
        r0 = img.shape[0] // 2 - patch // 2
        cols = np.linspace(0, img.shape[1] - patch, n_patch).astype(int)
        walk = []
        for cc in cols:
            lp = looks[:, r0:r0 + patch, cc:cc + patch]
            t, _q = adjacent_trajectory_e(lp, estimator=estimator, dtype=np.complex128)
            walk.append(np.asarray(t, dtype=float))
        walk = np.array(walk)
        incs = np.array([np.concatenate([[0.0], np.diff(w)]) for w in walk])
        return walk, incs

    def evaluate(arr):
        obs = np.array([_detrend(t, deg=2) for t in arr], dtype=float)
        T = tomogram_from_observations(obs, z)
        return (peak_depth_m(T, z, dz_phys) / dz_phys, float(contrast(T)),
                interlook_autocorr(arr)[0])

    print(f"\n{'='*104}")
    print(f"E8 — is the peak produced by the CUMULATIVE SUM? — {label}")
    print(f"  n_sub={n_sub} overlap={overlap} patch={patch} n_patch={n_patch} "
          f"window={window} coreg={estimator}")
    print(f"  dz_phys={dz_phys:.2f} m   noise trials={n_trials}   seed={seed}")
    print(f"  cumsum(inc) and inc have identical length, so the steering matrix is")
    print(f"  the same and the ONLY difference is the running total.")
    print(f"{'='*104}")
    print(f"{'input':<26}{'series':<14}{'raw lag-1':>11}{'peak cells':>13}"
          f"{'contrast':>11}{'pinned':>9}")
    print("-" * 104)

    rows = []
    walk_r, inc_r = trajectories(slc)
    for name, arr in (("cumsum (as published)", walk_r), ("increments", inc_r)):
        pk, c, lag = evaluate(arr)
        rows.append(dict(input="real", series=name, peak_cells=float(pk),
                         contrast=c, lag1=float(lag)))
        print(f"{'REAL DATA':<26}{name:<14}{lag:>11.3f}{pk:>13.2f}{c:>11.2f}"
              f"{('PIN' if pk <= guard_cells else 'clear'):>9}")

    acc = {"cumsum (as published)": ([], [], []), "increments": ([], [], [])}
    for _ in range(n_trials):
        img = (rng.normal(0, 1, (canvas, canvas))
               + 1j * rng.normal(0, 1, (canvas, canvas))).astype(np.complex128)
        w, i_ = trajectories(img)
        for name, arr in (("cumsum (as published)", w), ("increments", i_)):
            pk, c, lag = evaluate(arr)
            acc[name][0].append(pk); acc[name][1].append(c); acc[name][2].append(lag)
    for name, (pks, cs, lags) in acc.items():
        pks, cs = np.array(pks), np.array(cs)
        rows.append(dict(input="white noise", series=name,
                         peak_median=float(np.median(pks)), peak_sd=float(pks.std()),
                         contrast_median=float(np.median(cs)),
                         lag1=float(np.mean(lags)),
                         pinned_frac=float(np.mean(pks <= guard_cells))))
        print(f"{'WHITE NOISE (median)':<26}{name:<14}{np.mean(lags):>11.3f}"
              f"{np.median(pks):>13.2f}{np.median(cs):>11.2f}"
              f"{100*np.mean(pks <= guard_cells):>8.0f}%")

    print("-" * 104)

    # CORRECTED 14 Aug 2026. The previous verdict read only the WHITE NOISE rows
    # and announced a conclusion about the run as a whole. On the Giza scene the
    # noise arm unpins while the REAL arm does not (1.75 -> 1.88 cells, still
    # pinned), so the old message printed a statement its own data contradicted.
    # Third printer in this repository found to do this; all now read the row.
    def _row(inp, ser):
        m = [r for r in rows if r["input"] == inp
             and (r["series"].startswith("cumsum") if ser == "cumsum"
                  else r["series"] == "increments")]
        return m[0] if m else None

    for inp, tag in (("real", "REAL DATA"), ("white noise", "WHITE NOISE")):
        w, i = _row(inp, "cumsum"), _row(inp, "increments")
        if w is None or i is None:
            continue
        moved = i["peak_median"] - w["peak_median"]
        unpinned = i["pinned_frac"] < 0.5
        print(f"\n  {tag}: removing the cumulative sum moves the peak "
              f"{w['peak_median']:.2f} -> {i['peak_median']:.2f} cells "
              f"({moved:+.2f}), contrast {w['contrast_median']:.2f} -> "
              f"{i['contrast_median']:.2f}, pinned {100*w['pinned_frac']:.0f}% -> "
              f"{100*i['pinned_frac']:.0f}%.")
        if moved > 0.5 and unpinned:
            print(f"     -> UNPINS. Consistent with the running total generating "
                  f"the artifact on this arm.")
        elif i["contrast_median"] < w["contrast_median"] * 0.6:
            print(f"     -> Contrast collapses but the peak STAYS PINNED. The "
                  f"running total accounts for the contrast on this arm but is "
                  f"NOT shown to be necessary for the pinning. Report as an open "
                  f"item; do not describe this run as unpinning.")
        else:
            print(f"     -> Neither the peak nor the contrast responds. The cumsum "
                  f"account is not supported on this arm.")
    print("\n  Read the two arms separately. A conclusion drawn from the noise arm "
          "alone\n  does not license a statement about the real scene.")
    return rows


# ===========================================================================
# E9 — does CONTRAST scale with random-walk LENGTH, in isolation?
#
# E8 showed contrast, autocorrelation and n_sub rise together, and that
# removing the cumsum collapses the effect at every length. External review
# accepted that as strong circumstantial evidence but noted it is one step
# short of proof: other n_sub-dependent factors (spectral weighting of the
# sub-apertures, estimator variance, look SNR) co-vary and were not excluded.
#
# E9 removes every one of them. No SAR image, no sub-apertures, no
# coregistration, no overlap, no window. Just iid Gaussian increments,
# optionally accumulated, degree-2 detrended, and inverted on the same axis
# the real pipeline would use at that n_sub.
#
#   contrast rises with L for walks but not for increments
#       -> walk LENGTH alone drives the contrast; the n_sub sensitivity is
#          the cumulative sum, and sentence 5 of the claim can be stated
#          causally rather than as "consistent with"
#   contrast flat for both
#       -> length is not the driver; the unification must be withdrawn
# ===========================================================================
def experiment_walk(lengths, n_patch, n_trials, guard_cells, velocity, f_invest,
                    range_km, aperture_km, seed=0):
    from micromotion import detrend as _detrend

    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    rng = np.random.default_rng(seed)

    print(f"\n{'='*104}")
    print("E9 — contrast vs random-walk LENGTH, with the SAR pipeline removed entirely")
    print(f"  n_patch={n_patch}  trials={n_trials}  seed={seed}  dz_phys={dz_phys:.2f} m")
    print("  iid Gaussian increments only. No image, no sub-apertures, no overlap,")
    print("  no coregistration, no window. The ONLY variable is series length.")
    print(f"{'='*104}")
    print(f"{'length':>8}{'series':>14}{'lag-1':>9}{'contrast med':>14}"
          f"{'5-95 pct':>18}{'peak cells':>12}{'pinned':>9}")
    print("-" * 104)

    rows = []
    for L in lengths:
        z = np.linspace(0, L * DZ_TARGET / 2, 300)
        for kind in ("walk (cumsum)", "increments"):
            cs, pks, lags = [], [], []
            for _ in range(n_trials):
                inc = rng.normal(0.0, 1.0, (n_patch, L))
                inc[:, 0] = 0.0
                arr = np.cumsum(inc, axis=1) if kind.startswith("walk") else inc
                lags.append(interlook_autocorr(arr)[0])
                obs = np.array([_detrend(t, deg=2) for t in arr], dtype=float)
                T = tomogram_from_observations(obs, z)
                cs.append(float(contrast(T)))
                pks.append(peak_depth_m(T, z, dz_phys) / dz_phys)
            cs, pks = np.array(cs), np.array(pks)
            rows.append(dict(length=int(L), series=kind, lag1=float(np.mean(lags)),
                             contrast_median=float(np.median(cs)),
                             p05=float(np.percentile(cs, 5)),
                             p95=float(np.percentile(cs, 95)),
                             peak_median=float(np.median(pks)),
                             pinned_frac=float(np.mean(pks <= guard_cells))))
            print(f"{L:>8}{kind:>14}{np.mean(lags):>9.3f}{np.median(cs):>14.2f}"
                  f"{f'{np.percentile(cs,5):.2f} – {np.percentile(cs,95):.2f}':>18}"
                  f"{np.median(pks):>12.2f}{100*np.mean(pks <= guard_cells):>8.0f}%")
        print("-" * 104)

    walks = [r for r in rows if r["series"].startswith("walk")]
    incs = [r for r in rows if r["series"] == "increments"]
    w_lo, w_hi = walks[0]["contrast_median"], walks[-1]["contrast_median"]
    i_lo, i_hi = incs[0]["contrast_median"], incs[-1]["contrast_median"]
    print(f"\n  walk       : length {walks[0]['length']} -> {walks[-1]['length']}   "
          f"contrast {w_lo:.2f} -> {w_hi:.2f}   ({w_hi/max(w_lo,1e-9):.1f}x)")
    print(f"  increments : length {incs[0]['length']} -> {incs[-1]['length']}   "
          f"contrast {i_lo:.2f} -> {i_hi:.2f}   ({i_hi/max(i_lo,1e-9):.1f}x)")
    if w_hi / max(w_lo, 1e-9) > 3.0 and i_hi / max(i_lo, 1e-9) < 2.0:
        print("\n  -> Contrast scales with LENGTH for accumulated series and NOT for their")
        print("     own increments. Every other n_sub-dependent factor has been removed,")
        print("     so walk length alone drives it. The unification of the n_sub")
        print("     sensitivity with the cumulative sum can be stated causally.")
    else:
        print("\n  -> Length alone does NOT reproduce the scaling. Another n_sub-dependent")
        print("     factor is involved and the unification must be withdrawn or qualified.")
    return rows


# ===========================================================================
# E10 — the PSF-MATCHED null
#
# E7 used a white complex image. Real SAR speckle is NOT white: an SLC's
# spectrum occupies a finite band (chirp bandwidth in range, Doppler
# bandwidth in azimuth) and is essentially flat inside it and zero outside.
# That band-limiting is what gives speckle its resolution-cell correlation.
#
# Here the synthetic image is built the physically correct way: complex white
# noise is placed in a CENTRED SUB-BLOCK of the spectrum and inverse
# transformed. bw_frac = 1.0 reproduces E7's white image; smaller values give
# progressively longer resolution-cell correlation.
#
# The occupied bandwidth of the REAL scene is measured and printed, so the
# synthetic can be compared at the matching fraction rather than guessed.
# ===========================================================================
def occupied_bandwidth(slc, axis=1, frac_energy=0.95):
    """Fraction of the spectrum along `axis` holding `frac_energy` of the power."""
    S = np.abs(np.fft.fftshift(np.fft.fft2(slc))) ** 2
    p = S.sum(axis=0 if axis == 1 else 1)
    p = p / p.sum()
    order = np.argsort(p)[::-1]
    csum = np.cumsum(p[order])
    n_needed = int(np.searchsorted(csum, frac_energy) + 1)
    return n_needed / len(p)


def _bandlimited_slc(canvas, bw_frac, rng):
    """Complex image whose spectrum is white inside a centred band, zero outside."""
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


def experiment_psf(slc, n_sub, patch, n_patch, overlap, window, estimator,
                   n_trials, guard_cells, velocity, f_invest, range_km,
                   aperture_km, canvas, bw_fracs, label, seed=0):
    from micromotion import detrend as _detrend
    from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e

    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    rng = np.random.default_rng(seed)

    def run(img):
        looks, _ = decompose_subapertures_w(img, n_sub=n_sub, overlap=overlap, axis=1,
                                            window=window, dtype=np.complex128)
        r0 = img.shape[0] // 2 - patch // 2
        cols = np.linspace(0, img.shape[1] - patch, n_patch).astype(int)
        raw = np.array([np.asarray(
            adjacent_trajectory_e(looks[:, r0:r0 + patch, c:c + patch],
                                  estimator=estimator, dtype=np.complex128)[0],
            dtype=float) for c in cols])
        obs = np.array([_detrend(t, deg=2) for t in raw], dtype=float)
        T = tomogram_from_observations(obs, z)
        return (peak_depth_m(T, z, dz_phys) / dz_phys, float(contrast(T)),
                interlook_autocorr(raw)[0])

    bw_real_az = occupied_bandwidth(slc, axis=1)
    bw_real_rg = occupied_bandwidth(slc, axis=0)
    pk_real, c_real, lag_real = run(slc)

    print(f"\n{'='*104}")
    print(f"E10 — PSF-matched null: band-limited synthetic speckle — {label}")
    print(f"  n_sub={n_sub} overlap={overlap} patch={patch} n_patch={n_patch} "
          f"canvas={canvas}  trials={n_trials}")
    print(f"  REAL scene occupied bandwidth (95% energy): azimuth {bw_real_az:.3f}, "
          f"range {bw_real_rg:.3f}")
    print(f"  bw_frac = 1.0 is E7's white image. Lower = longer resolution-cell")
    print(f"  correlation. Compare the row nearest the real azimuth figure.")
    print(f"{'='*104}")
    print(f"{'bw_frac':>9}{'raw lag-1':>11}{'peak median':>13}{'5-95 pct':>18}"
          f"{'contrast med':>14}{'pinned':>9}")
    print("-" * 104)

    rows = []
    for bw in bw_fracs:
        pks, cs, lags = [], [], []
        for _ in range(n_trials):
            pk, c, lag = run(_bandlimited_slc(canvas, bw, rng))
            pks.append(pk); cs.append(c); lags.append(lag)
        pks, cs = np.array(pks), np.array(cs)
        rows.append(dict(bw_frac=float(bw), lag1=float(np.mean(lags)),
                         peak_median=float(np.median(pks)),
                         p05=float(np.percentile(pks, 5)),
                         p95=float(np.percentile(pks, 95)),
                         contrast_median=float(np.median(cs)),
                         pinned_frac=float(np.mean(pks <= guard_cells))))
        print(f"{bw:>9.2f}{np.mean(lags):>11.3f}{np.median(pks):>13.2f}"
              f"{f'{np.percentile(pks,5):.2f} – {np.percentile(pks,95):.2f}':>18}"
              f"{np.median(cs):>14.2f}{100*np.mean(pks <= guard_cells):>8.0f}%")
    print("-" * 104)
    print(f"{'REAL':>9}{lag_real:>11.3f}{pk_real:>13.2f}{'—':>18}{c_real:>14.2f}"
          f"{'—':>9}")
    print("-" * 104)

    nearest = min(rows, key=lambda r: abs(r["bw_frac"] - bw_real_az))
    print(f"\n  closest synthetic band to the real azimuth bandwidth "
          f"({bw_real_az:.3f}): bw_frac={nearest['bw_frac']:.2f}")
    print(f"    synthetic peak {nearest['peak_median']:.2f} cells, "
          f"contrast {nearest['contrast_median']:.2f}")
    print(f"    real      peak {pk_real:.2f} cells, contrast {c_real:.2f}")
    if abs(nearest["peak_median"] - pk_real) < 0.4:
        print("\n  -> With correctly correlated speckle the peak position still matches.")
        print("     The white-noise objection does not change the mechanism result.")
    else:
        print("\n  -> Correlated speckle SHIFTS the peak. The white-noise null was not")
        print("     representative and the absolute comparisons must be restated.")
    return rows


# ===========================================================================
# E11 — the 1/f^2 account: does the detrend DEGREE move the peak bin?
#
# A random walk has a power spectrum falling as 1/f^2. The patent describes
# the steering matrix as a DFT. If the tomogram of an accumulated series is
# close to its power spectrum, that spectrum is monotonically decreasing and
# its maximum sits at the LOWEST SURVIVING mode -- and a degree-d polynomial
# detrend removes precisely the lowest d+1 components.
#
# Prediction: the peak BIN INDEX should advance with detrend degree, and
# should not depend much on series length. That is a sharp, cheap test of
# whether the fixed shallow peak has an analytic explanation.
# ===========================================================================
def experiment_detrend(lengths, degrees, n_patch, n_trials, velocity, f_invest,
                       range_km, aperture_km, seed=0):
    from micromotion import detrend as _detrend

    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    rng = np.random.default_rng(seed)

    print(f"\n{'='*104}")
    print("E11 — does the DETREND DEGREE move the peak bin, as a 1/f^2 spectrum predicts?")
    print(f"  n_patch={n_patch}  trials={n_trials}  300-bin depth axis")
    print("  prediction: peak bin advances with degree; weak dependence on length")
    print(f"{'='*104}")
    print(f"{'length':>8}{'deg':>6}{'peak bin':>11}{'5-95 pct':>16}"
          f"{'peak cells':>12}{'contrast med':>14}")
    print("-" * 104)

    rows = []
    for L in lengths:
        z = np.linspace(0, L * DZ_TARGET / 2, 300)
        for deg in degrees:
            bins, cs, pks = [], [], []
            for _ in range(n_trials):
                inc = rng.normal(0.0, 1.0, (n_patch, L))
                inc[:, 0] = 0.0
                walk = np.cumsum(inc, axis=1)
                obs = np.array([_detrend(t, deg=deg) for t in walk], dtype=float)
                T = tomogram_from_observations(obs, z)
                prof = T.sum(0)
                bins.append(int(np.argmax(prof)))
                pks.append(peak_depth_m(T, z, dz_phys) / dz_phys)
                cs.append(float(contrast(T)))
            bins, cs, pks = np.array(bins), np.array(cs), np.array(pks)
            rows.append(dict(length=int(L), degree=int(deg),
                             bin_median=float(np.median(bins)),
                             p05=float(np.percentile(bins, 5)),
                             p95=float(np.percentile(bins, 95)),
                             peak_cells=float(np.median(pks)),
                             contrast_median=float(np.median(cs))))
            print(f"{L:>8}{deg:>6}{np.median(bins):>11.1f}"
                  f"{f'{np.percentile(bins,5):.0f} – {np.percentile(bins,95):.0f}':>16}"
                  f"{np.median(pks):>12.2f}{np.median(cs):>14.2f}")
        print("-" * 104)

    print("\n  peak bin by degree, averaged over lengths:")
    for deg in degrees:
        sub = [r["bin_median"] for r in rows if r["degree"] == deg]
        print(f"    deg {deg}: {np.mean(sub):7.1f}   (spread across lengths "
              f"{min(sub):.0f} – {max(sub):.0f})")
    by_deg = [np.mean([r["bin_median"] for r in rows if r["degree"] == d])
              for d in degrees]
    monotone = all(b2 >= b1 - 1e-9 for b1, b2 in zip(by_deg, by_deg[1:]))
    if monotone and by_deg[-1] > by_deg[0] + 1:
        print("\n  -> The peak bin ADVANCES with detrend degree.")
        print("     CORRECTED 14 Aug 2026: an earlier version of this message said the")
        print("     peak BIN is 'largely independent of series length'. That is FALSE —")
        print("     bins span 4 to 48 at degree 0. The invariant is the peak DEPTH IN")
        print("     RESOLUTION CELLS (bin x length / 598), not the bin index.")
        print("     This is an EMPIRICAL law. The algebra from a degree-d detrend of a")
        print("     1/f^2 series to the observed 1.69 +/- 0.02 cells is NOT closed; the")
        print("     constant 0.856 is undetermined. Do not report it as derived.")
    else:
        print("\n  -> The peak bin does NOT advance cleanly with degree. The 1/f^2 account")
        print("     is not supported; treat the fixed peak as an empirical result only.")
    return rows


# ===========================================================================
# E4 — the leakage experiment
# ===========================================================================
def experiment_leakage(slc, n_sub, patch, n_patch, overlap, estimator, windows,
                       n_perm, label):
    H, W = slc.shape
    row = H // 2 - patch // 2
    cols = np.linspace(0, W - patch, n_patch).astype(int)
    zg = np.linspace(0, n_sub * DZ_TARGET / 2, 300)

    print(f"\n{'='*100}")
    print(f"E4 — does the window gradient track INTER-LOOK CORRELATION? — {label}")
    print(f"  n_sub={n_sub} coregistrator={estimator} overlap={overlap}")
    print(f"  measured on the detrended residual trajectories that enter the inverter")
    print(f"{'='*100}")
    print(f"{'window':<10}{'lag-1 corr':>12}{'lag-2 corr':>13}{'contrast':>10}"
          f"{'shufRatio':>11}{'alignRatio':>12}")
    print("-" * 100)

    rows = []
    for w in windows:
        obs, _ = patch_observations_cfg(slc, cols, row, patch, n_sub, overlap,
                                        w, np.complex128, estimator)
        rho1, rho2 = interlook_autocorr(obs)
        T = tomogram_from_observations(obs, zg)
        c = contrast(T)
        r_s = c / (np.median(shuffle_null(obs, zg, n_perm, 0)) + 1e-12)
        r_a = c / (np.median(alignment_null(obs, zg, n_perm, 0)) + 1e-12)
        rows.append(dict(window=w, lag1=rho1, lag2=rho2, contrast=float(c),
                         ratio_shuffle=float(r_s), ratio_align=float(r_a)))
        print(f"{w:<10}{rho1:>12.3f}{rho2:>13.3f}{c:>10.2f}{r_s:>11.2f}{r_a:>12.2f}")

    print("-" * 100)
    x = np.array([r["lag1"] for r in rows]); y = np.array([r["ratio_shuffle"] for r in rows])
    if len(x) > 2 and x.std() > 0 and y.std() > 0:
        r = float(np.corrcoef(x, y)[0, 1])
        print(f"correlation( inter-look lag-1 , detection statistic ) = {r:+.3f}")
        if r > 0.8:
            print("  -> statistic tracks inter-look correlation: LEAKAGE READING SUPPORTED.")
        elif r < 0.3:
            print("  -> statistic does NOT track inter-look correlation: leakage reading")
            print("     is NOT supported; the competing bandwidth/SNR explanation survives.")
        else:
            print("  -> ambiguous; neither explanation is established.")
    return rows


# ===========================================================================
# Self-test
# ===========================================================================
def selftest():
    from sensitivity_sweep import synthetic_scene
    ok = {}
    rng = np.random.default_rng(0)

    print("[A] alignment null preserves per-patch profile shape, destroys agreement:")
    zg = np.linspace(0, 9 * DZ_TARGET / 2, 300)
    _, Kz = steering(9, zg)
    obs = 0.02 * rng.standard_normal((24, 9)) + np.cos(Kz * (0.5 * zg[-1]))
    Tp = per_patch_tomograms(obs, zg)
    algn = alignment_null(obs, zg, n_perm=50, seed=1)
    # each patch's own peak height must be untouched by the null construction
    shifted = np.array([np.roll(t, 37) for t in Tp])
    same_shape = np.allclose(np.sort(shifted, axis=1), np.sort(Tp, axis=1))
    drops = contrast(Tp) > np.median(algn)
    ok["A"] = bool(same_shape and drops)
    print(f"   per-patch profiles identical up to a shift: {same_shape}")
    print(f"   aligned contrast {contrast(Tp):.1f} vs alignment-null median "
          f"{np.median(algn):.1f} -> {'PASS' if ok['A'] else 'FAIL'}")

    print("\n[B] alignment null does NOT fire on empty data (the shuffle null's failure):")
    empty = rng.standard_normal((24, 11))
    zg2 = np.linspace(0, 11 * DZ_TARGET / 2, 300)
    T = tomogram_from_observations(empty, zg2)
    r_sh = contrast(T) / np.median(shuffle_null(empty, zg2, 100, 0))
    r_al = contrast(T) / np.median(alignment_null(empty, zg2, 100, 0))
    ok["B"] = bool(r_al < r_sh)
    print(f"   empty data: shuffle ratio {r_sh:.2f}, alignment ratio {r_al:.2f} "
          f"-> {'PASS' if ok['B'] else 'FAIL'}")

    print("\n[C] absolute guard is invariant to axis length; the 5% rule is not:")
    nz = 300
    res = []
    for n_sub in (32, 128):
        z = np.linspace(0, n_sub * DZ_TARGET / 2, nz)
        T = np.zeros((4, nz))
        z_m = z * (2.11 / DZ_TARGET)
        T[:, int(np.argmin(np.abs(z_m - 3.0)))] = 1.0      # a peak at 3 m, both times
        old, _, _ = shallow_pinned(T)
        new, pk = pinned_absolute(T, z, 2.11, 2.0)
        res.append((n_sub, old, new, pk))
        print(f"   n_sub={n_sub:>4}  peak {pk:.1f} m  old-5%: {'PIN' if old else 'clear':<5} "
              f" new-absolute: {'PIN' if new else 'clear'}")
    ok["C"] = bool(res[0][1] != res[1][1] and res[0][2] == res[1][2] is True)
    print(f"   old rule changes verdict on identical physics: {res[0][1] != res[1][1]}; "
          f"new rule stable: {res[0][2] == res[1][2]} -> {'PASS' if ok['C'] else 'FAIL'}")

    print("\n[D] inter-look autocorrelation responds to smoothness:")
    smooth = np.array([np.cos(np.linspace(0, 2*np.pi, 11) + p) for p in range(24)])
    white = rng.standard_normal((24, 11))
    rs, _ = interlook_autocorr(smooth); rw, _ = interlook_autocorr(white)
    ok["D"] = bool(rs > 0.5 > rw)
    print(f"   smooth trajectories lag-1 = {rs:+.2f}; white = {rw:+.2f} "
          f"-> {'PASS' if ok['D'] else 'FAIL'}")

    print("\n[E] fixed comparison window lies inside every n_sub's unambiguous range:")
    ok["E"] = all(ZGRID_FIXED[-1] <= n * DZ_TARGET / 2 + 1e-9 for n in (11, 32, 64, 128, 256))
    print(f"   fixed zmax {ZGRID_FIXED[-1]:.1f} vs smallest unambiguous "
          f"{NSUB_REF*DZ_TARGET/2:.1f} -> {'PASS' if ok['E'] else 'FAIL'}")

    print("\n" + "=" * 60)
    print("FOLLOW-UP HARNESS SELF-TEST:", "PASS" if all(ok.values()) else "FAIL", ok)
    print("=" * 60)
    return all(ok.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicd")
    ap.add_argument("--experiment",
                    choices=["nsub", "leakage", "geometry", "noise", "synthetic",
                             "increments", "walk", "psf", "detrend"], default="nsub")
    ap.add_argument("--lengths", nargs="*", type=int,
                    default=[11, 16, 22, 32, 45, 64, 90, 128])
    ap.add_argument("--bw-fracs", nargs="*", type=float,
                    default=[1.0, 0.8, 0.6, 0.4, 0.25, 0.15])
    ap.add_argument("--degrees", nargs="*", type=int, default=[0, 1, 2, 3, 4])
    ap.add_argument("--canvas", type=int, default=512)
    ap.add_argument("--n-trials", type=int, default=300)
    ap.add_argument("--crops", nargs="*", type=int, default=[256, 512, 1024])
    ap.add_argument("--patches", nargs="*", type=int, default=[32, 48, 64, 96, 128])
    ap.add_argument("--n-patches", nargs="*", type=int, default=[12, 24, 48])
    ap.add_argument("--overlaps", nargs="*", type=float, default=[0.0, 0.4, 0.6, 0.8, 0.9])
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--n-patch", type=int, default=24)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--window", default="hann")
    ap.add_argument("--estimator", default="phasecorr")
    ap.add_argument("--counts", nargs="*", type=int, default=[11, 16, 22, 32, 45, 64, 90, 128])
    ap.add_argument("--n-sub", type=int, default=11, help="for the leakage experiment")
    ap.add_argument("--windows", nargs="*", default=["blackman", "hann", "hamming", "rect"])
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--guard-cells", type=float, default=2.0)
    ap.add_argument("--velocity", type=float, default=6000.0)
    ap.add_argument("--f-investigation", type=float, default=22000.0)
    ap.add_argument("--range-km", type=float, default=650.0)
    ap.add_argument("--aperture-km", type=float, default=42.0)
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    # E11 needs no image either.
    if args.experiment == "detrend":
        rows = experiment_detrend(args.lengths, args.degrees, args.n_patch,
                                  args.n_trials, args.velocity,
                                  args.f_investigation, args.range_km,
                                  args.aperture_km)
        out = args.out or "runs/followup_detrend.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(experiment="detrend", rows=rows), open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    # E9 needs no image at all — it removes the SAR pipeline entirely.
    if args.experiment == "walk":
        rows = experiment_walk(args.lengths, args.n_patch, args.n_trials,
                               args.guard_cells, args.velocity,
                               args.f_investigation, args.range_km,
                               args.aperture_km)
        out = args.out or "runs/followup_walk.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(experiment="walk", n_patch=args.n_patch, rows=rows),
                  open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    if not args.sicd:
        ap.error("need --sicd or --selftest")

    from sarpy.io.complex.converter import open_complex
    reader = open_complex(args.sicd)
    R, C = reader.data_size
    label = os.path.basename(args.sicd)

    def load_crop(crop):
        crop = min(crop, R, C)
        r0, c0 = R // 2 - crop // 2, C // 2 - crop // 2
        print(f"  reading {crop}x{crop} centre crop ...")
        return reader[r0:r0 + crop, c0:c0 + crop]

    if args.experiment == "geometry":
        print(f"Source {label} ({R}x{C})")
        BASE = (512, 64, 24, 0.8)
        combos = [("baseline",) + BASE]
        for p in args.patches:
            if p != BASE[1]:
                combos.append(("patch", BASE[0], p, BASE[2], BASE[3]))
        for k in args.n_patches:
            if k != BASE[2]:
                combos.append(("n_patch", BASE[0], BASE[1], k, BASE[3]))
        for o in args.overlaps:
            if abs(o - BASE[3]) > 1e-9:
                combos.append(("overlap", BASE[0], BASE[1], BASE[2], o))
        for cr in args.crops:
            if cr != BASE[0]:
                combos.append(("crop", cr, BASE[1], BASE[2], BASE[3]))
        rows = experiment_geometry(load_crop, combos, args.n_sub, args.window,
                                   args.estimator, args.n_perm, args.guard_cells,
                                   args.velocity, args.f_investigation, args.range_km,
                                   args.aperture_km, label)
        out = args.out or f"runs/followup_geometry_{label}.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(label=label, experiment="geometry", n_sub=args.n_sub,
                       rows=rows), open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    print(f"Loading {args.crop}x{args.crop} crop from {label} ({R}x{C})")
    slc = load_crop(args.crop)

    if args.experiment == "psf":
        rows = experiment_psf(slc, args.n_sub, args.patch, args.n_patch,
                              args.overlap, args.window, args.estimator,
                              args.n_trials, args.guard_cells, args.velocity,
                              args.f_investigation, args.range_km,
                              args.aperture_km, args.crop, args.bw_fracs, label)
        out = args.out or f"runs/followup_psf_{label}.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(label=label, experiment="psf", n_sub=args.n_sub, rows=rows),
                  open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    if args.experiment == "increments":
        rows = experiment_increments(slc, args.n_sub, args.patch, args.n_patch,
                                     args.overlap, args.window, args.estimator,
                                     args.n_trials, args.guard_cells, args.velocity,
                                     args.f_investigation, args.range_km,
                                     args.aperture_km, args.crop, label)
        out = args.out or f"runs/followup_increments_{label}.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(label=label, experiment="increments", n_sub=args.n_sub,
                       overlap=args.overlap, rows=rows), open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    if args.experiment == "synthetic":
        rp = rc = None
        if args.sicd:
            from micromotion import detrend as _dt
            from sensitivity_sweep import (decompose_subapertures_w as _dec,
                                           adjacent_trajectory_e as _traj)
            _, _dz = metric_depth_axis(np.array([0.0]), args.velocity,
                                       args.f_investigation, args.range_km * 1e3,
                                       args.aperture_km * 1e3)
            _z = np.linspace(0, args.n_sub * DZ_TARGET / 2, 300)
            _lk, _ = _dec(slc, n_sub=args.n_sub, overlap=args.overlap, axis=1,
                          window=args.window, dtype=np.complex128)
            _r0 = slc.shape[0] // 2 - args.patch // 2
            _cs = np.linspace(0, slc.shape[1] - args.patch, args.n_patch).astype(int)
            _raw = np.array([np.asarray(_traj(_lk[:, _r0:_r0 + args.patch,
                                                  c:c + args.patch],
                                              estimator=args.estimator,
                                              dtype=np.complex128)[0], dtype=float)
                             for c in _cs])
            _T = tomogram_from_observations(
                np.array([_dt(t, deg=2) for t in _raw], dtype=float), _z)
            rp = peak_depth_m(_T, _z, _dz) / _dz
            rc = float(contrast(_T))
        rows = experiment_synthetic(args.n_sub, args.patch, args.n_patch,
                                    args.overlaps, args.window, args.estimator,
                                    args.n_trials, args.guard_cells, args.velocity,
                                    args.f_investigation, args.range_km,
                                    args.aperture_km, args.canvas, rp, rc)
        out = args.out or f"runs/followup_synthetic_{label}.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(label=label, experiment="synthetic", n_sub=args.n_sub,
                       real_peak_cells=rp, real_contrast=rc, rows=rows),
                  open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    if args.experiment == "noise":
        res = experiment_noise(slc, args.n_sub, args.patch, args.n_patch, args.overlap,
                               args.window, args.estimator, args.n_trials,
                               args.guard_cells, args.velocity, args.f_investigation,
                               args.range_km, args.aperture_km, label)
        out = args.out or f"runs/followup_noise_{label}.json"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump(dict(label=label, experiment="noise", **res), open(out, "w"), indent=1)
        print(f"\nresults -> {out}")
        return

    if args.experiment == "nsub":
        rows = experiment_nsub(slc, args.counts, args.patch, args.n_patch, args.overlap,
                               args.window, args.estimator, args.n_perm, args.guard_cells,
                               args.velocity, args.f_investigation, args.range_km,
                               args.aperture_km, label)
        out = args.out or f"runs/followup_nsub_{label}.json"
    else:
        rows = experiment_leakage(slc, args.n_sub, args.patch, args.n_patch, args.overlap,
                                  args.estimator, args.windows, args.n_perm, label)
        out = args.out or f"runs/followup_leakage_{label}.json"

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(dict(label=label, experiment=args.experiment, rows=rows), open(out, "w"), indent=1)
    print(f"\nresults -> {out}")


if __name__ == "__main__":
    main()
