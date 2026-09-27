#!/usr/bin/env python3
"""
known_voids_umbra.py — pre-registered test G (docs/PREREGISTRATION_KNOWN_VOIDS_2026-09-27.md):
do the hundreds of surveyed 5-30 m mastaba shafts of the Giza Western and Eastern Cemeteries change the
single-pass tomogram relative to bare plateau, on the three free Umbra SICDs, with OUR unchanged pipeline?
(The open-data analogue of ejhong/sar R13.) Also the Q3 coherence diagnostic (descriptive).

Three modes, run in this order on the Mac (needs sarpy):
  python3.13 src/known_voids_umbra.py --placement   # amplitude-only crops + region boxes; NO tomogram
  (G.7 amendments after the first placement check are marked in the constants below.)
  python3.13 src/known_voids_umbra.py               # the pre-registered run -> runs/known_voids_umbra.json
  python3 src/known_voids_umbra.py --selftest       # synthetic plumbing check (no SICD)
"""
import argparse, glob, json, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from streak_surface import build, plant_tiles, PLANT_AMP
from shape_metric_giza import CANVAS, NSUB, SCENE_GLOB, PRIMARY_SCENE, git_rev
from tomogram import DZ_TARGET
from sensitivity_sweep import decompose_subapertures_w, fourier_shift_p
from micromotion import match_score

# ---- fixed in the prereg (G.2) — lat_min, lat_max, lon_min, lon_max ----
REGIONS = {
    "W_cemetery": (29.9785, 29.9830, 31.1255, 31.1320),
    "E_cemetery": (29.9770, 29.9805, 31.1365, 31.1395),
    "P1_plateau": (29.9700, 29.9750, 31.1100, 31.1170),
    "P2_plateau": (29.9600, 29.9650, 31.1200, 31.1270),
}
TARGETS, CONTROLS = ("W_cemetery", "E_cemetery"), ("P2_plateau",)
# ---- G.7 placement amendments (fixed from amplitude-only placement check, before any tomogram) ----
# P1 dropped (contains a built compound + road in 02-07 and 03-08). d_PP = P2 north half vs south half.
# 02-08: its SICD geolocation lands both cemetery boxes on roads; amplitude registration to 02-07 around
# the pyramids (corr 0.50 vs -0.02 at zero shift) gives a pixel correction; 02-08 is SECONDARY (reported,
# not in the verdict).
PIX_CORRECTION = {"giza_2023-02-08_UMBRA-04": (576, -420)}
SECONDARY = {"giza_2023-02-08_UMBRA-04"}
NODATA_FRAC = 0.01
ZGRID = np.linspace(0, NSUB * DZ_TARGET / 2, 300)           # identical to build()
BAND = (ZGRID >= 5.0) & (ZGRID <= 30.0)                     # ejhong's 5-30 m band, in our axis units
D_MIN, NBINS, SEED = 0.2, 10, 0


def centroid(V):
    P = V / V.sum(axis=2, keepdims=True)
    return (P * ZGRID).sum(axis=2), P[..., BAND].sum(axis=2)


def std_diff(a, b):
    s = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return float((a.mean() - b.mean()) / (s + 1e-300))


def match_brightness(ma, mb, rng):
    """Indices into a and b with equal counts per pooled log-brightness decile."""
    la, lb = np.log(ma), np.log(mb)
    edges = np.quantile(np.concatenate([la, lb]), np.linspace(0, 1, NBINS + 1))
    ia, ib = [], []
    for k in range(NBINS):
        lo, hi = edges[k], edges[k + 1]
        a = np.where((la >= lo) & ((la < hi) if k < NBINS - 1 else (la <= hi)))[0]
        b = np.where((lb >= lo) & ((lb < hi) if k < NBINS - 1 else (lb <= hi)))[0]
        n = min(len(a), len(b))
        if n:
            ia += list(rng.choice(a, n, replace=False)); ib += list(rng.choice(b, n, replace=False))
    return np.array(ia, int), np.array(ib, int)


