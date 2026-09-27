#!/usr/bin/env python3
"""
figure_information.py — pre-registered C.4 step 2 (docs/PREREGISTRATION_FIGURES_2026-09-27.md).

How much independent spatial information does each panel of the 2022 paper's paired figures carry —
(a) "3D model of Khnum-Khufu" vs (b) "Tomographic reconstruction (magnitude)" — and does (a) hold
detail finer than anything (b) carries?

Statistics (fixed in the pre-registration, D.4):
  S1 effective resolution r = 1/f_c, f_c = highest radial frequency where the radially averaged power
     spectrum exceeds 2x its floor (floor = median over the top 10% of radial frequencies).
  S2 independent samples N = area / r^2.
  S3 fine-detail fraction: share of a panel's spectral energy above panel (b)'s cutoff f_c(b).

numpy + Pillow + pypdf only (no scipy), so it runs anywhere.

  python3 src/figure_information.py --controls
  python3 src/figure_information.py --extract data/biondi2022/<paper>.pdf   # dump embedded images
  python3 src/figure_information.py --measure reference/figure_layout.json  # score the pairs
"""
import argparse, hashlib, json, os, sys
import numpy as np

FLOOR_TOP, FLOOR_MULT = 0.10, 2.0


# --------------------------------------------------------------------------- statistics
def luminance(rgb):
    a = np.asarray(rgb, dtype=float)
    if a.ndim == 2:
        return a
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def _spectrum(img):
    g = np.asarray(img, float)
    g = g - g.mean()
    H, W = g.shape
    g = g * np.outer(np.hanning(H), np.hanning(W))
    P = np.abs(np.fft.fft2(g)) ** 2
    fy = np.fft.fftfreq(H)[:, None]
    fx = np.fft.fftfreq(W)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    return P, f


def radial_profile(img):
    P, f = _spectrum(img)
    H, W = img.shape
    df = 1.0 / max(H, W)
    edges = np.arange(df, 0.5 + df, df)           # exclude DC bin; stop at Nyquist
    centres, prof = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (f >= lo) & (f < hi)
        if m.any():
            centres.append(0.5 * (lo + hi)); prof.append(P[m].mean())
    return np.array(centres), np.array(prof), P, f


def s1_s2_v1_withdrawn(img):
    """S1 v1 (floor-relative cutoff). WITHDRAWN 27 Sep 2026 before any figure was measured: on its
    own positive control it ranked a Gaussian-blurred image as HIGHER resolution than the sharp
    original (it assumes a noise floor; a blurred spectrum has none, or only quantization). Kept
    for the record; not used. See PREREGISTRATION_FIGURES_2026-09-27.md D.4a."""
    fr, pr, _, _ = radial_profile(img)
    ntop = max(1, int(round(FLOOR_TOP * len(pr))))
    floor = float(np.median(pr[-ntop:]))
    above = np.where(pr > FLOOR_MULT * floor)[0]
    fc = float(fr[above[-1]]) if len(above) else float(fr[0])
    r = 1.0 / fc
    return dict(f_c=fc, r_px=r, N=float(img.shape[0] * img.shape[1] / r ** 2), floor=floor)


ENERGY_Q = 0.95


def energy_cutoff(img, q=ENERGY_Q):
    """Radial frequency below which a fraction q of the image's non-DC spectral energy lies."""
    P, f = _spectrum(img)
    m = f > 0
    ff, pp = f[m], P[m]
    o = np.argsort(ff)
    c = np.cumsum(pp[o]); c /= c[-1]
    return float(ff[o][min(np.searchsorted(c, q), len(c) - 1)])


def s1_s2(img):
    """S1 v2: effective resolution r = 1/f_E, f_E = 95%-energy radial frequency.
       S2: independent samples N = area / r^2."""
    fc = energy_cutoff(img)
    r = 1.0 / fc
    return dict(f_c=fc, r_px=r, N=float(img.shape[0] * img.shape[1] / r ** 2))


def fine_fraction(img, fc):
    P, f = _spectrum(img)
    tot = P[f > 0].sum()
    return float(P[f > fc].sum() / (tot + 1e-30))


