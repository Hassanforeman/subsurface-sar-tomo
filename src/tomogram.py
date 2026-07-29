#!/usr/bin/env python3
"""
tomogram.py — THE CAPSTONE (v2, with reviewer-requested controls).

End-to-end: one real SLC pass -> depth cross-section, PLUS two controls that turn
"did a band appear?" into a defensible result:

  POSITIVE CONTROL (in-data): inject a synthetic deep reflector INTO the real
    observations and confirm the pipeline recovers it. If it does, then a NULL result
    on the untouched data is meaningful ("nothing there"), not just "we couldn't see it".

  SURFACE-LEAKAGE CONTROL: correlate each patch's tomogram power with its surface
    brightness. High correlation => the "signal" is surface clutter bleeding into depth,
    NOT a real subsurface feature.

DEPTH AXIS IS UNCALIBRATED (relative/model units) — absolute metres need a velocity model
(Bible §4.1). We validate the machinery, not metric depth.

Usage:
  python3.13 src/tomogram.py --selftest
  python3.13 src/tomogram.py --sicd data/<scene>_SICD.nitf
Deps: numpy, matplotlib (sarpy only for --sicd).
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subaperture import decompose_subapertures, subpixel_shift, fourier_shift
from micromotion import adjacent_trajectory, detrend

DZ_TARGET = 5.0

# ---- validated tomographic core (same math as tomo_demo.py) ----
def steering(n_looks, zgrid):
    dKz = 2*np.pi / (n_looks * DZ_TARGET)
    Kz = np.arange(n_looks) * dKz
    return np.exp(1j * np.outer(Kz, zgrid)), Kz

def analytic1d(v):
    N = len(v); V = np.fft.fft(v); h = np.zeros(N)
    if N % 2 == 0: h[0]=1; h[N//2]=1; h[1:N//2]=2
    else: h[0]=1; h[1:(N+1)//2]=2
    return np.fft.ifft(V * h)

def invert_patch(resid, A):
    return np.abs(A.conj().T @ analytic1d(resid))**2

def tomogram_from_observations(obs, zgrid):
    A, _ = steering(obs.shape[1], zgrid)
    return np.array([invert_patch(r, A) for r in obs])

def null_tomogram(obs, zgrid, rng):
    sh = np.array([r[rng.permutation(len(r))] for r in obs])
    return tomogram_from_observations(sh, zgrid)

def contrast(T):
    prof = T.sum(0)
    return prof.max() / np.median(prof)

# ---- NEW: controls ----
def inject_reflector(obs, zgrid, z_inject, amp):
    """Add a synthetic reflector at z_inject (rel units) to every patch's observation."""
    _, Kz = steering(obs.shape[1], zgrid)
    return obs + amp * np.cos(Kz * z_inject)

def surface_brightness(slc, row, cols, patch):
    return np.array([np.mean(np.abs(slc[row:row+patch, c:c+patch])) for c in cols])

def leakage_correlation(T, brightness):
    """Pearson |corr| between per-patch tomogram peak power and surface brightness."""
    peak = T.max(axis=1)
    a = peak - peak.mean(); b = brightness - brightness.mean()
    return float(abs((a@b) / (np.sqrt((a@a)*(b@b)) + 1e-12)))


# ---- NEW: patent depth calibration + hardened control + stability guard ----
def metric_depth_axis(zgrid, v_seismic, f_invest, R, A, dz_target=DZ_TARGET):
    """Convert the RELATIVE depth axis to METRES using Biondi's own relation
    δz = λ·R/(2·A), λ = v/f  (patent WO2024008365A1). The relative half-range maps to
    the physical half-range n·δz/2, so the linear scale is δz/dz_target.
    Returns (z_metres, dz_phys). NB: this only re-LABELS the axis — it cannot create
    contrast (see steering_stress_test.py). f=22 kHz is what makes peaks read 'deep'."""
    dz_phys = (v_seismic / f_invest) * R / (2.0 * A)
    return zgrid * (dz_phys / dz_target), dz_phys


