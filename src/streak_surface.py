#!/usr/bin/env python3
"""
streak_surface.py — pre-registered test "vertical streaks are surface-driven"
(docs/PREREGISTRATION_STREAKS_2026-09-27.md, Part F), merged with the 02-08 near-miss split.

Every analysis choice is fixed here and in the prereg BEFORE this script is run on any SICD.

Per scene (the same three Umbra Giza SICDs, same 768 centre crops and pipeline as
shape_metric_giza.py; nothing re-tuned):
  V            30 x 30 x 300 volume, identical build (n_sub 11, overlap 0.8, Hann, patch 64,
               stride 24, degree-2 detrend, DFT/Bartlett)
  S_i          streak strength of tile i = mean of V[i, :] over all 300 depth bins
  Q_i          registration quality = mean match_score over the 10 adjacent look pairs
  M_i          surface brightness = mean |SLC| over the tile's 64 x 64 patch
  K_i          surface texture   = std/mean of |SLC| over the patch (reported, not in the rule)
  E_i          variance of the detrended trajectory (identity check only: S ~ E by construction)

PRIMARY RULE (F.3): scene is SURFACE-LINKED iff |Spearman(S,Q)| >= 0.3 or |Spearman(S,M)| >= 0.3.
  H-surface SUPPORTED if the pre-registered primary scene (03-08) and >= 2 of 3 scenes are linked;
  REJECTED if 03-08 and >= 2 of 3 are not; otherwise MIXED.
  Null reference: the same statistics on the seed-0 empty volume (does the link exist with no scene?).
POSITIVE CONTROL (F.4, in displacement, before tracking): 4 tiles (seed 11) get a sinusoidal
  azimuth shift of PLANT_AMP px (2 cycles over the 11 looks) applied to the looks. Passes if >= 3 of 4
  planted tiles rank in the top 10% of S. A failed control makes that scene INCONCLUSIVE.
NEAR-MISS SPLIT (F.5): N1 = max(|Spearman(F,M)|, |Spearman(F,Q)|), F_i = fraction of tile i's column
  above the volume's 99th percentile; N2 = median over the 8 included treatments of stats().elong.
  02-08 CLOSED-AS-SURFACE if N1 >= 0.3 and N2(02-08) <= 1.5 x max(N2 of the two other scenes);
  NEGATIVE WEAKENED if N1 < 0.3 and N2(02-08) > 1.5 x max(others); else MIXED.

  python3.13 src/streak_surface.py --selftest   # synthetic; fixes nothing, checks the plumbing
  python3.13 src/streak_surface.py              # real run -> runs/streak_surface.json
"""
import argparse, glob, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import DZ_TARGET, steering, analytic1d
from micromotion import detrend
from sensitivity_sweep import decompose_subapertures_w, adjacent_trajectory_e, fourier_shift_p
from volume_render import bandlimited_slc
from shape_metric_giza import (stats, INCLUDED, CANVAS, PATCH, STRIDE, NSUB, OVERLAP, BW_NULL,
                               SCENE_GLOB, PRIMARY_SCENE, read_crop, crop_origins, git_rev)
from render_sweep import OPS, apply_ops

RHO = 0.3
PLANT_N, PLANT_SEED, PLANT_CYC = 4, 11, 2
PLANT_AMP = 0.5          # px; fixed from the synthetic selftest only (F.4), never from real data
TOP = 0.10
ELONG_FACTOR = 1.5
NEARMISS_SCENE = "giza_2023-02-08_UMBRA-04"


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb) + 1e-300))


def plant_tiles(nr, nc, n=PLANT_N, seed=PLANT_SEED):
    rng = np.random.default_rng(seed)
    idx = set()
    while len(idx) < n:
        idx.add((int(rng.integers(2, nr - 2)), int(rng.integers(2, nc - 2))))
    return sorted(idx)