def compare(ta, tb, rng):
    """ta/tb: dicts of per-tile arrays c, f, M. Brightness-matched standardised differences."""
    ia, ib = match_brightness(ta["M"], tb["M"], rng)
    return dict(n_matched=int(len(ia)), d_centroid=std_diff(ta["c"][ia], tb["c"][ib]),
                d_band=std_diff(ta["f"][ia], tb["f"][ib]),
                d_centroid_unmatched=std_diff(ta["c"], tb["c"]))


# ---------------- geometry (sarpy, Mac only) ----------------
def open_scene(path):
    from sarpy.io.complex.converter import open_complex
    rd = open_complex(path)
    return rd, rd.sicd_meta


def to_image(sicd, lat, lon):
    from sarpy.geometry.point_projection import ground_to_image_geo
    hae = sicd.GeoData.SCP.LLH.HAE
    ip = ground_to_image_geo(np.array([[lat, lon, hae]]), sicd)[0]
    return np.asarray(ip).reshape(-1, 2)[0]


def tile_latlon(sicd, r0, c0, nr, nc, corr=(0, 0)):
    from sarpy.geometry.point_projection import image_to_ground_geo
    from shape_metric_giza import PATCH, STRIDE
    pts = np.array([[r0 - corr[0] + PATCH / 2 + i * STRIDE, c0 - corr[1] + PATCH / 2 + j * STRIDE]
                    for i in range(nr) for j in range(nc)], float)
    llh = np.asarray(image_to_ground_geo(pts, sicd))
    return llh[:, 0].reshape(nr, nc), llh[:, 1].reshape(nr, nc)