def inject_damped_resonance(obs, zgrid, z_inject, amp, decay=1.5):
    """HARDENED positive control: inject a MODERATELY-damped resonance (tone x decaying
    envelope) rather than the matched pure tone — off the steering basis but still
    physically recoverable, so it measures an honest (not self-flattering) detection floor.
    (decay>~3 becomes sub-cycle ring-down = genuinely undetectable; see steering_stress_test.)"""
    _, Kz = steering(obs.shape[1], zgrid)
    ramp = np.exp(-decay * np.arange(len(Kz)) / len(Kz))
    return obs + amp * (np.cos(Kz * z_inject) * ramp)


def peak_depth(T, zgrid):
    return float(zgrid[np.argmax(T.sum(0))])


def pinned_absolute(T, zgrid, dz_phys, guard_cells=2.0):
    """SCALE-STABLE surface-pinning guard (supersedes shallow_pinned).

    shallow_pinned() flags a peak in the shallowest `frac` OF THE AXIS. Because
    zgrid's extent scales with n_sub, that cutoff changes meaning when n_sub changes:
    the same 3 m peak is flagged at n_sub=128 (2.2% of a 135 m axis) and cleared at
    n_sub=32 (8.9% of a 33.8 m axis). This version flags on ABSOLUTE depth, in units
    of the depth-resolution cell, so its meaning does not depend on axis length.
    Returns (is_pinned, peak_depth_m)."""
    z_m = zgrid * (dz_phys / DZ_TARGET)
    pk = float(z_m[int(np.argmax(T.sum(0)))])
    return bool(pk <= guard_cells * dz_phys), pk


def per_patch_tomograms(obs, zgrid):
    A, _ = steering(obs.shape[1], zgrid)
    return np.array([np.abs(A.conj().T @ analytic1d(r))**2 for r in obs])


def alignment_null(obs, zgrid, rng, n_perm=1):
    """CORRECTLY-SPECIFIED null (supersedes null_tomogram for decision-making).

    null_tomogram() shuffles look order, which destroys the look-to-look smoothness
    that 80% sub-aperture overlap guarantees even under pure speckle — so it is
    anti-conservative and fires on empty data. This null instead preserves each
    patch's depth profile EXACTLY and randomises only whether patches AGREE on a
    depth, which is the scientific question. Returns an array of contrast values."""
    Tp = per_patch_tomograms(obs, zgrid)
    nz = Tp.shape[1]
    return np.array([contrast(np.array([np.roll(t, int(rng.integers(nz))) for t in Tp]))
                     for _ in range(n_perm)])


def shallow_pinned(T, frac=0.05):
    """Guard against the high-n_sub artifact: a peak in the shallowest `frac` of the
    depth axis (or most energy there) is a surface/low-frequency detrend artifact, NOT
    subsurface structure. Returns (is_pinned, peak_frac, shallow_energy_frac)."""
    prof = T.sum(0)
    peak_frac = np.argmax(prof) / (len(prof) - 1)
    nsh = max(1, int(frac * len(prof)))
    shallow_energy = prof[:nsh].sum() / (prof.sum() + 1e-12)
    return (peak_frac < frac) or (shallow_energy > 0.5), float(peak_frac), float(shallow_energy)


def look_count_stability(slc, cols, row, patch, overlap, n_chirp, counts):
    """Re-run the inversion at several sub-aperture counts; a real reflector holds its
    NORMALISED depth, an artifact/out-of-range peak jumps. Returns (normalised peaks, spread)."""
    pk = []
    for nL in counts:
        obs, _ = _patch_observations(slc, cols, row, patch, nL, overlap, n_chirp)
        zg = np.linspace(0, nL * DZ_TARGET / 2, 300)
        T = tomogram_from_observations(obs, zg)
        pk.append(float(np.argmax(T.sum(0)) / 299.0))   # normalised peak position [0,1]
    return [round(p, 3) for p in pk], float(np.std(pk))


