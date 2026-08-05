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
                    choices=["nsub", "leakage", "geometry", "noise"], default="nsub")
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