def region_crop(rd, sicd, box, corr=(0, 0)):
    lat0, lat1, lon0, lon1 = box
    rc = to_image(sicd, (lat0 + lat1) / 2, (lon0 + lon1) / 2) + np.array(corr)
    R, C = sicd.ImageData.NumRows, sicd.ImageData.NumCols
    r0 = int(np.clip(round(rc[0]) - CANVAS // 2, 0, R - CANVAS))
    c0 = int(np.clip(round(rc[1]) - CANVAS // 2, 0, C - CANVAS))
    img = np.asarray(rd[r0:r0 + CANVAS, c0:c0 + CANVAS], dtype=np.complex128)
    return img, r0, c0


def inside(lat, lon, box):
    return (lat >= box[0]) & (lat <= box[1]) & (lon >= box[2]) & (lon <= box[3])


# ---------------- Q3 coherence diagnostic (descriptive) ----------------
def coherence_diag(img, sicd=None):
    looks, _ = decompose_subapertures_w(img, n_sub=NSUB, overlap=0.8, axis=1, window="hann",
                                        dtype=np.complex128)
    mid = NSUB // 2
    vs_centre = [match_score(looks[mid], looks[k]) for k in range(NSUB)]
    adjacent = [match_score(looks[k - 1], looks[k]) for k in range(1, NSUB)]
    out = dict(match_vs_centre_look=vs_centre, match_adjacent=adjacent)
    if sicd is not None:
        T = sicd.ImageFormation.TEndProc - sicd.ImageFormation.TStartProc
        w = T / (1 + (NSUB - 1) * 0.2)
        out["centre_spacing_s"] = float((T - w) / (NSUB - 1))
        out["subaperture_s"] = float(w)
    return out


# ---------------- main runs ----------------
def placement():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    os.makedirs("runs", exist_ok=True)
    for p in sorted(glob.glob(SCENE_GLOB)):
        name = os.path.basename(p).split("_SICD")[0]
        rd, sicd = open_scene(p)
        corr = PIX_CORRECTION.get(name, (0, 0))
        fig, axs = plt.subplots(1, 4, figsize=(20, 5.4))
        for ax, (reg, box) in zip(axs, REGIONS.items()):
            img, r0, c0 = region_crop(rd, sicd, box, corr)
            a = 20 * np.log10(np.abs(img) + 1e-6)
            ax.imshow(a, cmap="gray", vmin=np.percentile(a, 2), vmax=np.percentile(a, 99.5))
            corners = [(box[0], box[2]), (box[0], box[3]), (box[1], box[3]), (box[1], box[2]), (box[0], box[2])]
            pts = np.array([to_image(sicd, la, lo) + np.array(corr) for la, lo in corners])
            ax.plot(pts[:, 1] - c0, pts[:, 0] - r0, "r-", lw=1.5)
            ax.set_title(f"{reg}  crop r{r0} c{c0}"); ax.set_axis_off()
        fig.suptitle(f"{name}: SLC amplitude only (placement check, G.3) — no tomogram built")
        fig.tight_layout(); fig.savefig(f"runs/known_voids_placement_{name}.png", dpi=80); plt.close(fig)
        print(f"{name}: -> runs/known_voids_placement_{name}.png", flush=True)


def per_region(img, sicd, r0, c0, box, plant=False, corr=(0, 0)):
    V, cov = build(img)
    nr, nc = V.shape[:2]
    lat, lon = tile_latlon(sicd, r0, c0, nr, nc, corr)
    m = inside(lat, lon, box) & (cov["M"] > NODATA_FRAC * np.median(cov["M"]))
    out = dict(V=V, cov=cov, mask=m, lat=lat)
    if plant:
        cand = [tuple(x) for x in np.argwhere(m)]
        rng = np.random.default_rng(11)
        k = max(1, len(cand) // 4)
        sel = [cand[i] for i in rng.choice(len(cand), k, replace=False)]
        Vp, covp = build(img, plant=sel)
        out.update(Vp=Vp, planted=sel)
    return out


def arrays(V, cov, mask, sel=None):
    c, f = centroid(V)
    if sel is not None:
        mm = np.zeros_like(mask); [mm.__setitem__(t, True) for t in sel]; mask = mm
    return dict(c=c[mask], f=f[mask], M=cov["M"][mask])


def main_real():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    res = dict(prereg="docs/PREREGISTRATION_KNOWN_VOIDS_2026-09-27.md", script="src/known_voids_umbra.py",
               git=git_rev(), regions=REGIONS, band_axis_units=[5.0, 30.0], d_min=D_MIN, scenes={})
    for p in sorted(glob.glob(SCENE_GLOB)):
        name = os.path.basename(p).split("_SICD")[0]
        rd, sicd = open_scene(p)
        corr = PIX_CORRECTION.get(name, (0, 0))
        R = {}
        for reg in TARGETS + CONTROLS:
            box = REGIONS[reg]
            img, r0, c0 = region_crop(rd, sicd, box, corr)
            R[reg] = per_region(img, sicd, r0, c0, box, plant=(reg in TARGETS), corr=corr)
            R[reg]["img"] = img if reg == "P2_plateau" else None
        cem = {k: np.concatenate([arrays(R[t]["V"], R[t]["cov"], R[t]["mask"])[k] for t in TARGETS]) for k in "cfM"}
        pla = {k: np.concatenate([arrays(R[t]["V"], R[t]["cov"], R[t]["mask"])[k] for t in CONTROLS]) for k in "cfM"}
        q = R["P2_plateau"]; latmed = np.median(q["lat"][q["mask"]])
        p1 = arrays(q["V"], q["cov"], q["mask"] & (q["lat"] >= latmed))
        p2 = arrays(q["V"], q["cov"], q["mask"] & (q["lat"] < latmed))
        main = compare(cem, pla, rng)
        pp = compare(p1, p2, rng)
        # positive control: the same cemetery crops with displacement planted in 25% of cemetery tiles
        pc = {k: np.concatenate([arrays(R[t]["Vp"], R[t]["cov"], R[t]["mask"], R[t]["planted"])[k]
                                 for t in TARGETS]) for k in "cfM"}
        ctrl = compare(pc, pla, rng)
        ctrl_pass = abs(ctrl["d_centroid"]) >= D_MIN
        n_tiles = {reg: int(R[reg]["mask"].sum()) for reg in TARGETS + CONTROLS}
        hit = abs(main["d_centroid"]) >= D_MIN and abs(main["d_centroid"]) > abs(pp["d_centroid"])
        verdict = ("INCONCLUSIVE (control failed)" if not ctrl_pass else
                   "INCONCLUSIVE (too few tiles)" if min(n_tiles.values()) < 20 else
                   "DIFFERS" if hit else "NULL")
        res["scenes"][name] = dict(secondary=name in SECONDARY, pix_correction=list(corr), n_tiles=n_tiles, cem_vs_plateau=main, plateau_vs_plateau=pp,
                                   control=dict(**ctrl, passed=bool(ctrl_pass), amp_px=PLANT_AMP),
                                   verdict=verdict,
                                   q3_coherence=coherence_diag(R["P2_plateau"]["img"], sicd))
        print(f"{name}: tiles {n_tiles}  d_centroid cem-plat {main['d_centroid']:+.3f} "
              f"(plat-plat {pp['d_centroid']:+.3f})  d_band {main['d_band']:+.3f}  "
              f"control {ctrl['d_centroid']:+.3f} -> {verdict}{'  [SECONDARY]' if name in SECONDARY else ''}", flush=True)
    sc = {n: v for n, v in res["scenes"].items() if n not in SECONDARY}
    diffs = [n for n, s in sc.items() if s["verdict"] == "DIFFERS"]
    nulls = [n for n, s in sc.items() if s["verdict"] == "NULL"]
    signs = {np.sign(sc[n]["cem_vs_plateau"]["d_centroid"]) for n in diffs}
    res["overall"] = ("KNOWN VOIDS DETECTED" if len(diffs) == len(sc) == 2 and len(signs) == 1 else
                      "NULL (known voids not distinguished)" if len(nulls) == len(sc) == 2 else "MIXED/INCONCLUSIVE")
    print(f"\nOVERALL: {res['overall']}")
    json.dump(res, open("runs/known_voids_umbra.json", "w"), indent=1, default=float)
    print(f"-> runs/known_voids_umbra.json ({time.time()-t0:.0f}s)")


def selftest():
    """No SICD: synthetic speckle stands in for all four regions (all tiles 'inside').
    (a) two independent empty crops must NOT differ (|d| < D_MIN); (b) planted displacement in 25%
    of one crop's tiles must be detected (|d_centroid| >= D_MIN)."""
    from volume_render import bandlimited_slc
    from shape_metric_giza import BW_NULL
    rng = np.random.default_rng(SEED)
    A = bandlimited_slc(CANVAS, BW_NULL, np.random.default_rng(1))
    B = bandlimited_slc(CANVAS, BW_NULL, np.random.default_rng(2))
    VA, cA = build(A); VB, cB = build(B)
    allm = np.ones(VA.shape[:2], bool)
    a, b = arrays(VA, cA, allm), arrays(VB, cB, allm)
    e = compare(a, b, rng)
    cand = [tuple(x) for x in np.argwhere(allm)]
    sel = [cand[i] for i in np.random.default_rng(11).choice(len(cand), len(cand) // 4, replace=False)]
    VP, _ = build(A, plant=sel)
    pl = compare(arrays(VP, cA, allm, sel), b, rng)
    q3 = coherence_diag(A)
    print(f"[a] empty vs empty: d_centroid {e['d_centroid']:+.3f}  d_band {e['d_band']:+.3f}  (want |d| < {D_MIN})")
    print(f"[b] planted vs empty: d_centroid {pl['d_centroid']:+.3f}  (want |d| >= {D_MIN})")
    print(f"[q3] match adjacent {np.round(q3['match_adjacent'], 3).tolist()}")
    return abs(e["d_centroid"]) < D_MIN and abs(pl["d_centroid"]) >= D_MIN


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--placement", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    elif a.placement:
        placement()
    else:
        main_real()
