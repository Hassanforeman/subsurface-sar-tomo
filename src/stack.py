#!/usr/bin/env python3
"""
stack.py — multi-acquisition stacking (Validation Plan Lever 0).

Biondi uses 200+ scenes, not one pass (his 2022 abstract says "series of SAR images";
on Joe Rogan he says "more than 200"). A stack buys temporal aperture (many dates of the
surface-vibration field) and, if co-registered, multi-baseline angular aperture. This
module stacks per-scene depth tomograms and re-applies the controls, to test the decisive
question: does a known reflector (e.g. the ~160 m Butte water table) emerge from a stack
that single-pass missed — AND does a consistent processing ARTIFACT reinforce just the same?

Modes:
  python3.13 src/stack.py --selftest                       # synthetic N-scene demo (no data)
  python3.13 src/stack.py --sicds data/A.nitf data/B.nitf ...   # stack real co-located scenes
      (optional: --n-sub 128 --lrsd --f-investigation 22000 --ground-truth)

Caveat: scenes must image roughly the same footprint; cross-pass coregistration of the
patch axis is a refinement (the depth/frequency axis is what we stack here).

Deps: numpy (+ sarpy for --sicds).
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import (DZ_TARGET, steering, tomogram_from_observations, null_tomogram,
                      shallow_pinned, _patch_observations, metric_depth_axis)


def _norm_profile(T):
    p = T.sum(0)
    return p / (p.max() + 1e-12)


def stack_profiles(obs_list, zgrid, rng):
    """Mean of per-scene NORMALISED depth profiles for real and shuffled-null."""
    realP, nullP = [], []
    for o in obs_list:
        realP.append(_norm_profile(tomogram_from_observations(o, zgrid)))
        nullP.append(_norm_profile(null_tomogram(o, zgrid, rng)))
    return np.mean(realP, 0), np.mean(nullP, 0), np.array(realP)


def profile_contrast(p):
    return float(p.max() / (np.median(p) + 1e-12))


# ---------------------------------------------------------------------------
def run_on_sicds(paths, crop=512, n_sub=128, patch=64, n_patch=24, overlap=0.8,
                 n_chirp=1, use_lrsd=False, velocity=6000.0, f_invest=22000.0,
                 aperture_km=42.0, range_km=650.0, ground_truth=False):
    from sarpy.io.complex.converter import open_complex
    obs_list = []
    for p in paths:
        reader = open_complex(p)
        R, C = reader.data_size
        r0, c0 = R//2 - crop//2, C//2 - crop//2
        slc = reader[r0:r0+crop, c0:c0+crop]
        row = crop//2 - patch//2
        cols = np.linspace(0, crop - patch, n_patch).astype(int)
        obs, _ = _patch_observations(slc, cols, row, patch, n_sub, overlap, n_chirp)
        if use_lrsd:
            from micromotion import lrsd_denoise
            obs, _ = lrsd_denoise(obs)
        obs_list.append(obs)
        print(f"  + {os.path.basename(p)}")

    zgrid = np.linspace(0, n_sub*DZ_TARGET/2, 300)
    z_m, dz = metric_depth_axis(zgrid, velocity, f_invest, range_km*1e3, aperture_km*1e3)
    rng = np.random.default_rng(0)
    Rs, Ns, perscene = stack_profiles(obs_list, zgrid, rng)
    c_single = float(np.mean([profile_contrast(pp) for pp in perscene]))
    c_stack, c_null = profile_contrast(Rs), profile_contrast(Ns)
    pinned, pf, sh = shallow_pinned(np.tile(Rs, (n_patch, 1)))
    peak_m = z_m[int(np.argmax(Rs))]

    print(f"  scenes stacked: {len(obs_list)}; depth calibration δz={dz:.2f} m, range 0–{z_m[-1]:.0f} m")
    print(f"  per-scene mean contrast {c_single:.1f}x -> STACKED {c_stack:.1f}x (stacked null {c_null:.1f}x)")
    print(f"  stacked peak at {peak_m:.0f} m ({pf*100:.0f}% of axis; {sh*100:.0f}% energy in top 5%)")
    if c_stack > 5*c_null and not pinned:
        print(f"  VERDICT: STACKED SIGNAL at {peak_m:.0f} m, not surface-pinned -> INVESTIGATE vs ground truth")
    elif c_stack > 5*c_null and pinned:
        print(f"  VERDICT: stacked peak is SURFACE-PINNED -> artifact reinforced by the stack, NOT real")
    else:
        print(f"  VERDICT: stack INDISTINGUISHABLE FROM NULL (single-pass null persists under stacking)")
    _plot_stack(Rs, Ns, z_m, perscene, "runs/stack.png", ground_truth)
    print("  figure -> runs/stack.png")


def _plot_stack(Rs, Ns, z_m, perscene, out, ground_truth):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    for pp in perscene:
        ax[0].plot(pp, z_m, color='gray', lw=0.6, alpha=0.5)
    ax[0].plot(Rs, z_m, color='crimson', lw=2.2, label='stacked real')
    ax[0].plot(Ns, z_m, color='tab:blue', lw=1.4, ls='--', label='stacked null')
    if ground_truth:
        ax[0].axhline(160.0, color='tab:cyan', lw=1.5, ls=':', label='water table ~160 m')
    ax[0].invert_yaxis(); ax[0].set_xlabel("normalised power"); ax[0].set_ylabel("depth (m)")
    ax[0].set_title("Stacked depth profile (grey = per scene)"); ax[0].legend(fontsize=8)
    ax[1].imshow(perscene, aspect='auto', cmap='inferno',
                 extent=[z_m[0], z_m[-1], len(perscene), 0])
    ax[1].set_xlabel("depth (m)"); ax[1].set_ylabel("scene #")
    ax[1].set_title("Per-scene depth profiles (consistency check)")
    os.makedirs("runs", exist_ok=True); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close()


# ---------------------------------------------------------------------------
def selftest():
    rng = np.random.default_rng(3)
    nP, nL, N = 24, 11, 8
    zgrid = np.linspace(0, nL*DZ_TARGET/2, 300)
    _, Kz = steering(nL, zgrid)
    z0 = 0.45 * zgrid[-1]

    # [A] a CONSISTENT real reflector + independent noise -> stack lifts it
    obs_list = []
    for _ in range(N):
        o = 0.8 * rng.standard_normal((nP, nL))
        o += 0.6 * np.cos(Kz * z0)
        obs_list.append(o)
    Rs, Ns, perscene = stack_profiles(obs_list, zgrid, rng)
    c_single = float(np.mean([profile_contrast(p) for p in perscene]))
    c_stack = profile_contrast(Rs)
    peak_z = zgrid[int(np.argmax(Rs))]
    okA = c_stack > c_single and abs(peak_z - z0) <= 2*DZ_TARGET
    print(f"[A] consistent reflector: per-scene contrast {c_single:.1f} -> stacked {c_stack:.1f}; "
          f"peak z={peak_z:.0f}/{z0:.0f} -> {'PASS (stack lifts a real reflector)' if okA else 'FAIL'}")

    # [B] a CONSISTENT artifact (residual low-freq trend) ALSO reinforces -> honesty caveat
    obs_art = []
    for _ in range(N):
        o = 0.8 * rng.standard_normal((nP, nL))
        o += np.linspace(0, 2.0, nL)[None, :]      # same un-detrended trend every scene
        obs_art.append(o)
    Ra, _, _ = stack_profiles(obs_art, zgrid, rng)
    pinned, pf, _ = shallow_pinned(np.tile(Ra, (nP, 1)))
    okB = pinned
    print(f"[B] consistent artifact reinforces too (peak {pf*100:.0f}% of axis) "
          f"-> {'PASS (consistency != reality; guards still required)' if okB else 'FAIL'}")

    print("\n" + "="*60)
    print("STACK SELF-TEST:", "PASS" if (okA and okB) else "FAIL")
    print("="*60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicds", nargs="*", help="paths to co-located SICD .nitf scenes to stack")
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--n-sub", type=int, default=128)
    ap.add_argument("--n-chirp", type=int, default=1)
    ap.add_argument("--lrsd", action="store_true")
    ap.add_argument("--velocity", type=float, default=6000.0)
    ap.add_argument("--f-investigation", type=float, default=22000.0)
    ap.add_argument("--aperture-km", type=float, default=42.0)
    ap.add_argument("--range-km", type=float, default=650.0)
    ap.add_argument("--ground-truth", action="store_true")
    args = ap.parse_args()
    if args.sicds:
        run_on_sicds(args.sicds, crop=args.crop, n_sub=args.n_sub, n_chirp=args.n_chirp,
                     use_lrsd=args.lrsd, velocity=args.velocity, f_invest=args.f_investigation,
                     aperture_km=args.aperture_km, range_km=args.range_km,
                     ground_truth=args.ground_truth)
    else:
        selftest()
