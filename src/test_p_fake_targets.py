"""Test P — fake-target / analyst-freedom test (pre-registration P, 12 Nov 2026).

Rules: docs/PREREGISTRATION_FAKE_TARGETS_2026-11-12.md (P.2-P.7 with the P.8 amendments A1-A7).
"S-like" = OUR reconstruction of M. Seyfzadeh's publicly described pipeline; it is not his code.

Modes
  --selftest                     synthetic speckle only (no SICD)
  --extract SICD OUT.npz [--corr R C]   crop the two lines (no statistic computed)
  --placement IN(.nitf|.npz)     amplitude-only PNG with the lines drawn
  --run IN(.nitf|.npz) LABEL     main run -> runs/test_p_<LABEL>.json (+ PNG)
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "..", "runs")

# ---- fixed by the pre-registration ----
CROP = 1024
K = 295
BSHIFT_FRAC = 0.0226
PATCH_RG, PATCH_AZ = 32, 24          # rows (range) x cols (azimuth)
RING = 48
W = 175
NPOS = 149
P_RUN = 8
GATE = 0.1
CYC50 = 12.0                         # cycles per window at 50 m when s = 1 (ours, arbitrary)
DZ = 0.5
NZ = 100
CSTEP = 0.03                         # frequency grid step, cycles per window
NFREQ = 800                          # up to 24 cycles per window
S_GRID = np.exp(np.linspace(np.log(0.5), np.log(2.0), 21))
SMOOTH = (1, 3, 5)
SHIFTS_M = (-4.0, -2.0, 0.0, 2.0, 4.0)
TOL_POS, TOL_Z = 10, 3.0
PCTL = 75.0                          # P.8 amendment A8 (was 90; set on synthetic selftest only)
ZMIN_ROW = 8                         # threshold from rows deeper than 4 m (A8)
OSIRIS = (29.975406, 31.135597)      # de.wikipedia "Osiris-Grab"
HEADING = 102.45
SHAFT_POS = 120
DESERT_C = (29.9625, 31.1235)        # centre of region P2 (test G)
CTRL_POS = 60
REAL_DEPTHS = (10.0, 22.0, 33.0)
ALT_DEPTHS = (10.0, 24.0, 33.0)
FLANKS = np.array([[0, RING], [34, 34], [-34, 34], [0, -RING], [34, -34], [-34, -34]])


# ---------------- geometry ----------------
def line_latlon(anchor, anchor_pos, shift_m):
    lat0, lon0 = anchor
    h = np.deg2rad(HEADING)
    d = np.arange(NPOS) - anchor_pos
    north = d * np.cos(h) + shift_m * np.cos(h - np.pi / 2)
    east = d * np.sin(h) + shift_m * np.sin(h - np.pi / 2)
    lat = lat0 + north / 110860.0
    lon = lon0 + east / (111320.0 * np.cos(np.deg2rad(lat0)))
    return lat, lon


def lines_pixels(sicd, anchor, anchor_pos, corr=(0, 0)):
    from sarpy.geometry.point_projection import ground_to_image_geo
    hae = sicd.GeoData.SCP.LLH.HAE
    out = []
    for sh in SHIFTS_M:
        lat, lon = line_latlon(anchor, anchor_pos, sh)
        ip = np.asarray(ground_to_image_geo(np.c_[lat, lon, np.full(NPOS, hae)], sicd)[0]).reshape(-1, 2)
        out.append(ip + np.array(corr))
    return np.array(out)                                   # (5, 149, 2) full-image row, col


def extract(path, corr=(0, 0)):
    from sarpy.io.complex.converter import open_complex
    rd = open_complex(path)
    s = rd.sicd_meta
    R, C = s.ImageData.NumRows, s.ImageData.NumCols
    out = dict(row_ss=float(s.Grid.Row.SS), col_ss=float(s.Grid.Col.SS))
    for name, anchor, apos in (("osiris", OSIRIS, SHAFT_POS), ("desert", DESERT_C, NPOS // 2)):
        px = lines_pixels(s, anchor, apos, corr)
        ctr = px[2].mean(axis=0)
        r0 = int(np.clip(round(ctr[0]) - CROP // 2, 0, R - CROP))
        c0 = int(np.clip(round(ctr[1]) - CROP // 2, 0, C - CROP))
        out["crop_" + name] = np.asarray(rd[r0:r0 + CROP, c0:c0 + CROP], dtype=np.complex64)
        out["px_" + name] = (px - np.array([r0, c0])).astype(np.float32)
    return out


def load(path, corr=(0, 0)):
    if path.endswith(".npz"):
        z = np.load(path)
        return {k: z[k] for k in z.files}
    return extract(path, corr)


# ---------------- A1: Reference / Offset pairs ----------------
def spectrum_support(img):
    F = np.fft.fft(img, axis=1)
    prof = uniform_filter(np.mean(np.abs(F) ** 2, axis=0), 15, mode="wrap")
    N = prof.size
    ang = 2 * np.pi * np.arange(N) / N
    centre = int(round((np.angle(np.sum(prof * np.exp(1j * ang))) % (2 * np.pi)) / (2 * np.pi) * N))
    roll = N // 2 - centre
    F = np.roll(F, roll, axis=1)
    prof = np.roll(prof, roll)
    on = np.where(prof > 0.1 * np.median(prof[prof > np.median(prof)]))[0]
    return F, int(on.min()), int(on.max()) + 1


def pair_windows(lo, hi):
    ns = hi - lo
    band = ns // 2
    b = max(1, int(round(BSHIFT_FRAC * ns)))
    step = (ns - band - b) / (K - 1)
    return band, b, step


def make_pair(F, lo, hi, k):
    band, b, step = pair_windows(lo, hi)
    s0 = lo + int(round(k * step))
    win = np.hanning(band).astype(np.float32)
    out = []
    for st in (s0, s0 + b):
        w = np.zeros(F.shape[1], np.float32)
        w[st:st + band] = win
        out.append(np.fft.ifft(F * w, axis=1).astype(np.complex64))
    return out[0], out[1]


# ---------------- A2/A3: displacement ----------------
def grab(img, centres):
    r = np.round(centres[:, 0]).astype(int)[:, None, None] + (np.arange(PATCH_RG) - PATCH_RG // 2)[None, :, None]
    c = np.round(centres[:, 1]).astype(int)[:, None, None] + (np.arange(PATCH_AZ) - PATCH_AZ // 2)[None, None, :]
    return img[r, c]


def _parab(m1, c0, p1):
    den = m1 - 2 * c0 + p1
    return np.where(np.abs(den) > 1e-12, 0.5 * (m1 - p1) / np.where(den == 0, 1, den), 0.0)


def shifts(ref, off, centres):
    """Shift (rows, cols) of `off` relative to `ref` for each patch centre."""
    A = np.fft.fft2(grab(ref, centres))
    B = np.fft.fft2(grab(off, centres))
    C = np.abs(np.fft.ifft2(B * np.conj(A)))
    M = C.shape[0]
    Cs = np.fft.fftshift(C, axes=(1, 2))
    r0, c0 = PATCH_RG // 2, PATCH_AZ // 2
    sub = Cs[:, r0 - 4:r0 + 5, c0 - 4:c0 + 5]                # |shift| <= 4 px
    idx = sub.reshape(M, -1).argmax(axis=1)
    pr, pc = idx // 9 + r0 - 4, idx % 9 + c0 - 4
    m = np.arange(M)
    dr = _parab(Cs[m, pr - 1, pc], Cs[m, pr, pc], Cs[m, pr + 1, pc])
    dc = _parab(Cs[m, pr, pc - 1], Cs[m, pr, pc], Cs[m, pr, pc + 1])
    return np.c_[pr - r0 + dr, pc - c0 + dc]


def fourier_shift(tile, dr, dc):
    fr = np.fft.fftfreq(tile.shape[0])[:, None]
    fc = np.fft.fftfreq(tile.shape[1])[None, :]
    return np.fft.ifft2(np.fft.fft2(tile) * np.exp(-2j * np.pi * (fr * dr + fc * dc))).astype(tile.dtype)


def plant_q(k):
    th = [2 * np.pi * (d * CYC50 / 50.0) * k / W for d in REAL_DEPTHS]
    return 0.25 * sum(np.sin(t) for t in th), 0.5 * sum(np.cos(t) for t in th)     # rows (rg), cols (az)


def displacement(img, px, row_ss, col_ss, plant_at=None):
    """Return q[line, pos, k, 2] in metres (range, azimuth), common mode removed."""
    F, lo, hi = spectrum_support(img)
    tg = px.reshape(-1, 2)
    allc = np.concatenate([tg] + [tg + f for f in FLANKS])
    T = tg.shape[0]
    q = np.zeros((T, K, 2), np.float32)
    for k in range(K):
        ref, off = make_pair(F, lo, hi, k)
        if plant_at is not None:
            r, c = int(round(plant_at[0])), int(round(plant_at[1]))
            dr, dc = plant_q(k)
            off[r - 32:r + 32, c - 32:c + 32] = fourier_shift(off[r - 32:r + 32, c - 32:c + 32], dr, dc)
        sh = shifts(ref, off, allc).reshape(7, T, 2)
        common = 0.5 * (np.median(sh[1:4], axis=0) + np.median(sh[4:7], axis=0))
        q[:, k, :] = sh[0] - common
    q[..., 0] *= row_ss
    q[..., 1] *= col_ss
    return q.reshape(px.shape[0], px.shape[1], K, 2)


# ---------------- A5/A6: windowed elliptical fit ----------------
def score_map(q):
    """q[pos, K, 2] -> S[pos, NFREQ]: best gated adjusted R^2 over all W-windows."""
    T = q.shape[0]
    n = np.arange(K)
    nw = K - W + 1

    def wsum(x):                                             # sliding window sum along last axis
        cs = np.concatenate([np.zeros(x.shape[:-1] + (1,), x.dtype), np.cumsum(x, axis=-1)], axis=-1)
        return cs[..., W:] - cs[..., :-W]

    q64 = q.astype(np.float64).transpose(0, 2, 1)            # (T, 2, K)
    S0 = wsum(q64)                                           # (T, 2, nw)
    SST = (wsum(q64 ** 2) - S0 ** 2 / W).sum(axis=1)         # (T, nw)
    out = np.zeros((T, NFREQ), np.float32)
    for j in range(NFREQ):
        th = 2 * np.pi * (CSTEP * (j + 1)) * n / W
        co, si = np.cos(th), np.sin(th)
        G = np.empty((nw, 3, 3))
        G[:, 0, 0] = W
        G[:, 0, 1] = G[:, 1, 0] = wsum(co)
        G[:, 0, 2] = G[:, 2, 0] = wsum(si)
        G[:, 1, 1] = wsum(co * co)
        G[:, 2, 2] = wsum(si * si)
        G[:, 1, 2] = G[:, 2, 1] = wsum(co * si)
        Gi = np.linalg.pinv(G, rcond=1e-9)
        b = np.stack([S0, wsum(q64 * co), wsum(q64 * si)], axis=-1)      # (T, 2, nw, 3)
        beta = np.einsum("wij,tcwj->tcwi", Gi, b)
        ssfit = (b * beta).sum(axis=-1).sum(axis=1) - (S0 ** 2 / W).sum(axis=1)
        r2 = np.where(SST > 0, ssfit / np.where(SST > 0, SST, 1), 0.0)
        adj = 1 - (1 - r2) * (2 * W - 1) / (2 * W - 6)
        u, v = beta[..., 1], beta[..., 2]                    # (T, 2, nw)
        fro = (u ** 2 + v ** 2).sum(axis=1)
        det = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
        disc = np.sqrt(np.clip(fro ** 2 - 4 * det ** 2, 0, None))
        ratio = np.sqrt(np.clip(fro - disc, 0, None) / np.where(fro + disc > 0, fro + disc, 1))
        adj = np.where(ratio > GATE, adj, 0.0)
        out[:, j] = np.clip(adj.max(axis=1), 0, None)
    return out


# ---------------- A7 + knobs + hit rule ----------------
def run_filter(img):
    pos = img > 0
    keep = np.zeros_like(pos)
    for z in range(img.shape[1]):
        col = pos[:, z]
        i = 0
        while i < col.size:
            if col[i]:
                j = i
                while j < col.size and col[j]:
                    j += 1
                if j - i >= P_RUN:
                    keep[i:j, z] = True
                i = j
            else:
                i += 1
    return np.where(keep, img, 0.0)


def image_for(S, s, smooth):
    z = DZ * (np.arange(NZ) + 1)
    idx = np.round(s * z * CYC50 / 50.0 / CSTEP).astype(int) - 1
    img = run_filter(S[:, np.clip(idx, 0, NFREQ - 1)])
    if smooth > 1:
        img = uniform_filter(img, size=smooth, mode="constant")
    return img


def hits(img, thr, pos, depths):
    h = 0
    for d in depths:
        z0 = max(0, int(np.floor((d - TOL_Z) / DZ)) - 1)
        z1 = min(NZ, int(np.ceil((d + TOL_Z) / DZ)))
        p0, p1 = max(0, pos - TOL_POS), min(NPOS, pos + TOL_POS + 1)
        h += bool(np.any(img[p0:p1, z0:z1] >= thr))
    return h


def evaluate(Slines, targets):
    """Slines[5, pos, NFREQ]; targets = list of (pos, depths). Returns F, T per target, mean busyness."""
    n3 = np.zeros(len(targets))
    busy = []
    ncfg = 0
    for li in range(len(SHIFTS_M)):
        for s in S_GRID:
            for sm in SMOOTH:
                img = image_for(Slines[li], s, sm)
                sub = img[:, ZMIN_ROW:]
                nz = sub[sub > 0]
                ncfg += 1
                if nz.size == 0:
                    busy.append(0.0)
                    continue
                thr = np.percentile(nz, PCTL)
                busy.append(float(np.mean(sub >= thr)))
                for i, (p, d) in enumerate(targets):
                    n3[i] += hits(img, thr, p, d) == 3
    F = n3 / ncfg
    return F, (n3 > 0).astype(int), float(np.mean(busy))


def pval(F_real, F_fake):
    return float((1 + np.sum(F_fake >= F_real)) / (F_fake.size + 1))


def fake_targets():
    d = json.load(open(os.path.join(RUNS, "test_p_fake_targets.json")))
    return [(t["position"], tuple(t["depths_m"])) for t in d["fake_targets"]]


def noise_like(img, rng):
    az = np.sqrt(np.mean(np.abs(np.fft.fft(img, axis=1)) ** 2, axis=0))
    rg = np.sqrt(np.mean(np.abs(np.fft.fft(img, axis=0)) ** 2, axis=1))
    w = (rng.standard_normal(img.shape) + 1j * rng.standard_normal(img.shape))
    return np.fft.ifft2(np.fft.fft2(w) * rg[:, None] * az[None, :]).astype(np.complex64)


def analyse(d, label, make_png=True):
    rs, cs = float(d["row_ss"]), float(d["col_ss"])
    fakes = fake_targets()
    rng = np.random.default_rng(0)
    fam = {}
    q = displacement(d["crop_osiris"], d["px_osiris"], rs, cs)
    fam["osiris"] = np.array([score_map(q[i]) for i in range(q.shape[0])])
    q = displacement(d["crop_desert"], d["px_desert"], rs, cs)
    fam["desert"] = np.array([score_map(q[i]) for i in range(q.shape[0])])
    q = displacement(d["crop_desert"].copy(), d["px_desert"], rs, cs, plant_at=d["px_desert"][2, CTRL_POS])
    fam["desert_planted"] = np.array([score_map(q[i]) for i in range(q.shape[0])])
    q = displacement(noise_like(d["crop_osiris"], rng), d["px_osiris"], rs, cs)
    fam["noise"] = np.array([score_map(q[i]) for i in range(q.shape[0])])

    n1 = [t for t in fakes if abs(t[0] - SHAFT_POS) > 15]
    F_os, T_os, busy_os = evaluate(fam["osiris"], [(SHAFT_POS, REAL_DEPTHS), (SHAFT_POS, ALT_DEPTHS)] + n1)
    F_de, T_de, busy_de = evaluate(fam["desert"], fakes)
    F_pl, T_pl, busy_pl = evaluate(fam["desert_planted"], [(CTRL_POS, REAL_DEPTHS)])
    F_no, T_no, busy_no = evaluate(fam["noise"], fakes)
    res = dict(label=label, n_configs=len(SHIFTS_M) * len(S_GRID) * len(SMOOTH),
               F_real=float(F_os[0]), T_real=int(T_os[0]), F_real_alt_10_24_33=float(F_os[1]),
               p_N1=pval(F_os[0], F_os[2:]), p_N2=pval(F_os[0], F_de),
               p_N1_alt=pval(F_os[1], F_os[2:]), p_N2_alt=pval(F_os[1], F_de),
               share_fakes_T1=dict(N1=float(T_os[2:].mean()), N2=float(T_de.mean()), N3=float(T_no.mean())),
               median_F_fakes=dict(N1=float(np.median(F_os[2:])), N2=float(np.median(F_de)), N3=float(np.median(F_no))),
               busyness=dict(osiris=busy_os, desert=busy_de, planted=busy_pl, noise=busy_no),
               control=dict(F=float(F_pl[0]), p_N2=pval(F_pl[0], F_de)), n_fakes=dict(N1=len(n1), N2=len(fakes)))
    c_ok = res["control"]["p_N2"] <= 0.05
    if not c_ok:
        v = "INCONCLUSIVE (control failed)"
    elif res["p_N1"] <= 0.05 and res["p_N2"] <= 0.05:
        v = "STANDS OUT"
    elif res["p_N1"] > 0.20 and res["p_N2"] > 0.20:
        v = "NOT DISTINGUISHED"
    else:
        v = "MIXED"
    res["verdict"] = v
    json.dump(res, open(os.path.join(RUNS, f"test_p_{label}.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(RUNS, f"test_p_{label}_scores.npz"), **fam)
    if make_png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(4, 1, figsize=(11, 13))
        for a, (name, title) in zip(ax, (("osiris", "Osiris-shaft line (real shaft at position 120)"),
                                         ("desert", "Bare desert line"),
                                         ("desert_planted", "Bare desert + planted signal at position 60"),
                                         ("noise", "Pure noise (no radar scene)"))):
            img = image_for(fam[name][2], 1.0, 1)
            a.imshow(img.T, aspect="auto", cmap="magma", extent=[0, NPOS, 50, 0])
            a.set_title(f"{label}: {title}  [S-like, s=1, no smoothing, no line shift]")
            a.set_ylabel("nominal depth (m)")
        ax[0].plot([SHAFT_POS] * 3, REAL_DEPTHS, "c+", ms=12)
        ax[2].plot([CTRL_POS] * 3, REAL_DEPTHS, "c+", ms=12)
        ax[-1].set_xlabel("line position (about 1 m spacing)")
        fig.tight_layout()
        fig.savefig(os.path.join(RUNS, f"test_p_{label}.png"), dpi=110)
    return res


def placement(d, label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))
    for a, name in zip(ax, ("osiris", "desert")):
        amp = np.abs(d["crop_" + name])
        a.imshow(amp, cmap="gray", vmax=np.percentile(amp, 98))
        px = d["px_" + name][2]
        a.plot(px[:, 1], px[:, 0], "y-", lw=1)
        a.plot(px[SHAFT_POS, 1], px[SHAFT_POS, 0], "r+", ms=14)
        a.set_title(f"{label} {name} line (amplitude only)")
    fig.tight_layout()
    fig.savefig(os.path.join(RUNS, f"test_p_placement_{label}.png"), dpi=110)


def selftest():
    rng = np.random.default_rng(1)
    w = rng.standard_normal((CROP, CROP)) + 1j * rng.standard_normal((CROP, CROP))
    F = np.fft.fft(w, axis=1)
    m = np.zeros(CROP)
    m[100:900] = 1
    img = np.fft.ifft(F * m, axis=1).astype(np.complex64)
    px = np.array([[[512 + 0.0 * i + 3 * j, 300 + 2.0 * i] for i in range(NPOS)] for j in range(5)], np.float32)
    d = dict(row_ss=0.5, col_ss=0.8, crop_osiris=img, crop_desert=img.copy(), px_osiris=px, px_desert=px)
    res = analyse(d, "selftest", make_png=True)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    corr = (0, 0)
    if "--corr" in a:
        i = a.index("--corr")
        corr = (float(a[i + 1]), float(a[i + 2]))
        a = a[:i] + a[i + 3:]
    if a[0] == "--selftest":
        selftest()
    elif a[0] == "--extract":
        np.savez(a[2], **extract(a[1], corr))
        print("wrote", a[2])
    elif a[0] == "--placement":
        placement(load(a[1], corr), a[2] if len(a) > 2 else "scene")
    elif a[0] == "--run":
        print(json.dumps(analyse(load(a[1], corr), a[2]), indent=1))
