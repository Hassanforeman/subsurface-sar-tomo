#!/usr/bin/env python3
"""
E12 — the planted-SLC positive control.

WHY THIS EXISTS
---------------
The manuscript's "in-data positive control" injects a tone into `obs` — the
per-patch trajectory vector — AFTER the cumulative sum and AFTER the degree-2
detrend, using `inject_reflector()`:

    return obs + amp * np.cos(Kz * z_inject)

That demonstrates the inverter recovers a tone written in its own coordinates.
It does not demonstrate that a PHYSICAL displacement signature survives the SAR
front-end, and E9 has since shown the front-end is not even necessary to produce
the artifact. Adversarial review (13 Aug 2026) called this self-flattering. It is.

E12 plants the signature UPSTREAM of everything the artifact depends on: each
sub-aperture look is physically shifted in the image domain by a sub-pixel
amount, so the displacement must be RECOVERED by the pipeline's own magnitude
cross-correlation estimator, from speckle, through the window taper, before it
is accumulated, detrended and inverted. Nothing downstream is touched.

A reflector at relative depth z produces, under the method's own model, a
per-look displacement trajectory D_k = A * cos(Kz[k] * z). We impose exactly
that, coherently across every patch, and ask two questions:

  1. At what amplitude does the planted depth beat the 1.71-cell artifact?
  2. Is that amplitude physically plausible?

The experiment is designed to be publishable whichever way it falls:
  * signal wins at small amplitude -> the method has a real detection channel
    and the manuscript's language must soften.
  * signal never wins, or needs an absurd amplitude -> the pipeline cannot see
    a real signal but reliably reports a fake one, which is a stronger result
    than anything currently in the paper.

Usage
-----
  python3 src/experiment_e12_planted.py --selftest
  python3 src/experiment_e12_planted.py                       # synthetic speckle
  python3 src/experiment_e12_planted.py --sicd data/<giza>_SICD.nitf
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from micromotion import detrend
from tomogram import (DZ_TARGET, steering, contrast, tomogram_from_observations,
                      metric_depth_axis)
from sensitivity_sweep import (decompose_subapertures_w, adjacent_trajectory_e,
                               fourier_shift_p)


# ---------------------------------------------------------------------------
# synthetic scene, band-limited to a realistic occupied bandwidth
# ---------------------------------------------------------------------------
def bandlimited_slc(canvas, bw_frac, rng):
    """Complex image whose spectrum is white inside a centred band, zero outside.
    Identical construction to E10's null (bw_frac=0.80 matches the measured
    occupied bandwidth of the real Bingham scene, azimuth 0.750)."""
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


# ---------------------------------------------------------------------------
# the planted displacement trajectory
# ---------------------------------------------------------------------------
def planted_trajectory(Kz, z_target, amp, waveform="tone", decay=1.5):
    """Per-look displacement, in PIXELS, that a reflector at z_target produces
    under the method's own forward model.

    waveform='tone'   : A*cos(Kz*z)  — the model's matched signature.
    waveform='damped' : the same tone times a decaying envelope, deliberately
                        OFF the steering basis, so the test cannot be accused of
                        handing the inverter its own eigenvector.
    """
    d = amp * np.cos(Kz * z_target)
    if waveform == "damped":
        d = d * np.exp(-decay * np.arange(len(Kz)) / len(Kz))
    return d.astype(float)


def plant_into_looks(looks, disp):
    """Physically shift look k of the SLC by disp[k] pixels along the azimuth
    (column) axis — the same axis the trajectory estimator measures. This is
    upstream of trajectory estimation, coregistration, the cumulative sum and
    the detrend. The estimator must recover the motion from image data."""
    out = np.empty_like(looks)
    for k in range(looks.shape[0]):
        out[k] = fourier_shift_p(looks[k], 0.0, float(disp[k]),
                                 dtype=np.complex128)
    return out


# ---------------------------------------------------------------------------
# the pipeline, unmodified downstream of the plant
# ---------------------------------------------------------------------------
def run_pipeline(looks, patch, n_patch, estimator, zgrid):
    r0 = looks.shape[1] // 2 - patch // 2
    cols = np.linspace(0, looks.shape[2] - patch, n_patch).astype(int)
    raw = np.array([np.asarray(
        adjacent_trajectory_e(looks[:, r0:r0 + patch, c:c + patch],
                              estimator=estimator, dtype=np.complex128)[0],
        dtype=float) for c in cols])
    obs = np.array([detrend(t, deg=2) for t in raw], dtype=float)
    T = tomogram_from_observations(obs, zgrid)
    prof = T.sum(0)
    return T, prof, raw


def summarise(prof, zgrid, z_target, dz_phys):
    """peak position in resolution cells, contrast, and the profile power at the
    planted depth relative to the profile's own peak."""
    cells = zgrid / DZ_TARGET
    i_pk = int(np.argmax(prof))
    peak_cells = float(cells[i_pk])
    i_tgt = int(np.argmin(np.abs(cells - z_target / DZ_TARGET)))
    return dict(peak_cells=peak_cells,
                contrast=float(prof.max() / np.median(prof)),
                target_cells=float(cells[i_tgt]),
                power_at_target_over_peak=float(prof[i_tgt] / (prof.max() + 1e-30)),
                found_target=bool(abs(peak_cells - cells[i_tgt]) <= 1.0),
                pinned=bool(peak_cells <= 2.0))