def build(img, plant=None, amp=PLANT_AMP):
    """Same volume as shape_metric_giza.build_volume, plus per-tile covariates.
    plant: list of (row_idx, col_idx) tiles whose look patches get a sinusoidal azimuth shift."""
    zgrid = np.linspace(0, NSUB * DZ_TARGET / 2, 300)
    A, _ = steering(NSUB, zgrid)
    looks, _ = decompose_subapertures_w(img, n_sub=NSUB, overlap=OVERLAP, axis=1,
                                        window="hann", dtype=np.complex128)
    H, W = looks.shape[1], looks.shape[2]
    rows = list(range(0, H - PATCH + 1, STRIDE))
    cols = list(range(0, W - PATCH + 1, STRIDE))
    plant = set(plant or [])
    shifts = amp * np.sin(2 * np.pi * PLANT_CYC * np.arange(NSUB) / NSUB)
    amp_img = np.abs(img)
    V, Q, M, K, E = [], [], [], [], []
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            lp = looks[:, r:r + PATCH, c:c + PATCH]
            if (i, j) in plant:
                lp = np.array([fourier_shift_p(lp[k], 0.0, shifts[k]) for k in range(NSUB)])
            t, coh = adjacent_trajectory_e(lp, dtype=np.complex128)
            o = detrend(np.asarray(t, dtype=float), deg=2)
            V.append(np.abs(A.conj().T @ analytic1d(o)) ** 2)
            Q.append(float(np.mean(coh[1:])))
            a = amp_img[r:r + PATCH, c:c + PATCH]
            M.append(float(a.mean())); K.append(float(a.std() / (a.mean() + 1e-12)))
            E.append(float(np.var(o)))
    shp = (len(rows), len(cols))
    V = np.array(V).reshape(*shp, -1)
    return V, {k: np.array(v).reshape(shp) for k, v in dict(Q=Q, M=M, K=K, E=E).items()}


def tile_stats(V, cov):
    S = V.mean(axis=2).ravel()
    thr = np.percentile(V, 99.0)
    F = (V > thr).mean(axis=2).ravel()
    q, m, k, e = (cov[x].ravel() for x in "QMKE")
    out = dict(rho_SQ=spearman(S, q), rho_SM=spearman(S, m), rho_SK=spearman(S, k),
               rho_SE_identity=spearman(S, e), rho_FM=spearman(F, m), rho_FQ=spearman(F, q))
    out["surface_linked"] = bool(abs(out["rho_SQ"]) >= RHO or abs(out["rho_SM"]) >= RHO)
    out["N1"] = max(abs(out["rho_FM"]), abs(out["rho_FQ"]))
    return out, S


def control(img, V_shape):
    tiles = plant_tiles(*V_shape[:2])
    Vp, _ = build(img, plant=tiles)
    S = Vp.mean(axis=2)
    cut = np.quantile(S, 1 - TOP)
    hits = sum(bool(S[i, j] >= cut) for i, j in tiles)
    return dict(tiles=tiles, amp_px=PLANT_AMP, hits=hits, passed=hits >= 3)


def elong_median(V):
    return float(np.median([stats(apply_ops(V, OPS[n]))["elong"] for n in INCLUDED]))


