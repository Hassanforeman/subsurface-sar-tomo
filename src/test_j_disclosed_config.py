#!/usr/bin/env python3
"""
Test J — the authors' newly disclosed configuration (pre-registration:
docs/PREREGISTRATION_DISCLOSED_CONFIG_2026-11-09.md).

Each look uses a fraction `f` of the azimuth (Doppler) spectrum, slid across the full
spectrum. With n_sub looks the band is N*f, which needs overlap = (n_sub - 1/f)/(n_sub - 1).
  Arm A: f = 1/2 ("we are using half bandwidth")
  Arm B: f = 6 s / T_collect ("five, six, seven seconds to listen")
Everything else is the v6.3 Table 3 pipeline. Depth labels at 10 kHz and 22 kHz are labels only.

Usage:
  python3 src/test_j_disclosed_config.py --sicd data/X.nitf --arm A --counts 11 21
  python3 src/test_j_disclosed_config.py --sicd data/X.nitf --arm B --counts 11
  python3 src/test_j_disclosed_config.py --sicd data/X.nitf --arm A --counts 11 --noise
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, contrast, tomogram_from_observations, metric_depth_axis
from sensitivity_sweep import (patch_observations_cfg, decompose_subapertures_w,
                               adjacent_trajectory_e, inject_damped_resonance)
from followup_experiments import (ZGRID_FIXED, alignment_null, per_patch_tomograms,
                                  interlook_autocorr)

V, R_KM, A_KM = 6000.0, 650.0, 42.0


def overlap_for(n_sub, f):
    if n_sub * f <= 1.0:
        raise ValueError(f"n_sub={n_sub} too small for look fraction f={f:.3f} (need n_sub > 1/f)")
    return (n_sub - 1.0 / f) / (n_sub - 1.0)


def peak_cells(T, zgrid):
    return float(zgrid[int(np.argmax(T.sum(0)))] / DZ_TARGET)


def run_config(slc, n_sub, f, window, estimator, n_perm, guard_cells, patch=64, n_patch=24, seed=0):
    H, W = slc.shape
    row = H // 2 - patch // 2
    cols = np.linspace(0, W - patch, n_patch).astype(int)
    ov = overlap_for(n_sub, f)
    obs, quals = patch_observations_cfg(slc, cols, row, patch, n_sub, ov, window,
                                        np.complex128, estimator)
    z_native = np.linspace(0, n_sub * DZ_TARGET / 2, 300)
    T_native = tomogram_from_observations(obs, z_native)
    T_fixed = tomogram_from_observations(obs, ZGRID_FIXED)
    c_fixed = contrast(T_fixed)
    algn = alignment_null(obs, ZGRID_FIXED, n_perm=n_perm, seed=seed)
    ratio = c_fixed / (np.median(algn) + 1e-12)
    pk = peak_cells(T_native, z_native)
    pinned = pk <= guard_cells

    # per-patch peaks beyond the guard
    Tp = per_patch_tomograms(obs, z_native)
    pp = z_native[np.argmax(Tp, axis=1)] / DZ_TARGET
    frac_beyond = float(np.mean(pp > guard_cells))

    # raw adjacent displacements (before accumulation) and inter-look correlation
    looks, _ = decompose_subapertures_w(slc, n_sub=n_sub, overlap=ov, axis=1,
                                        window=window, dtype=np.complex128)
    incs = []
    for cc in cols:
        traj, _ = adjacent_trajectory_e(looks[:, row:row + patch, cc:cc + patch], estimator=estimator)
        incs.append(np.diff(np.concatenate([[0.0], traj]))[1:])
    incs = np.abs(np.array(incs))
    lag1, lag2 = interlook_autocorr(obs)

    # hardened positive control (observation domain), on the fixed window
    z_inj = 0.7 * ZGRID_FIXED[-1]
    obs_pc = inject_damped_resonance(obs, ZGRID_FIXED, z_inj, 4 * np.std(obs))
    T_pc = tomogram_from_observations(obs_pc, ZGRID_FIXED)
    pc_ratio = contrast(T_pc) / (np.median(alignment_null(obs_pc, ZGRID_FIXED, n_perm=n_perm, seed=seed)) + 1e-12)
    pc_peak = peak_cells(T_pc, ZGRID_FIXED)
    pc_ok = bool(abs(pc_peak - z_inj / DZ_TARGET) <= 1.0 and pc_peak > guard_cells)

    labels = {}
    for fi in (10000.0, 22000.0):
        _, dz = metric_depth_axis(np.array([0.0]), V, fi, R_KM * 1e3, A_KM * 1e3)
        labels[f"{int(fi/1000)}kHz"] = dict(dz_m=float(dz), peak_m=float(pk * dz))

    verdict = ("surface-pinned artifact" if pinned else
               ("beyond guard and >=5x: check stability (falsification criteria)" if ratio >= 5 else
                "beyond guard, below 5x: no detection"))
    return dict(n_sub=n_sub, look_fraction=float(f), overlap=float(ov), window=window,
                c_fixed=float(c_fixed), align_null_median=float(np.median(algn)),
                ratio_align=float(ratio), peak_cells=pk, surface_pinned=bool(pinned),
                frac_patches_beyond_guard=frac_beyond,
                median_abs_adjacent_disp_px=float(np.median(incs)),
                lag1=lag1, lag2=lag2, quality=float(np.mean(quals)),
                pos_ctrl=dict(inject_cells=float(z_inj / DZ_TARGET), peak_cells=pc_peak,
                              ratio_align=float(pc_ratio), recovered=pc_ok),
                depth_labels=labels, verdict=verdict)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sicd", required=True)
    ap.add_argument("--arm", choices=["A", "B"], default="A")
    ap.add_argument("--look-seconds", type=float, default=6.0)
    ap.add_argument("--counts", nargs="*", type=int, default=[11])
    ap.add_argument("--window", default="hann")
    ap.add_argument("--estimator", default="phasecorr")
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--guard-cells", type=float, default=2.0)
    ap.add_argument("--noise", action="store_true", help="replace the crop with complex white noise")
    ap.add_argument("--out")
    a = ap.parse_args()

    from sarpy.io.complex.converter import open_complex
    rd = open_complex(a.sicd)
    m = rd.sicd_meta
    Rn, Cn = rd.data_size
    T = float(m.Timeline.CollectDuration)
    meta = dict(collect_s=T, az_imp_resp_bw=float(m.Grid.Col.ImpRespBW),
                az_res_m=float(m.Grid.Col.ImpRespWid), rows=Rn, cols=Cn)
    f = 0.5 if a.arm == "A" else min(1.0, a.look_seconds / T)
    crop = min(a.crop, Rn, Cn)
    r0, c0 = Rn // 2 - crop // 2, Cn // 2 - crop // 2
    slc = np.asarray(rd[r0:r0 + crop, c0:c0 + crop])
    label = os.path.basename(a.sicd)
    if a.noise:
        rng = np.random.default_rng(12345)
        slc = (rng.standard_normal(slc.shape) + 1j * rng.standard_normal(slc.shape)) / np.sqrt(2)
        label = "NOISE_like_" + label

    print(f"Test J  {label}  arm={a.arm}  f={f:.3f}  look_time={f*T:.2f} s of {T:.2f} s  window={a.window}")
    rows = []
    for n in a.counts:
        r = run_config(slc, n, f, a.window, a.estimator, a.n_perm, a.guard_cells)
        rows.append(r)
        print(f"  n_sub={n:3d} ov={r['overlap']:.3f}  ratio={r['ratio_align']:.2f}  peak={r['peak_cells']:.2f} cells  "
              f"pinned={r['surface_pinned']}  beyond-guard patches={r['frac_patches_beyond_guard']:.2f}  "
              f"|disp|={r['median_abs_adjacent_disp_px']:.4f}px  lag1={r['lag1']:.2f}  "
              f"posctrl={r['pos_ctrl']['recovered']} ({r['pos_ctrl']['ratio_align']:.1f}x)  -> {r['verdict']}")
    out = a.out or (f"runs/test_j_{'noise_' if a.noise else ''}{a.arm}_{a.window}_"
                    f"{os.path.splitext(os.path.basename(a.sicd))[0]}.json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(dict(test="J", arm=a.arm, look_fraction=f, look_seconds=f * T, label=label,
                   noise=a.noise, meta=meta, rows=rows,
                   prereg="docs/PREREGISTRATION_DISCLOSED_CONFIG_2026-11-09.md"),
              open(out, "w"), indent=1)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
