#!/usr/bin/env python3
"""
increments_order_null.py — pre-registered test H (docs/PREREGISTRATION_INCREMENTS_2026-09-27.md):
is the "increments anomaly" (peak stays pinned after de-accumulation on 2 of 3 Giza scenes) anything more
than chance? Per scene, the REAL increments are compared with a look-order-shuffle null built from those
same increments (each tile's increment values kept, their order across looks randomised; inc[0]=0 stays
first). Identical E8 configuration: 512 centre crop, patch 64, 24 patches on the centre row, n_sub 11,
overlap 0.8, Hann, phasecorr, degree-2 detrend, 300 bins, guard 2 cells, dz_phys from (6000 m/s, 22 kHz,
650 km, 42 km).

  python3.13 src/increments_order_null.py            # real run (sarpy) -> runs/increments_order_null.json
  python3 src/increments_order_null.py --selftest    # synthetic, no SICD
"""
import argparse, glob, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, contrast, tomogram_from_observations, metric_depth_axis
from micromotion import detrend
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e

N_SUB, OVERLAP, PATCH, N_PATCH, CROP = 11, 0.8, 64, 24, 512
GUARD, N_SHUF, SEED, ALPHA = 2.0, 1000, 0, 0.05
_, DZ_PHYS = metric_depth_axis(np.array([0.0]), 6000.0, 22000.0, 650e3, 42e3)
Z = np.linspace(0, N_SUB * DZ_TARGET / 2, 300)


def increments(img):
    looks, _ = decompose_subapertures_w(img, n_sub=N_SUB, overlap=OVERLAP, axis=1, window="hann",
                                        dtype=np.complex128)
    r0 = img.shape[0] // 2 - PATCH // 2
    cols = np.linspace(0, img.shape[1] - PATCH, N_PATCH).astype(int)
    inc = []
    for cc in cols:
        t, _q = adjacent_trajectory_e(looks[:, r0:r0 + PATCH, cc:cc + PATCH], estimator="phasecorr",
                                      dtype=np.complex128)
        t = np.asarray(t, float)
        inc.append(np.concatenate([[0.0], np.diff(t)]))
    return np.array(inc)


def peak_cells(arr):
    obs = np.array([detrend(t, deg=2) for t in arr])
    T = tomogram_from_observations(obs, Z)
    z_m = Z * (DZ_PHYS / DZ_TARGET)
    return float(z_m[int(np.argmax(T.sum(0)))] / DZ_PHYS), float(contrast(T))


def lag1(arr):
    v = [np.corrcoef(a[1:-1], a[2:])[0, 1] for a in arr if np.std(a[1:]) > 0]
    return float(np.nanmean(v))


def order_null(inc, rng):
    out = np.empty(N_SHUF)
    for k in range(N_SHUF):
        sh = inc.copy()
        for row in sh:
            row[1:] = row[1:][rng.permutation(len(row) - 1)]
        out[k] = peak_cells(sh)[0]
    return out


def analyse(inc, rng):
    pk_inc, c_inc = peak_cells(inc)
    pk_cum, c_cum = peak_cells(np.cumsum(inc, axis=1))
    null = order_null(inc, rng)
    pct = float(np.mean(null <= pk_inc))
    return dict(peak_cumsum=pk_cum, contrast_cumsum=c_cum, peak_inc=pk_inc, contrast_inc=c_inc,
                inc_pinned=bool(pk_inc <= GUARD), lag1_inc=lag1(inc),
                null_median=float(np.median(null)), null_p05=float(np.quantile(null, 0.05)),
                null_pinned_frac=float(np.mean(null <= GUARD)), percentile_of_observed=pct,
                anomalous=bool(pct < ALPHA))


def main_real():
    from sarpy.io.complex.converter import open_complex
    from shape_metric_giza import git_rev
    rng = np.random.default_rng(SEED)
    res = dict(prereg="docs/PREREGISTRATION_INCREMENTS_2026-09-27.md", script="src/increments_order_null.py",
               git=git_rev(), dz_phys=DZ_PHYS, n_shuffles=N_SHUF, alpha=ALPHA, scenes={})
    for p in sorted(glob.glob("data/giza_*_SICD.nitf")):
        name = os.path.basename(p).split("_SICD")[0]
        rd = open_complex(p); R, C = rd.data_size
        r0, c0 = R // 2 - CROP // 2, C // 2 - CROP // 2
        img = np.asarray(rd[r0:r0 + CROP, c0:c0 + CROP], dtype=np.complex128)
        a = analyse(increments(img), rng)
        res["scenes"][name] = a
        print(f"{name}: cumsum peak {a['peak_cumsum']:.2f}  increments peak {a['peak_inc']:.2f} "
              f"({'PIN' if a['inc_pinned'] else 'clear'})  lag-1 {a['lag1_inc']:+.3f}  | order-shuffle null: "
              f"median {a['null_median']:.2f}, pinned {100*a['null_pinned_frac']:.0f}%  -> observed at "
              f"percentile {100*a['percentile_of_observed']:.1f}  {'ANOMALOUS' if a['anomalous'] else 'not anomalous'}",
              flush=True)
    n_anom = sum(s["anomalous"] for s in res["scenes"].values())
    res["overall"] = ("ORDER-DEPENDENT PINNING (anomaly real)" if n_anom >= 2 else
                      "NOT ANOMALOUS (consistent with the order-shuffle null)" if n_anom == 0 else
                      "MIXED (1 of 3)")
    print(f"\nOVERALL: {res['overall']}")
    os.makedirs("runs", exist_ok=True)
    json.dump(res, open("runs/increments_order_null.json", "w"), indent=1)
    print("-> runs/increments_order_null.json")


def selftest():
    """(a) white-noise image: observed should sit mid-null (not anomalous);
    (b) increments plus a planted look-ordered one-cycle component (order-dependent pinning) must be flagged."""
    global N_SHUF
    N_SHUF = 300
    rng = np.random.default_rng(1)
    img = (rng.normal(0, 1, (CROP, CROP)) + 1j * rng.normal(0, 1, (CROP, CROP))).astype(np.complex128)
    inc = increments(img)
    a = analyse(inc, np.random.default_rng(SEED))
    ramp = inc.copy()
    # one full cycle across the looks: an ORDERED component that survives the deg-2 detrend and sits at
    # the surface-pinned mode (~1.6-1.7 cells). Amplitude = 1 sd of the increments. Fixed from synthetic only.
    ramp[:, 1:] += 1.0 * inc[:, 1:].std() * np.sin(2 * np.pi * np.arange(1, N_SUB) / (N_SUB - 1))
    b = analyse(ramp, np.random.default_rng(SEED))
    print(f"[a] white noise: inc peak {a['peak_inc']:.2f}, null median {a['null_median']:.2f}, "
          f"percentile {100*a['percentile_of_observed']:.1f} -> {'ANOMALOUS' if a['anomalous'] else 'ok'}")
    print(f"[b] planted slow ordered component: inc peak {b['peak_inc']:.2f}, percentile "
          f"{100*b['percentile_of_observed']:.1f} -> {'flagged' if b['anomalous'] else 'MISSED'}")
    return (not a["anomalous"]) and b["anomalous"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(0 if selftest() else 1) if a.selftest else main_real()