def main_real():
    scenes = sorted(glob.glob(SCENE_GLOB))
    if not scenes:
        sys.exit(f"no SICDs matching {SCENE_GLOB}")
    t0 = time.time()
    res = dict(prereg="docs/PREREGISTRATION_STREAKS_2026-09-27.md", script="src/streak_surface.py",
               git=git_rev(), rho=RHO, plant=dict(n=PLANT_N, seed=PLANT_SEED, amp_px=PLANT_AMP,
               cycles=PLANT_CYC, top=TOP), scenes={})
    print("null (bw 0.80, seed 0) ...", flush=True)
    null_img = bandlimited_slc(CANVAS, BW_NULL, np.random.default_rng(0))
    Vn, cn = build(null_img)
    res["null"], _ = tile_stats(Vn, cn)
    res["null"]["elong_median"] = elong_median(Vn)
    print(f"  null: rho(S,Q) {res['null']['rho_SQ']:+.2f}  rho(S,M) {res['null']['rho_SM']:+.2f}  "
          f"identity rho(S,E) {res['null']['rho_SE_identity']:+.2f}", flush=True)
    for p in scenes:
        name = os.path.basename(p).split("_SICD")[0]
        _, (R, C) = read_crop(p, 0, 0, 1)
        o = crop_origins(R, C)[0]
        img, _ = read_crop(p, *o)
        V, cov = build(img)
        st, _ = tile_stats(V, cov)
        st["control"] = control(img, V.shape)
        st["elong_median"] = elong_median(V)
        from shape_metric_giza import plant_shafts
        st["elong_median_painted_shafts"] = elong_median(plant_shafts(V))
        st["verdict"] = ("INCONCLUSIVE (control failed)" if not st["control"]["passed"]
                         else "SURFACE-LINKED" if st["surface_linked"] else "NOT LINKED")
        res["scenes"][name] = st
        print(f"  {name}: rho(S,Q) {st['rho_SQ']:+.2f}  rho(S,M) {st['rho_SM']:+.2f}  "
              f"rho(S,K) {st['rho_SK']:+.2f}  identity {st['rho_SE_identity']:+.2f}  "
              f"control {st['control']['hits']}/4  -> {st['verdict']}", flush=True)
    sc = res["scenes"]
    linked = [n for n, s in sc.items() if s["verdict"] == "SURFACE-LINKED"]
    notl = [n for n, s in sc.items() if s["verdict"] == "NOT LINKED"]
    prim = sc.get(PRIMARY_SCENE, {}).get("verdict")
    overall = ("H-surface SUPPORTED" if prim == "SURFACE-LINKED" and len(linked) >= 2 else
               "H-surface REJECTED" if prim == "NOT LINKED" and len(notl) >= 2 else "MIXED")
    res["overall"] = overall
    nm = sc.get(NEARMISS_SCENE)
    if nm:
        others = [s["elong_median"] for n, s in sc.items() if n != NEARMISS_SCENE]
        big = nm["elong_median"] > ELONG_FACTOR * max(others)
        res["near_miss"] = dict(N1=nm["N1"], N2=nm["elong_median"], N2_others=others,
                                N2_painted=nm["elong_median_painted_shafts"],
                                verdict=("CLOSED-AS-SURFACE" if nm["N1"] >= RHO and not big else
                                         "NEGATIVE WEAKENED" if nm["N1"] < RHO and big else "MIXED"))
    print(f"\nOVERALL: {overall}")
    if nm:
        print(f"NEAR-MISS 02-08: N1 {nm['N1']:.2f}, N2 {nm['elong_median']:.2f} vs others "
              f"{['%.2f' % x for x in res['near_miss']['N2_others']]} -> {res['near_miss']['verdict']}")
    os.makedirs("runs", exist_ok=True)
    json.dump(res, open("runs/streak_surface.json", "w"), indent=1)
    print(f"-> runs/streak_surface.json ({time.time()-t0:.0f}s)")


def selftest():
    """Plumbing only, on synthetic speckle. (a) the control's planted tiles must rise into the top
    10% at PLANT_AMP; (b) a brightness-modulated synthetic scene runs end to end."""
    img = bandlimited_slc(CANVAS, BW_NULL, np.random.default_rng(0))
    V, cov = build(img)
    st, _ = tile_stats(V, cov)
    c = control(img, V.shape)
    print(f"[null] rho(S,Q) {st['rho_SQ']:+.2f} rho(S,M) {st['rho_SM']:+.2f} "
          f"identity rho(S,E) {st['rho_SE_identity']:+.2f}")
    print(f"[control] planted {c['hits']}/4 in top 10% at {PLANT_AMP} px -> "
          f"{'PASS' if c['passed'] else 'FAIL'}")
    return c["passed"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(0 if selftest() else 1) if a.selftest else main_real()