def score_pair(a, b):
    sa, sb = s1_s2(a), s1_s2(b)
    Ea, Eb = fine_fraction(a, sb["f_c"]), fine_fraction(b, sb["f_c"])
    return dict(a=sa, b=sb, N_ratio=sa["N"] / (sb["N"] + 1e-30),
                E_a=Ea, E_b=Eb, E_ratio=Ea / (Eb + 1e-30),
                P1_hit=bool(sa["N"] > sb["N"]), P2_hit=bool(Ea >= 5 * Eb))


# --------------------------------------------------------------------------- controls
def _blur(img, sigma):
    H, W = img.shape
    fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.fftfreq(W)[None, :]
    G = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * G))


def _polygon_render(n=400, seed=5):
    """A sharp-edged, flat-shaded, CAD-like render: overlapping polygons on a background."""
    from matplotlib.path import Path
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n]
    pts = np.c_[xx.ravel(), yy.ravel()]
    img = np.full((n, n), 40.0)
    for _ in range(14):
        c = rng.uniform(60, n - 60, 2); k = rng.integers(3, 7)
        ang = np.sort(rng.uniform(0, 2 * np.pi, k)); rad = rng.uniform(20, 80, k)
        poly = np.c_[c[0] + rad * np.cos(ang), c[1] + rad * np.sin(ang)]
        m = Path(poly).contains_points(pts).reshape(n, n)
        img[m] = rng.uniform(80, 240)
    return img


def q8(x):
    """Quantize to 8 bits, as every published figure is stored."""
    x = (x - x.min()) / (x.max() - x.min() + 1e-30)
    return np.round(x * 255)


def controls():
    sharp = _polygon_render()
    blurred = _blur(sharp, 4.0)
    pos = score_pair(q8(sharp), q8(blurred))
    rng = np.random.default_rng(9)
    n1 = _blur(rng.normal(size=(400, 400)), 4.0)
    n2 = _blur(rng.normal(size=(400, 400)), 4.0)
    nul = score_pair(q8(n1), q8(n2))
    ladder = {}
    for sig in (1, 2, 4, 8):
        ladder[sig] = [score_pair(q8(_polygon_render(seed=s)),
                                  q8(_blur(_polygon_render(seed=s), sig)))["N_ratio"]
                       for s in range(5)]
    mono = all(min(ladder[b]) > max(ladder[a]) for a, b in [(1, 2), (2, 4), (4, 8)])
    print("[ladder]   N(sharp)/N(blurred) by blur sigma: " +
          "; ".join(f"s{k}: {min(v):.1f}-{max(v):.1f}" for k, v in ladder.items()) +
          f"  -> {'monotonic' if mono else 'NOT monotonic'}")
    s2_ok = (pos["N_ratio"] > 1 and mono) and (0.5 <= nul["N_ratio"] <= 2.0)
    s3_ok = pos["E_ratio"] >= 5 and nul["E_ratio"] < 5
    print(f"[S2 positive] sharp vs blurred (sigma 4): N {pos['a']['N']:.0f} vs {pos['b']['N']:.0f} "
          f"(x{pos['N_ratio']:.1f}); [S2 null] x{nul['N_ratio']:.2f}  -> S2 {'PASS' if s2_ok else 'FAIL'}")
    print(f"[S3 positive] fine-detail E_a/E_b = {pos['E_a']:.3f}/{pos['E_b']:.3f} (x{pos['E_ratio']:.1f}, "
          f"bar 5x); [S3 null] x{nul['E_ratio']:.2f}  -> S3 {'PASS' if s3_ok else 'FAIL: not used (D.5)'}")
    out = dict(statistic="S1 v2: 95%-energy radial cutoff", positive=pos, null=nul,
               ladder={str(k): v for k, v in ladder.items()}, ladder_monotonic=mono,
               S2_pass=s2_ok, S3_pass=s3_ok)
    os.makedirs("runs", exist_ok=True)
    json.dump(out, open("runs/figure_information_controls.json", "w"), indent=1)
    print("-> runs/figure_information_controls.json")
    return s2_ok