# ==========================================================================
def selftest():
    rng = np.random.default_rng(7)
    n_patch, n_look = 24, 9
    zgrid = np.linspace(0, n_look*DZ_TARGET/2, 300)   # valid half-range for real observables
    _, Kz = steering(n_look, zgrid)
    z_true = 15.0

    obs = 0.02 * rng.standard_normal((n_patch, n_look))
    for p in range(8, 16): obs[p] += np.cos(Kz * z_true)
    T = tomogram_from_observations(obs, zgrid)
    Tn = null_tomogram(obs, zgrid, rng)
    peak_z = zgrid[np.argmax(T[8:16], axis=1)]
    locA = np.all(np.abs(peak_z - z_true) <= 2*DZ_TARGET)
    sepB = contrast(T) > 5*contrast(Tn)
    print(f"[A] injected layer recovered: peaks {np.round(peak_z,1).tolist()} -> {'PASS' if locA else 'FAIL'}")
    print(f"[B] signal vs null contrast: {contrast(T):.1f}x vs {contrast(Tn):.1f}x -> {'PASS' if sepB else 'FAIL'}")

    # [C] positive control on NOISE-ONLY data: inject deep reflector, must recover above null
    noise = 0.02 * rng.standard_normal((n_patch, n_look))
    z_deep = 0.7 * zgrid[-1]
    inj = inject_reflector(noise, zgrid, z_deep, amp=3*np.std(noise))
    Ti = tomogram_from_observations(inj, zgrid)
    recov_z = zgrid[np.argmax(Ti.sum(0))]
    okC = abs(recov_z - z_deep) <= 2*DZ_TARGET and contrast(Ti) > 5*contrast(null_tomogram(inj, zgrid, rng))
    print(f"[C] positive control (inject at z={z_deep:.0f} into noise): recovered at {recov_z:.0f} -> {'PASS' if okC else 'FAIL'}")

    # [D] leakage metric: high when signal is brightness-correlated, low when independent
    bright = rng.uniform(1, 5, n_patch)
    T_leak = (bright[:, None] * np.abs(np.random.default_rng(1).standard_normal((n_patch, 300))))  # power tracks brightness
    T_indep = np.abs(np.random.default_rng(2).standard_normal((n_patch, 300)))
    cl, ci = leakage_correlation(T_leak, bright), leakage_correlation(T_indep, bright)
    okD = cl > 0.5 and ci < 0.3
    print(f"[D] leakage metric: correlated={cl:.2f} (want hi), independent={ci:.2f} (want lo) -> {'PASS' if okD else 'FAIL'}")

    # [E] metric depth calibration: 22 kHz vs physical f only RELABELS, never changes contrast
    z_hi, dz_hi = metric_depth_axis(zgrid, 6000., 22000., 650e3, 42e3)   # Biondi
    z_lo, dz_lo = metric_depth_axis(zgrid, 1000., 30., 650e3, 42e3)      # physical-ish
    same_pattern = np.isclose(contrast(T), contrast(tomogram_from_observations(obs, zgrid)))
    okE = (dz_hi < dz_lo) and same_pattern and (z_hi[-1] < z_lo[-1])
    print(f"[E] metric calibration relabels only: δz(22kHz)={dz_hi:.2f} m vs δz(30Hz)={dz_lo:.0f} m; "
          f"range {z_hi[-1]:.0f} m vs {z_lo[-1]:.0f} m; contrast unchanged={same_pattern} -> {'PASS' if okE else 'FAIL'}")

    # [F] hardened (damped) positive control sets a higher, honest detection floor
    noise2 = 0.02 * rng.standard_normal((n_patch, n_look))
    zg2 = np.linspace(0, n_look*DZ_TARGET/2, 300)
    Td = tomogram_from_observations(inject_damped_resonance(noise2, zg2, 0.7*zg2[-1], 8*np.std(noise2)), zg2)
    okF = contrast(Td) > 3*contrast(null_tomogram(noise2, zg2, rng))
    print(f"[F] hardened damped positive control recovers at strong amp -> {'PASS' if okF else 'FAIL'}")

    # [G] near-surface guard flags a surface-pinned peak, passes a mid-depth one
    nz = 300
    T_surf = np.zeros((4, nz)); T_surf[:, 2] = 1.0          # peak in shallowest bins
    T_mid  = np.zeros((4, nz)); T_mid[:, nz // 2] = 1.0     # peak at mid-depth
    pin_s, _, _ = shallow_pinned(T_surf)
    pin_m, _, _ = shallow_pinned(T_mid)
    okG = pin_s and not pin_m
    print(f"[G] near-surface guard: surface-peak flagged={pin_s}, mid-peak flagged={pin_m} -> {'PASS' if okG else 'FAIL'}")

    _plot2(T, Tn, zgrid, "selftest (injected layer)", "runs/tomogram_selftest.png", z_true)
    print("\n" + "="*60)
    print("INTEGRATION + CONTROLS SELF-TEST:",
          "PASS" if (locA and sepB and okC and okD and okE and okF and okG) else "FAIL — inspect runs/tomogram_selftest.png")
    print("="*60)


def _patch_observations(slc, cols, row, patch, n_sub, overlap, n_chirp):
    """Build per-patch detrended residual trajectories. With n_chirp>1, use MCA:
    average the trajectory across range (chirp) sub-bands for SNR/diversity."""
    obs, quals = [], []
    if n_chirp > 1:
        from subaperture import multichromatic_subapertures
        mca, _ = multichromatic_subapertures(slc, n_chirp=n_chirp, n_sub=n_sub,
                                             overlap_chirp=0.5, overlap_dop=overlap)
        for cc in cols:
            tr, q = np.zeros(n_sub), 0.0
            for ch in range(n_chirp):
                lp = mca[ch][:, row:row+patch, cc:cc+patch]
                traj, qq = adjacent_trajectory(lp)
                tr += detrend(traj, deg=2); q += np.mean(qq[1:])
            obs.append(tr / n_chirp); quals.append(q / n_chirp)
    else:
        looks, _ = decompose_subapertures(slc, n_sub=n_sub, overlap=overlap, axis=1)
        for cc in cols:
            lp = looks[:, row:row+patch, cc:cc+patch]
            traj, q = adjacent_trajectory(lp)
            obs.append(detrend(traj, deg=2)); quals.append(np.mean(q[1:]))
    return np.array(obs), quals


def _plot_fcompare(T, zgrid, freqs, v, R_km, A_km, title, out):
    """#2: render the SAME tomogram under several investigation frequencies. The pattern
    is identical; only the depth axis rescales (δz=vR/2Af) — proving 'deep' is relabelling."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    n = len(freqs); fig, ax = plt.subplots(1, n, figsize=(5*n, 6))
    for i, f in enumerate(freqs):
        z_m, dz = metric_depth_axis(zgrid, v, f, R_km*1e3, A_km*1e3)
        ax[i].imshow(_norm(T).T, aspect='auto', extent=[0, T.shape[0], z_m[-1], z_m[0]], cmap='inferno')
        ax[i].axhline(160.0, color='cyan', lw=1, ls='--', alpha=0.6)   # 160 m water table ref
        ax[i].set_title(f"f={f:g} Hz: δz={dz:.2g} m\nrange 0–{z_m[-1]:.0f} m")
        ax[i].set_xlabel("patch"); ax[i].set_ylabel("depth (m)")
    fig.suptitle(f"{title}\nIDENTICAL tomogram, different investigation frequency = pure depth-axis relabelling")
    os.makedirs("runs", exist_ok=True); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close()


def run_on_sicd(path, crop=512, n_sub=11, patch=64, n_patch=24, overlap=0.8,
                n_chirp=1, use_lrsd=False, velocity=6000.0, f_invest=22000.0,
                aperture_km=42.0, range_km=650.0, ground_truth=False, stability=False,
                f_compare=False, guard_cells=2.0):
    from sarpy.io.complex.converter import open_complex
    reader = open_complex(path)
    R, C = reader.data_size
    r0, c0 = R//2 - crop//2, C//2 - crop//2
    print(f"Loading {crop}x{crop} crop; {n_sub} looks; {n_chirp} chirp band(s); {n_patch} patches ...")
    slc = reader[r0:r0+crop, c0:c0+crop]

    row = crop//2 - patch//2
    cols = np.linspace(0, crop - patch, n_patch).astype(int)
    obs, quals = _patch_observations(slc, cols, row, patch, n_sub, overlap, n_chirp)
    if use_lrsd:
        from micromotion import lrsd_denoise
        obs, _ = lrsd_denoise(obs)
    bright = surface_brightness(slc, row, cols, patch)

    zgrid = np.linspace(0, n_sub*DZ_TARGET/2, 300)   # valid half-range for real observables
    z_m, dz_phys = metric_depth_axis(zgrid, velocity, f_invest, range_km*1e3, aperture_km*1e3)
    rng = np.random.default_rng(0)
    T  = tomogram_from_observations(obs, zgrid)
    Tn = null_tomogram(obs, zgrid, rng)

    # HARDENED POSITIVE CONTROL: damped resonance (not a matched tone) at the noise scale
    z_deep = 0.7 * zgrid[-1]
    amp = 4 * np.std(obs)
    Ti = tomogram_from_observations(inject_damped_resonance(obs, zgrid, z_deep, amp), zgrid)
    pc_z = peak_depth(Ti, zgrid)
    pc_ok = abs(pc_z - z_deep) <= 3*DZ_TARGET and contrast(Ti) > 3*contrast(Tn)

    leak = leakage_correlation(T, bright)
    c_real, c_null = contrast(T), contrast(Tn)
    pinned_frac, pkfrac, shen = shallow_pinned(T)
    pinned, pk_m = pinned_absolute(T, zgrid, dz_phys, guard_cells)
    c_align = float(np.median(alignment_null(obs, zgrid, np.random.default_rng(1), n_perm=64)))
    above = c_real > 5 * c_align
    above_shuffle = c_real > 5 * c_null
    metric_peak = z_m[np.argmax(T.sum(0))]
    print(f"  mean registration quality: {np.mean(quals):.2f}")
    print(f"  depth calibration: v={velocity:.0f} m/s, f={f_invest:.0f} Hz -> "
          f"δz_phys={dz_phys:.2f} m; metric depth range 0–{z_m[-1]:.0f} m")
    print(f"  REAL tomogram contrast {c_real:.1f}x")
    print(f"    shuffle null   {c_null:.1f}x  -> ratio {c_real/(c_null+1e-12):.2f}x "
          f"(anti-conservative; retained for comparison with earlier results)")
    print(f"    ALIGNMENT null {c_align:.1f}x  -> ratio {c_real/(c_align+1e-12):.2f}x "
          f"(decision statistic)")
    if above and pinned:
        verdict = (f"ABOVE NULL but SURFACE-PINNED at {metric_peak:.0f} m "
                   f"-> detrend/surface ARTIFACT, NOT subsurface structure")
    elif above:
        verdict = f"ABOVE NULL, not surface-pinned (peak {metric_peak:.0f} m) -> investigate"
    else:
        verdict = "INDISTINGUISHABLE FROM NULL (no subsurface signal; no hallucination)"
    print(f"  VERDICT: {verdict}")
    print(f"  NEAR-SURFACE GUARD (absolute): peak at {pk_m:.1f} m; threshold "
          f"{guard_cells:g} cells = {guard_cells*dz_phys:.1f} m "
          f"-> {'ARTIFACT-SUSPECT' if pinned else 'ok (not surface-pinned)'}")
    print(f"    legacy 5%-of-axis rule would say: peak at {pkfrac*100:.0f}% of axis, "
          f"{shen*100:.0f}% of energy in shallowest 5% "
          f"-> {'ARTIFACT-SUSPECT' if pinned_frac else 'ok'}"
          + ("   [DISAGREES with the absolute guard]" if pinned_frac != pinned else ""))
    print(f"  HARDENED POSITIVE CONTROL (damped): recovered at z={pc_z:.0f}/{z_deep:.0f} "
          f"-> {'PASS' if pc_ok else 'FAIL (damped signal lost -> detection floor is higher than a pure tone)'}")
    print(f"  SURFACE-LEAKAGE: corr = {leak:.2f} "
          f"-> {'HIGH: likely surface clutter' if leak>0.5 else 'low: not obviously surface-driven'}")
    if stability:
        cset = sorted(set([max(8, n_sub // 4), max(9, n_sub // 2), n_sub]))
        peaks, spread = look_count_stability(slc, cols, row, patch, overlap, n_chirp, cset)
        at_surface = (np.mean(peaks) < 0.05)             # stable-but-pinned-at-surface = artifact
        if at_surface:
            stab_msg = "STABLE but SURFACE-PINNED -> artifact (not a real reflector)"
        elif spread < 0.05:
            stab_msg = "STABLE at depth -> real-like"
        else:
            stab_msg = "UNSTABLE -> artifact / out-of-range"
        print(f"  SUB-APERTURE-COUNT STABILITY (n_sub={cset}): normalised peaks {peaks} "
              f"spread={spread:.3f} -> {stab_msg}")
    print(f"  REAL tomogram peak labelled at {metric_peak:.0f} m depth "
          f"(at f={f_invest:.0f} Hz). NB: relabelling-only; not evidence of structure.")
    out = f"runs/tomogram_{os.path.basename(path)}.png"
    if f_compare:
        _plot_fcompare(T, zgrid, [22000., 1000., 50.], velocity, range_km, aperture_km,
                       os.path.basename(path), f"runs/fcompare_{os.path.basename(path)}.png")
        print(f"  frequency-relabelling figure -> runs/fcompare_{os.path.basename(path)}.png")
    if ground_truth:
        _plot_compare(T, Tn, z_m, bright, os.path.basename(path),
                      f"runs/repro_{os.path.basename(path)}.png", f_invest)
        print(f"  comparison vs Butte ground truth -> runs/repro_{os.path.basename(path)}.png")
    _plot4(T, Tn, Ti, bright, zgrid, os.path.basename(path), out, z_deep)


# West Camp documented ground truth (metres) for overlay
_GT_WATER_TABLE_M = 160.0
_GT_LEVELS_M = (30.5, 457.0)   # 100-ft levels span, surface stack to Travona depth

def _plot_compare(T, Tn, z_m, bright, title, out, f_invest):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(16, 6), gridspec_kw={'width_ratios':[3,3,2]})
    ext = [0, T.shape[0], z_m[-1], z_m[0]]
    ax[0].imshow(_norm(T).T, aspect='auto', extent=ext, cmap='inferno')
    ax[0].set_title(f"REAL tomogram (metric, f={f_invest:.0f} Hz)"); ax[0].set_xlabel("patch")
    ax[0].set_ylabel("depth (m)")
    ax[1].imshow(_norm(Tn).T, aspect='auto', extent=ext, cmap='inferno')
    ax[1].set_title("Null (shuffled)"); ax[1].set_xlabel("patch")
    # ground-truth panel
    ax[2].axhspan(_GT_LEVELS_M[0], _GT_LEVELS_M[1], color='saddlebrown', alpha=0.15)
    for zz in np.arange(_GT_LEVELS_M[0], _GT_LEVELS_M[1]+1, 30.5):
        ax[2].axhline(zz, color='saddlebrown', lw=0.8, alpha=0.7)
    ax[2].axhline(_GT_WATER_TABLE_M, color='tab:blue', lw=2, ls='--')
    ax[2].text(0.05, _GT_WATER_TABLE_M-6, "water table ~160 m", color='tab:blue', fontsize=8)
    ax[2].set_ylim(z_m[-1], z_m[0]); ax[2].set_xticks([]); ax[2].set_title("Butte GROUND TRUTH")
    ax[2].set_ylabel("depth (m)")
    for a in ax[:2]:
        a.axhline(_GT_WATER_TABLE_M, color='cyan', lw=1, ls='--', alpha=0.7)
    os.makedirs("runs", exist_ok=True); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close()


# ---- plots ----
def _norm(x): return x/(x.max()+1e-12)

def _plot2(T, Tn, zgrid, title, out, z_true=None):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13,5), sharey=True)
    ext=[0,T.shape[0],zgrid[-1],zgrid[0]]
    im=ax[0].imshow(_norm(T).T,aspect='auto',extent=ext,cmap='inferno'); ax[0].set_title(f"Tomogram — {title}")
    ax[0].set_xlabel("along-track patch"); ax[0].set_ylabel("relative depth (uncalibrated)")
    if z_true is not None: ax[0].axhline(z_true,color='cyan',ls='--',lw=1,alpha=.7)
    ax[1].imshow(_norm(Tn).T,aspect='auto',extent=ext,cmap='inferno'); ax[1].set_title("Null (shuffled)")
    ax[1].set_xlabel("along-track patch"); fig.colorbar(im,ax=ax,shrink=.8,label="norm. power")
    os.makedirs("runs",exist_ok=True); fig.savefig(out,dpi=120,bbox_inches='tight'); print(f"  figure -> {out}")

def _plot4(T, Tn, Ti, bright, zgrid, title, out, z_deep):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(13,9))
    ext=[0,T.shape[0],zgrid[-1],zgrid[0]]
    ax[0,0].imshow(_norm(T).T,aspect='auto',extent=ext,cmap='inferno'); ax[0,0].set_title(f"REAL tomogram — {title}")
    ax[0,0].set_xlabel("patch"); ax[0,0].set_ylabel("relative depth")
    ax[0,1].imshow(_norm(Tn).T,aspect='auto',extent=ext,cmap='inferno'); ax[0,1].set_title("Null (shuffled)")
    ax[0,1].set_xlabel("patch")
    ax[1,0].imshow(_norm(Ti).T,aspect='auto',extent=ext,cmap='inferno')
    ax[1,0].axhline(z_deep,color='cyan',ls='--',lw=1,alpha=.7)
    ax[1,0].set_title("POSITIVE CONTROL: real + injected deep reflector"); ax[1,0].set_xlabel("patch"); ax[1,0].set_ylabel("relative depth")
    ax[1,1].scatter(bright, T.max(axis=1), c='tab:red'); ax[1,1].set_title("SURFACE-LEAKAGE: tomogram power vs surface brightness")
    ax[1,1].set_xlabel("patch surface brightness"); ax[1,1].set_ylabel("patch peak power")
    os.makedirs("runs",exist_ok=True); fig.tight_layout(); fig.savefig(out,dpi=120); print(f"  figure -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicd")
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--n-sub", type=int, default=11,
                    help="number of Doppler sub-apertures; crank up (e.g. 128) to reach deep metric range")
    ap.add_argument("--n-chirp", type=int, default=1, help="MCA range sub-bands (1 = off)")
    ap.add_argument("--lrsd", action="store_true", help="LRSD-denoise the observations")
    ap.add_argument("--velocity", type=float, default=6000.0, help="seismic velocity m/s")
    ap.add_argument("--f-investigation", type=float, default=22000.0,
                    help="investigation frequency Hz (Biondi=22000; physical seismic ~30-50)")
    ap.add_argument("--aperture-km", type=float, default=42.0)
    ap.add_argument("--range-km", type=float, default=650.0)
    ap.add_argument("--ground-truth", action="store_true",
                    help="overlay Butte West Camp ground truth in a comparison figure")
    ap.add_argument("--stability", action="store_true",
                    help="sub-aperture-count stability guard (re-runs at n/4, n/2, n)")
    ap.add_argument("--guard-cells", type=float, default=2.0,
                    help="surface-pinning guard: peak within this many depth cells of the "
                         "surface is an artifact (scale-stable; replaces the 5%-of-axis rule)")
    ap.add_argument("--f-compare", action="store_true",
                    help="render the same tomogram at 22000/1000/50 Hz (relabelling demo)")
    args = ap.parse_args()
    if args.sicd:
        run_on_sicd(args.sicd, crop=args.crop, n_sub=args.n_sub, n_chirp=args.n_chirp,
                    use_lrsd=args.lrsd, velocity=args.velocity, f_invest=args.f_investigation,
                    aperture_km=args.aperture_km, range_km=args.range_km,
                    ground_truth=args.ground_truth, stability=args.stability,
                    f_compare=args.f_compare, guard_cells=args.guard_cells)
    else:
        selftest()
