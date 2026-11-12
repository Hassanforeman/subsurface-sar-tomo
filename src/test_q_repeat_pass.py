"""Test Q — repeat-pass consistency (pre-registration Q, 12 Nov 2026). See
docs/PREREGISTRATION_REPEAT_PASS_2026-11-12.md.  S-like pipeline = Test P (our reconstruction).

  --extract SICD OUT.npz [--corr R C]   crops for the 16 lines (geometry + no-data flag only)
  --run LABEL=FILE.npz LABEL=FILE.npz LABEL=FILE.npz
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T

GRID_C = (29.9760, 31.1312)
SPACING = 200.0
NL = 16


def centres():
    out = []
    for i in range(4):
        for j in range(4):
            north, east = (i - 1.5) * SPACING, (j - 1.5) * SPACING
            out.append((GRID_C[0] + north / 110860.0, GRID_C[1] + east / (111320.0 * np.cos(np.deg2rad(GRID_C[0])))))
    return out


def extract(path, corr=(0, 0)):
    from sarpy.io.complex.converter import open_complex
    from sarpy.geometry.point_projection import ground_to_image_geo
    rd = open_complex(path)
    s = rd.sicd_meta
    R, C = s.ImageData.NumRows, s.ImageData.NumCols
    hae = s.GeoData.SCP.LLH.HAE
    crops = np.zeros((NL, T.CROP, T.CROP), np.complex64)
    px = np.zeros((NL, T.NPOS, 2), np.float32)
    ok = np.zeros(NL, bool)
    for k, c in enumerate(centres()):
        lat, lon = T.line_latlon(c, T.NPOS // 2, 0.0)
        ip = np.asarray(ground_to_image_geo(np.c_[lat, lon, np.full(T.NPOS, hae)], s)[0]).reshape(-1, 2) + np.array(corr)
        if ip[:, 0].min() < 90 or ip[:, 1].min() < 90 or ip[:, 0].max() > R - 90 or ip[:, 1].max() > C - 90:
            continue
        ctr = ip.mean(axis=0)
        r0 = int(np.clip(round(ctr[0]) - T.CROP // 2, 0, R - T.CROP))
        c0 = int(np.clip(round(ctr[1]) - T.CROP // 2, 0, C - T.CROP))
        img = np.asarray(rd[r0:r0 + T.CROP, c0:c0 + T.CROP], dtype=np.complex64)
        p = ip - np.array([r0, c0])
        amp = np.abs(img)
        near = amp[int(p[:, 0].min()) - 64:int(p[:, 0].max()) + 64, int(p[:, 1].min()) - 64:int(p[:, 1].max()) + 64]
        if near.size == 0 or np.mean(near == 0) > 0.01 or near.mean() < 0.01 * np.median(amp[amp > 0]):
            continue
        crops[k], px[k], ok[k] = img, p, True
    return dict(crops=crops, px=px, ok=ok, row_ss=float(s.Grid.Row.SS), col_ss=float(s.Grid.Col.SS))


def hp(q, n=15):
    from scipy.ndimage import uniform_filter1d
    q = q.astype(np.float64)
    return q - uniform_filter1d(q, n, axis=1, mode="nearest")


def images(q):
    """q[pos, K, 2] -> (primary, secondary) images, depth-row means removed, 3-px smoothed."""
    S1 = T.score_map(q)
    prim = T.image_for(S1, 1.0, 1)[:, T.ZMIN_ROW:]
    S2 = T.score_map(hp(q[None] if q.ndim == 2 else q))
    z = T.DZ * (np.arange(T.NZ) + 1)
    idx = np.clip(np.round((3.0 + 1.24 * z * T.CYC50 / 50.0) / T.CSTEP).astype(int) - 1, 0, T.NFREQ - 1)
    sec = S2[:, idx].copy()
    sec[sec < 0.02] = 0
    old = T.P_RUN; T.P_RUN = 3; sec = T.run_filter(sec); T.P_RUN = old
    sec = uniform_filter(sec, size=(3, 1), mode="constant")
    out = []
    for im in (prim, sec):
        im = uniform_filter(im, 3)
        out.append(im - im.mean(axis=0, keepdims=True))
    return out


def corr(a, b):
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])


def process(path, label):
    cache = os.path.join(T.RUNS, f"test_q_{label}_images.npz")
    if os.path.exists(cache):
        z = np.load(cache)
        return {k: z[k] for k in z.files}
    d = np.load(path)
    rs, cs = float(d["row_ss"]), float(d["col_ss"])
    out = dict(ok=d["ok"])
    prim, sec = np.zeros((NL, T.NPOS, T.NZ - T.ZMIN_ROW)), np.zeros((NL, T.NPOS, T.NZ))
    for k in range(NL):
        if not d["ok"][k]:
            continue
        q = T.displacement(d["crops"][k], d["px"][k][None], rs, cs)[0]
        prim[k], sec[k] = images(q)
        if k == int(np.argmax(d["ok"])):                      # control on the first usable line
            qc = T.displacement(d["crops"][k].copy(), d["px"][k][None], rs, cs, plant_at=d["px"][k][T.CTRL_POS])[0]
            out["ctrl_prim"], out["ctrl_sec"] = images(qc)
        print(label, "line", k, "done", flush=True)
    out["prim"], out["sec"] = prim, sec
    np.savez_compressed(cache, **out)
    return out


def run(pairs):
    data = {lab: process(path, lab) for lab, path in pairs}
    labs = [l for l, _ in pairs]
    ok = np.all([data[l]["ok"] for l in labs], axis=0)
    idx = np.where(ok)[0]
    res = dict(lines_used=idx.tolist(), n_lines=int(idx.size), pairs={})
    rng = np.random.default_rng(0)
    for kind in ("prim", "sec"):
        for a in range(3):
            for b in range(a + 1, 3):
                A, B = data[labs[a]][kind][idx], data[labs[b]][kind][idx]
                n = idx.size
                Cm = np.array([[corr(A[i], B[j]) for j in range(n)] for i in range(n)])
                same, diff = np.diag(Cm), Cm[~np.eye(n, dtype=bool)]
                eff = same.mean() - diff.mean()
                perm = []
                for _ in range(5000):
                    p = rng.permutation(n)
                    s_ = Cm[np.arange(n), p].mean()
                    d_ = (Cm.sum() - Cm[np.arange(n), p].sum()) / (n * n - n)
                    perm.append(s_ - d_)
                pv = (1 + np.sum(np.array(perm) >= eff)) / 5001
                cc = corr(data[labs[a]]["ctrl_" + kind], data[labs[b]]["ctrl_" + kind])
                res["pairs"][f"{kind}:{labs[a]}-{labs[b]}"] = dict(
                    same_line_mean=float(same.mean()), different_line_mean=float(diff.mean()), effect=float(eff), p=float(pv),
                    same_line_values=[round(float(x), 3) for x in same], control_corr=cc,
                    diff_p95=float(np.percentile(diff, 95)), control_pass=bool(cc > np.percentile(diff, 95)))
    for kind in ("prim", "sec"):
        P = [v for k, v in res["pairs"].items() if k.startswith(kind)]
        if idx.size < 10 or sum(x["control_pass"] for x in P) < 2:
            v = "INCONCLUSIVE"
        elif sum(x["p"] <= 0.05 and x["effect"] > 0 for x in P) >= 2:
            v = "REPEATS"
        elif sum(x["p"] > 0.20 for x in P) >= 2:
            v = "DOES NOT REPEAT"
        else:
            v = "MIXED"
        res["verdict_" + kind] = v
    json.dump(res, open(os.path.join(T.RUNS, "test_q_repeat_pass.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "pairs"}))
    for k, v in res["pairs"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != "same_line_values"})


if __name__ == "__main__":
    a = sys.argv[1:]
    corr_ = (0, 0)
    if "--corr" in a:
        i = a.index("--corr"); corr_ = (float(a[i + 1]), float(a[i + 2])); a = a[:i] + a[i + 3:]
    if a[0] == "--extract":
        d = extract(a[1], corr_)
        np.savez(a[2], **d)
        print("wrote", a[2], "ok lines:", np.where(d["ok"])[0].tolist())
    elif a[0] == "--run":
        run([x.split("=", 1) for x in a[1:]])