# --------------------------------------------------------------------------- extraction
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(pdf, outdir):
    """Dump every embedded raster image at native resolution, with page numbers."""
    from pypdf import PdfReader
    os.makedirs(outdir, exist_ok=True)
    r = PdfReader(pdf)
    rows = []
    for pi, page in enumerate(r.pages, 1):
        text = page.extract_text() or ""
        for k, im in enumerate(page.images):
            name = f"p{pi:03d}_{k:02d}_{im.name}".replace("/", "_")
            fn = os.path.join(outdir, name)
            with open(fn, "wb") as f:
                f.write(im.data)
            rows.append(dict(page=pi, file=fn, bytes=len(im.data)))
        caps = [ln for ln in text.splitlines() if "Figure" in ln and "3D model" in ln]
        if caps:
            rows.append(dict(page=pi, caption_lines=caps))
    json.dump(dict(pdf=pdf, sha256=sha256(pdf), pages=len(r.pages), items=rows),
              open(os.path.join(outdir, "_index.json"), "w"), indent=1)
    print(f"{sum(1 for x in rows if 'file' in x)} images from {len(r.pages)} pages -> {outdir}/_index.json")


# --------------------------------------------------------------------------- measurement
def load_panel(fn, box):
    from PIL import Image
    im = Image.open(fn).convert("RGB")
    a = np.asarray(im)
    if box:
        x0, y0, x1, y1 = box
        a = a[y0:y1, x0:x1]
    return luminance(a)


def measure(layout_path):
    L = json.load(open(layout_path))
    res = dict(layout=layout_path, pdf=L.get("pdf"), pdf_sha256=L.get("pdf_sha256"),
               crop_rule=L.get("crop_rule"), pairs={})
    for fig in L["pairs"]:
        a = load_panel(fig["a"]["file"], fig["a"].get("box"))
        b = load_panel(fig["b"]["file"], fig["b"].get("box"))
        s = score_pair(a, b)
        s.update(desc=fig.get("desc", {}), shape_a=list(a.shape), shape_b=list(b.shape))
        if fig.get("b_m_per_px"):
            s["r_b_m"] = s["b"]["r_px"] * fig["b_m_per_px"]
            s["P3_hit"] = bool(s["r_b_m"] > 3.71)
        res["pairs"][fig["id"]] = s
        print(f"{fig['id']:<10} N(a) {s['a']['N']:>8.0f}  N(b) {s['b']['N']:>7.0f}  "
              f"E_a {s['E_a']:.3f}  E_b {s['E_b']:.3f}  (x{s['E_ratio']:.1f})  "
              f"P1 {'hit' if s['P1_hit'] else 'miss'}  P2 {'hit' if s['P2_hit'] else 'miss'}")
    n = len(res["pairs"])
    p1 = sum(v["P1_hit"] for v in res["pairs"].values())
    p2 = sum(v["P2_hit"] for v in res["pairs"].values())
    res["summary"] = dict(n_pairs=n, P1_hits=p1, P2_hits=p2,
                          P1_majority=p1 > n / 2, P2_majority=p2 > n / 2)
    res["summary"]["P2_status"] = "NOT USED: S3 failed its positive control (D.4a); descriptive only"
    med = float(np.median([v["N_ratio"] for v in res["pairs"].values()])) if n else float("nan")
    res["summary"].update(median_N_ratio=med, P1b_hit=bool(med >= 4))
    print(f"P1b median N(a)/N(b) = {med:.2f} (bar >= 4)  -> {'hit' if med >= 4 else 'miss'}")
    print(f"\nP1 (N(a) > N(b)) in {p1}/{n} pairs  [primary]")
    print(f"P2 not used (S3 failed its control); E_a >= 5 E_b in {p2}/{n} pairs, descriptive only")
    json.dump(res, open("runs/figure_information.json", "w"), indent=1)
    print("-> runs/figure_information.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--extract")
    ap.add_argument("--out", default="data/biondi2022/images")
    ap.add_argument("--measure")
    a = ap.parse_args()
    if a.controls:
        sys.exit(0 if controls() else 1)
    elif a.extract:
        extract(a.extract, a.out)
    elif a.measure:
        measure(a.measure)
    else:
        ap.print_help()
