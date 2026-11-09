#!/usr/bin/env python3
"""
Test K — topographic parallax as a known, physical inter-look displacement
(never pre-registered; see STATUS).

STATUS 10 Nov 2026: NOT RUN and NOT pre-registered. The geometry stage showed the predicted effect is
0.003-0.08 px per look step per 100 m of height on the three Giza scenes, below the ~0.2 px tracking floor
(hypothesis H2 withdrawn; see docs/REVIEW_BIONDI2022_KHUFU_2026-11-10.md, section 6). Kept as a geometry
tool: R/Rdot projection at any slow time, look-centre times, pyramid model, QA overlay.

A scatterer at height h above the focus plane is imaged, by a sub-aperture centred at slow time t,
at the image-plane point with the same range and range-rate at t (R/Rdot projection).

Stages (run separately so geometry is fixed before any displacement is looked at):
  --qa       amplitude image + projected pyramid wireframe (no displacement data)
  --run      measure adjacent-look displacement per patch, compare with the geometric prediction
  --selftest solver checks on synthetic geometry (no SAR data)
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# name: (lat, lon, base side m, height as it stands m, base height above ellipsoid m)
PYRAMIDS = {
    "khufu":  (29.979167, 31.134167, 230.33, 138.5, 75.5),
    "khafre": (29.976111, 31.130833, 215.25, 136.4, 85.5),
}
A_WGS, E2 = 6378137.0, 6.69437999014e-3


def llh_to_ecf(lat, lon, h):
    la, lo = np.radians(lat), np.radians(lon)
    n = A_WGS / np.sqrt(1 - E2 * np.sin(la) ** 2)
    return np.array([(n + h) * np.cos(la) * np.cos(lo), (n + h) * np.cos(la) * np.sin(lo),
                     (n * (1 - E2) + h) * np.sin(la)])


def enu_basis(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    e = np.array([-np.sin(lo), np.cos(lo), 0.0])
    n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    u = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return e, n, u


def pyramid_points(name, spacing=3.0, de=0.0, dn=0.0):
    """Surface points of a square pyramid aligned to true north. Returns (ECEF Nx3, height N, face N).
    de/dn: translation of the whole model in metres east/north (set at the QA stage only)."""
    lat, lon, side, H, base = PYRAMIDS[name]
    half = side / 2
    g = np.arange(-half, half + 1e-6, spacing)
    E, N = np.meshgrid(g, g)
    E, N = E.ravel(), N.ravel()
    h = H * (1 - np.maximum(np.abs(E), np.abs(N)) / half)
    face = np.where(np.abs(E) >= np.abs(N), np.where(E > 0, 0, 2), np.where(N > 0, 1, 3))  # E,N,W,S
    o = llh_to_ecf(lat, lon, base)
    e, n, u = enu_basis(lat, lon)
    X = o + np.outer(E + de, e) + np.outer(N + dn, n) + np.outer(h, u)
    return X, h, face


def wireframe(name, de=0.0, dn=0.0):
    lat, lon, side, H, base = PYRAMIDS[name]
    half = side / 2
    o = llh_to_ecf(lat, lon, base)
    e, n, u = enu_basis(lat, lon)
    c = [(-half, -half), (half, -half), (half, half), (-half, half)]
    P = [o + (x + de) * e + (y + dn) * n for x, y in c]
    apex = o + de * e + dn * n + H * u
    segs = [(P[i], P[(i + 1) % 4]) for i in range(4)] + [(p, apex) for p in P]
    return segs


class Geom:
    """Minimal SICD geometry: ARP polynomial, slant image plane, look-centre times."""
    def __init__(self, m):
        self.scp = m.GeoData.SCP.ECF.get_array()
        self.urow = m.Grid.Row.UVectECF.get_array()
        self.ucol = m.Grid.Col.UVectECF.get_array()
        self.rss, self.css = float(m.Grid.Row.SS), float(m.Grid.Col.SS)
        self.scp_pix = m.ImageData.SCPPixel.get_array().astype(float)
        self.first = np.array([m.ImageData.FirstRow, m.ImageData.FirstCol], float)
        self.arp_poly = m.Position.ARPPoly
        self.t_coa = float(m.SCPCOA.SCPTime)
        self.col_sgn = int(m.Grid.Col.Sgn)
        self.col_bw = float(m.Grid.Col.ImpRespBW)
        self.krow = float(m.Grid.Row.KCtr)
        self.pa = np.array(m.PFA.PolarAngPoly.Coefs, float)
        self.T = float(m.Timeline.CollectDuration)

    def arp(self, t):
        return np.asarray(self.arp_poly(t), float)

    def varp(self, t):
        return np.asarray(self.arp_poly.derivative_eval(t, der_order=1), float)

    def project(self, X, t, iters=8):
        """R/Rdot projection of ECEF points X (N,3) at slow time t onto the slant image plane.
        Returns pixel coordinates (N,2) = (row, col), full-image indexing."""
        p, v = self.arp(t), self.varp(t)
        d = X - p
        R = np.linalg.norm(d, axis=1)
        Rd = -(d @ v) / R
        ab = np.zeros((len(X), 2))
        for _ in range(iters):
            S = self.scp + np.outer(ab[:, 0], self.urow) + np.outer(ab[:, 1], self.ucol)
            ds = S - p
            Rs = np.linalg.norm(ds, axis=1)
            f1 = Rs - R
            f2 = -(ds @ v) / Rs - Rd
            # Jacobian
            dR_da, dR_db = (ds @ self.urow) / Rs, (ds @ self.ucol) / Rs
            dD_da = -(self.urow @ v) / Rs + (ds @ v) * dR_da / Rs ** 2
            dD_db = -(self.ucol @ v) / Rs + (ds @ v) * dR_db / Rs ** 2
            det = dR_da * dD_db - dR_db * dD_da
            ab[:, 0] -= (f1 * dD_db - f2 * dR_db) / det
            ab[:, 1] -= (-f1 * dD_da + f2 * dR_da) / det
        return np.stack([self.scp_pix[0] + ab[:, 0] / self.rss, self.scp_pix[1] + ab[:, 1] / self.css], 1)

    def look_times(self, n_cols, n_sub, overlap, window="hann"):
        """Slow time at the effective centre of each Doppler look made by decompose_subapertures_w."""
        from sensitivity_sweep import WINDOWS
        band = n_cols / (n_sub - (n_sub - 1) * overlap)
        step = band * (1 - overlap)
        f = (np.arange(n_cols) - n_cols / 2) / n_cols                 # cycles/pixel, fftshifted order
        inband = np.abs(f) <= self.col_bw * self.css / 2
        ts, fs = [], []
        for k in range(n_sub):
            c = band / 2 + k * step
            lo, hi = max(0, int(round(c - band / 2))), min(n_cols, int(round(c + band / 2)))
            w = np.zeros(n_cols)
            w[lo:hi] = WINDOWS[window](hi - lo)
            w = (w ** 2) * inband
            fc = float((w * f).sum() / w.sum())
            kcol = -self.col_sgn * fc / self.css                       # cycles/m (SICD Sgn convention)
            theta = np.arctan(kcol / self.krow)
            roots = np.roots(self.pa[::-1] - np.r_[np.zeros(len(self.pa) - 1), theta])
            roots = roots[np.isreal(roots)].real
            t = roots[np.argmin(np.abs(roots - self.t_coa))]
            ts.append(float(t)); fs.append(fc)
        return np.array(ts), np.array(fs)


def selftest():
    """Flat-earth toy: radar flying +x at height Hs, looking toward +y. Slant plane through origin."""
    class P:
        def __call__(self, t): return np.array([7000.0 * t, -400e3, 500e3])
        def derivative_eval(self, t, der_order=1): return np.array([7000.0, 0.0, 0.0])
    g = Geom.__new__(Geom)
    g.scp = np.zeros(3); g.arp_poly = P(); g.t_coa = 0.0
    los = -np.array([0.0, -400e3, 500e3]); los /= np.linalg.norm(los)
    g.urow = los; g.ucol = np.array([1.0, 0, 0]); g.rss = g.css = 1.0; g.scp_pix = np.zeros(2)
    inc = np.degrees(np.arctan2(400e3, 500e3))
    ok = True
    # (1) a point in the slant plane maps to itself
    X = (37.0 * g.urow + 12.0 * g.ucol)[None]
    pix = g.project(X, 0.0)[0]
    ok &= np.allclose(pix, [37, 12], atol=1e-3); print("in-plane point ->", pix.round(4))
    # (2) raising a ground point by h shortens slant range by h*cos(inc)
    h = 100.0
    pix = g.project(np.array([[0, 0, h]]), 0.0)[0]
    ok &= abs(pix[0] + h * np.cos(np.radians(inc))) < 0.05 and abs(pix[1]) < 0.05
    print(f"h={h} at COA -> row {pix[0]:.3f} (expect {-h*np.cos(np.radians(inc)):.3f}), col {pix[1]:.4f}")
    # (3) straight-line flight: the R/Rdot circle is centred on the flight line, so its intersection with a
    #     slant plane containing that line does not move with t. Height gives NO inter-look drift here;
    #     any drift on real data comes only from orbit curvature (see docs/REVIEW_BIONDI2022_KHUFU, section 6).
    dt = 1.0
    c1 = g.project(np.array([[0, 0, h]]), dt / 2)[0][1] - g.project(np.array([[0, 0, h]]), -dt / 2)[0][1]
    print(f"col drift over {dt}s for straight flight: {c1:.6f} m (expect 0)")
    ok &= abs(c1) < 1e-3
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


def load(path):
    from sarpy.io.complex.converter import open_complex
    rd = open_complex(path)
    return rd, rd.sicd_meta, Geom(rd.sicd_meta)


def qa(path, out, offsets):
    """Amplitude + wireframe. Uses no displacement data."""
    from PIL import Image, ImageDraw
    from sarpy.geometry import point_projection
    rd, m, g = load(path)
    info = {}
    for name in PYRAMIDS:
        de, dn = offsets.get(name, (0.0, 0.0))
        X, h, _ = pyramid_points(name, 10.0, de, dn)
        mine = g.project(X, g.t_coa)
        theirs, _, _ = point_projection.ground_to_image(X, m)
        info[name + "_solver_vs_sarpy_px"] = float(np.abs(mine - theirs).max())
        lo = np.floor(mine.min(0)).astype(int) - 300
        hi = np.ceil(mine.max(0)).astype(int) + 300
        lo = np.maximum(lo, 0); hi = np.minimum(hi, rd.data_size)
        a = np.abs(np.asarray(rd[lo[0]:hi[0], lo[1]:hi[1]]))
        f = max(1, int(round((hi[1] - lo[1]) / 900)))
        fr = max(1, int(round(f * g.css / g.rss)))
        hh, ww = (a.shape[0] // fr) * fr, (a.shape[1] // f) * f
        a = np.sqrt((a[:hh, :ww] ** 2).reshape(hh // fr, fr, ww // f, f).mean((1, 3)))
        db = 20 * np.log10(a + 1e-6)
        l, u = np.percentile(db, [2, 99.7])
        im = Image.fromarray((np.clip((db - l) / (u - l), 0, 1) * 255).astype(np.uint8)).convert("RGB")
        dr = ImageDraw.Draw(im)
        for p, q in wireframe(name, de, dn):
            pq = g.project(np.array([p, q]), g.t_coa)
            dr.line([((pq[0, 1] - lo[1]) / f, (pq[0, 0] - lo[0]) / fr), ((pq[1, 1] - lo[1]) / f, (pq[1, 0] - lo[0]) / fr)],
                    fill=(255, 220, 0), width=2)
        fn = f"{out}_{name}.png"
        im.save(fn); info[name + "_png"] = fn
    print(json.dumps(info, indent=1))


def measure(path, out, offsets, n_sub=11, overlap=0.8, patch=64, min_pts=40):
    from sensitivity_sweep import decompose_subapertures_w, ESTIMATORS
    rd, m, g = load(path)
    res = dict(test="K", sicd=os.path.basename(path), n_sub=n_sub, overlap=overlap, patch=patch,
               offsets=offsets, prereg="docs/PREREGISTRATION_PARALLAX_2026-11-10.md", pyramids={})
    for name in PYRAMIDS:
        de, dn = offsets.get(name, (0.0, 0.0))
        X, h, face = pyramid_points(name, 3.0, de, dn)
        pc = g.project(X, g.t_coa)
        margin = 4 * patch
        lo = np.maximum(np.floor(pc.min(0)).astype(int) - margin, 0)
        hi = np.minimum(np.ceil(pc.max(0)).astype(int) + margin, rd.data_size)
        hi = lo + ((hi - lo) // patch) * patch
        slc = np.asarray(rd[lo[0]:hi[0], lo[1]:hi[1]])
        nR, nC = slc.shape
        ts, fs = g.look_times(nC, n_sub, overlap)
        # predicted per-step displacement of each model point (pixels), averaged over the n_sub-1 steps
        proj = np.stack([g.project(X, t) for t in ts])                 # (n_sub, N, 2)
        step = np.diff(proj, axis=0).mean(0)                            # (N, 2) row, col
        looks, _ = decompose_subapertures_w(slc, n_sub=n_sub, overlap=overlap, axis=1, window="hann")
        amp = np.abs(looks)
        rows = []
        for r in range(0, nR, patch):
            for c in range(0, nC, patch):
                inside = ((pc[:, 0] >= lo[0] + r) & (pc[:, 0] < lo[0] + r + patch) &
                          (pc[:, 1] >= lo[1] + c) & (pc[:, 1] < lo[1] + c + patch))
                npt = int(inside.sum())
                P = np.abs(slc[r:r + patch, c:c + patch]) ** 2
                rec = dict(r=int(lo[0] + r), c=int(lo[1] + c), n_model=npt,
                           pointiness=float(P.max() / (P.mean() + 1e-12)), mean_power=float(P.mean()))
                if npt >= min_pts:
                    rec.update(h=float(h[inside].mean()), pred_row=float(step[inside, 0].mean()),
                               pred_col=float(step[inside, 1].mean()),
                               face=int(np.bincount(face[inside], minlength=4).argmax()))
                for est in ("phasecorr", "ncc"):
                    d = np.array([ESTIMATORS[est](amp[k - 1, r:r + patch, c:c + patch],
                                                  amp[k, r:r + patch, c:c + patch], np.float64)
                                  for k in range(1, n_sub)])
                    rec[est + "_row"] = float(np.median(d[:, 0])); rec[est + "_col"] = float(np.median(d[:, 1]))
                    rec[est + "_col_mean"] = float(np.mean(d[:, 1]))
                rows.append(rec)
        res["pyramids"][name] = dict(crop=[int(lo[0]), int(hi[0]), int(lo[1]), int(hi[1])],
                                     look_times=ts.tolist(), look_f=fs.tolist(), patches=rows)
        print(name, "crop", lo, hi, "patches", len(rows), "on-pyramid", sum("h" in x for x in rows))
    json.dump(res, open(out, "w"))
    print("->", out)


def analyse(path_json, n_boot=2000, seed=0):
    d = json.load(open(path_json))
    rng = np.random.default_rng(seed)
    out = {}
    for name, P in d["pyramids"].items():
        on = [x for x in P["patches"] if "h" in x]
        off = [x for x in P["patches"] if x["n_model"] == 0]
        o = dict(n_on=len(on), n_off=len(off),
                 pred_col_per_100m=float(np.polyfit([x["h"] for x in on], [x["pred_col"] for x in on], 1)[0] * 100),
                 pred_col_range=[float(min(x["pred_col"] for x in on)), float(max(x["pred_col"] for x in on))])
        pred = np.array([x["pred_col"] for x in on])
        for est in ("phasecorr", "ncc"):
            y = np.array([x[est + "_col"] for x in on])
            gain = float(np.polyfit(pred, y, 1)[0]); r = float(np.corrcoef(pred, y)[0, 1])
            bs = []
            for _ in range(n_boot):
                i = rng.integers(0, len(on), len(on))
                bs.append(np.polyfit(pred[i], y[i], 1)[0])
            o[est] = dict(gain=gain, r=r, gain_ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                          off_median=float(np.median([x[est + "_col"] for x in off])),
                          off_iqr=float(np.subtract(*np.percentile([x[est + "_col"] for x in off], [75, 25]))))
            # secondary: top-quartile "pointiness" patches
            pt = np.array([x["pointiness"] for x in on]); sel = pt >= np.percentile(pt, 75)
            o[est]["gain_pointy"] = float(np.polyfit(pred[sel], y[sel], 1)[0])
            # sign-free check with the row axis as a nuisance comparison
            o[est]["r_row_vs_predrow"] = float(np.corrcoef([x["pred_row"] for x in on], [x[est + "_row"] for x in on])[0, 1])
        out[name] = o
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sicd"); ap.add_argument("--out")
    ap.add_argument("--qa", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyse"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--offsets", default="{}", help='JSON, e.g. {"khufu":[de,dn]} metres east/north')
    a = ap.parse_args()
    off = {k: tuple(v) for k, v in json.loads(a.offsets).items()}
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.qa: qa(a.sicd, a.out, off)
    if a.run: measure(a.sicd, a.out, off)
    if a.analyse: analyse(a.analyse)