# ---------------------------------------------------------------------------
def experiment(slc_source, amps, n_sub, patch, n_patch, overlap, window,
               estimator, n_trials, canvas, bw_frac, z_frac, waveform,
               velocity, f_invest, range_km, aperture_km, seed=0):
    rng = np.random.default_rng(seed)
    zgrid = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    _, Kz = steering(n_sub, zgrid)
    _, dz_phys = metric_depth_axis(np.array([0.0]), velocity, f_invest,
                                   range_km * 1e3, aperture_km * 1e3)
    z_target = z_frac * zgrid[-1]

    real = slc_source is not None

    # ---- calibrate against the pipeline's own noise floor -------------------
    # Adversarial review, 13 Aug: "design the amplitude against the pipeline's own
    # residual RMS, not against a displacement that would light up any tracker."
    # A large plant always survives; the question is whether a seismic-scale one does.
    cal_img = slc_source if real else bandlimited_slc(canvas, bw_frac,
                                                      np.random.default_rng(seed + 9999))
    cal_looks, _ = decompose_subapertures_w(cal_img, n_sub=n_sub, overlap=overlap,
                                            axis=1, window=window,
                                            dtype=np.complex128)
    _, _, cal_raw = run_pipeline(cal_looks, patch, n_patch, estimator, zgrid)
    walk_rms = float(np.mean(np.std(cal_raw, axis=1)))

    print(f"\n{'='*100}")
    print("E12 — planted-SLC positive control (signature injected UPSTREAM of the front-end)")
    print(f"  scene       : {'REAL SICD' if real else f'synthetic speckle, bw_frac={bw_frac}'}")
    print(f"  n_sub={n_sub}  patch={patch}  n_patch={n_patch}  overlap={overlap}  window={window}")
    print(f"  waveform    : {waveform}{'  (matched to steering basis)' if waveform=='tone' else '  (OFF basis)'}")
    print(f"  planted at  : z={z_target:.2f} rel  =  {z_target/DZ_TARGET:.2f} cells  "
          f"=  {z_target*(dz_phys/DZ_TARGET):.2f} m")
    print(f"  dz_phys     : {dz_phys:.2f} m     trials per amplitude: {n_trials}")
    print(f"  BASELINE trajectory RMS from the unplanted scene: {walk_rms:.5f} px")
    print(f"  amplitudes are reported both in pixels and as multiples of that RMS")
    print(f"{'='*100}")
    print(f"{'amp (px)':>10s} {'x walk RMS':>11s} {'peak cells':>11s} {'5-95 pct':>15s} "
          f"{'contrast':>9s} {'found tgt':>10s} {'pinned':>8s} {'P(tgt)/P(pk)':>13s}")
    print("-" * 108)

    rows = []
    for amp in amps:
        pks, cs, found, pinned, ratio = [], [], [], [], []
        for t in range(n_trials):
            if real:
                img = slc_source
                trial_rng = np.random.default_rng(seed + t)
            else:
                img = bandlimited_slc(canvas, bw_frac, rng)
            looks, _ = decompose_subapertures_w(img, n_sub=n_sub, overlap=overlap,
                                                axis=1, window=window,
                                                dtype=np.complex128)
            disp = planted_trajectory(Kz, z_target, amp, waveform)
            if amp > 0:
                looks = plant_into_looks(looks, disp)
            _, prof, _ = run_pipeline(looks, patch, n_patch, estimator, zgrid)
            s = summarise(prof, zgrid, z_target, dz_phys)
            pks.append(s["peak_cells"]); cs.append(s["contrast"])
            found.append(s["found_target"]); pinned.append(s["pinned"])
            ratio.append(s["power_at_target_over_peak"])
            if real and amp == amps[0] and t == 0:
                pass  # real scene is deterministic; one trial suffices at amp 0
        row = dict(amp_px=float(amp),
                   amp_x_walk_rms=float(amp / (walk_rms + 1e-30)),
                   peak_cells=float(np.median(pks)),
                   p05=float(np.percentile(pks, 5)),
                   p95=float(np.percentile(pks, 95)),
                   contrast=float(np.median(cs)),
                   found_target_frac=float(np.mean(found)),
                   pinned_frac=float(np.mean(pinned)),
                   power_ratio=float(np.median(ratio)))
        rows.append(row)
        print(f"{amp:10.4f} {row['amp_x_walk_rms']:11.1f} {row['peak_cells']:11.2f} "
              f"{row['p05']:6.2f} - {row['p95']:<6.2f} "
              f"{row['contrast']:9.2f} {row['found_target_frac']*100:9.0f}% "
              f"{row['pinned_frac']*100:7.0f}% {row['power_ratio']:13.3f}")

    # --- detection floor -----------------------------------------------------
    floor = None
    for r in rows:
        if r["found_target_frac"] >= 0.5:
            floor = r["amp_px"]; break
    print("-" * 108)
    if floor is None:
        print("VERDICT: no tested amplitude lets the planted reflector beat the artifact.")
        print("         The pipeline reports a peak it was not given and misses one it was.")
    else:
        print(f"VERDICT: detection floor at {floor:g} px of per-look displacement.")
        print(f"         Below this the artifact wins; above it the planted depth is recovered.")
    print("         Read this against the artifact baseline in the amp=0 row.")
    return rows, dict(walk_rms_px=walk_rms,
                      detection_floor_x_walk_rms=(None if floor is None
                                                  else float(floor / (walk_rms + 1e-30))),
                      z_target=float(z_target),
                      z_target_cells=float(z_target / DZ_TARGET),
                      z_target_m=float(z_target * (dz_phys / DZ_TARGET)),
                      dz_phys=float(dz_phys), detection_floor_px=floor)


# ---------------------------------------------------------------------------
def selftest():
    """Verify the plant does what it claims before any conclusion rests on it."""
    rng = np.random.default_rng(0)
    n_sub, patch, n_patch = 11, 64, 24
    zgrid = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    _, Kz = steering(n_sub, zgrid)
    img = bandlimited_slc(512, 0.8, rng)
    looks, _ = decompose_subapertures_w(img, n_sub=n_sub, overlap=0.8, axis=1,
                                        window="hann", dtype=np.complex128)

    # [A] a large plant must be recovered by the estimator to within a fraction
    #     of a pixel — this is the only thing that makes the experiment meaningful
    z_t = 0.6 * zgrid[-1]
    amp = 0.5
    disp = planted_trajectory(Kz, z_t, amp)
    shifted = plant_into_looks(looks, disp)
    _, _, raw = run_pipeline(shifted, patch, n_patch, "phasecorr", zgrid)
    _, _, raw0 = run_pipeline(looks, patch, n_patch, "phasecorr", zgrid)
    rec = raw.mean(0) - raw0.mean(0)          # recovered minus baseline walk
    tgt = disp - disp[0]                       # cumsum of increments loses D[0]
    r = float(np.corrcoef(rec, tgt)[0, 1])
    scale = float(np.polyfit(tgt, rec, 1)[0])
    okA = r > 0.9
    print(f"[A] planted displacement recovered by the front-end: corr={r:.3f} -> "
          f"{'PASS' if okA else 'FAIL'}")

    # [E] the front-end ATTENUATES sub-pixel displacement. This is a finding, not
    #     a bug: it is reported, not asserted away. amp is in pixels; `scale` is
    #     the fraction of the planted amplitude that survives to the trajectory.
    print(f"[E] front-end recovery scale at {amp} px: {scale:.3f} "
          f"({100*scale:.0f}% of the planted amplitude survives)")

    # [B] zero amplitude must leave the pipeline bit-identical
    same = np.allclose(plant_into_looks(looks, np.zeros(n_sub)), looks, atol=1e-9)
    print(f"[B] amp=0 plant is a no-op -> {'PASS' if same else 'FAIL'}")

    # [C] the unplanted synthetic scene must still show the artifact at ~1.7 cells
    _, prof0, _ = run_pipeline(looks, patch, n_patch, "phasecorr", zgrid)
    pk0 = float((zgrid / DZ_TARGET)[int(np.argmax(prof0))])
    okC = 1.2 <= pk0 <= 2.2
    print(f"[C] artifact present in the unplanted control: peak={pk0:.2f} cells -> "
          f"{'PASS' if okC else 'FAIL'}")

    # [D] the shift is along the axis the estimator measures
    one = np.zeros(n_sub); one[5] = 1.0
    s = plant_into_looks(looks, one)
    moved = float(np.abs(np.abs(s[5]) - np.abs(looks[5])).mean())
    still = float(np.abs(np.abs(s[4]) - np.abs(looks[4])).mean())
    okD = moved > 10 * still + 1e-12
    print(f"[D] plant is per-look and localised: moved={moved:.4f} untouched={still:.2e} -> "
          f"{'PASS' if okD else 'FAIL'}")

    ok = okA and same and okC and okD
    print(f"\nSELFTEST {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicd")
    ap.add_argument("--amps", nargs="*", type=float,
                    default=[0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0])
    ap.add_argument("--n-sub", type=int, default=11)
    ap.add_argument("--patch", type=int, default=64)
    ap.add_argument("--n-patch", type=int, default=24)
    ap.add_argument("--overlap", type=float, default=0.8)
    ap.add_argument("--window", default="hann")
    ap.add_argument("--estimator", default="phasecorr")
    ap.add_argument("--n-trials", type=int, default=12)
    ap.add_argument("--canvas", type=int, default=512)
    ap.add_argument("--bw-frac", type=float, default=0.80)
    ap.add_argument("--z-frac", type=float, default=0.60,
                    help="planted depth as a fraction of the depth axis")
    ap.add_argument("--waveform", default="tone", choices=["tone", "damped"])
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--velocity", type=float, default=6000.0)
    ap.add_argument("--f-investigation", type=float, default=22000.0)
    ap.add_argument("--range-km", type=float, default=650.0)
    ap.add_argument("--aperture-km", type=float, default=42.0)
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    slc = None
    label = "synthetic"
    if args.sicd:
        import sarpy.io.complex as sicd_io
        rdr = sicd_io.open(args.sicd)
        full = rdr[:, :]
        r0 = full.shape[0] // 2 - args.crop // 2
        c0 = full.shape[1] // 2 - args.crop // 2
        slc = np.asarray(full[r0:r0 + args.crop, c0:c0 + args.crop],
                         dtype=np.complex128)
        label = os.path.basename(args.sicd).split("_SICD")[0]
        print(f"loaded {args.sicd}  crop={slc.shape}")

    rows, meta = experiment(slc, args.amps, args.n_sub, args.patch, args.n_patch,
                            args.overlap, args.window, args.estimator,
                            args.n_trials, args.canvas, args.bw_frac, args.z_frac,
                            args.waveform, args.velocity, args.f_investigation,
                            args.range_km, args.aperture_km)

    out = args.out or f"runs/e12_planted_{label}_{args.waveform}.json"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(dict(label=label, experiment="e12_planted", waveform=args.waveform,
                   n_sub=args.n_sub, overlap=args.overlap, patch=args.patch,
                   n_patch=args.n_patch, **meta, rows=rows),
              open(out, "w"), indent=1)
    print(f"\nresults -> {out}")


if __name__ == "__main__":
    main()
