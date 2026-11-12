"""Test R — repeat-pass consistency, corrected design. See docs/PREREGISTRATION_REPEAT_PASS_R_2026-11-12.md.
  --selftest
  --control SITE LABEL=FILE.npz ...     compute control images only (uses cached Test Q/R images)
  --run SITE LABEL=FILE.npz ...         full run for a site (images cached per label)
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T
import test_q_repeat_pass as Q

PLANTS = [((22, 38), 12.0), ((67, 83), 22.0), ((112, 128), 33.0)]


def planted_displacement(img, px, rs, cs):
    F, lo, hi = T.spectrum_support(img)
    tg = px.reshape(-1, 2)
    allc = np.concatenate([tg] + [tg + f for f in T.FLANKS])
    n = tg.shape[0]
    boxes = []
    for (a, b), d in PLANTS:
        seg = tg[a:b + 1]
        boxes.append((max(0, int(seg[:, 0].min()) - 16), int(seg[:, 0].max()) + 16,
                      max(0, int(seg[:, 1].min()) - 16), int(seg[:, 1].max()) + 16, d))
    q = np.zeros((n, T.K, 2), np.float32)
    for k in range(T.K):
        ref, off = T.make_pair(F, lo, hi, k)
        for r0, r1, c0, c1, d in boxes:
            th = 2 * np.pi * (d * T.CYC50 / 50.0) * k / T.W
            off[r0:r1, c0:c1] = T.fourier_shift(off[r0:r1, c0:c1], 0.25 * np.sin(th), 0.5 * np.cos(th))
        sh = T.shifts(ref, off, allc).reshape(7, n, 2)
        q[:, k, :] = sh[0] - 0.5 * (np.median(sh[1:4], axis=0) + np.median(sh[4:7], axis=0))
    q[..., 0] *= rs
    q[..., 1] *= cs
    return q


def line_images(d, tag):
    """All usable lines of one pass -> dict(prim, sec, ok); cached."""
    for name in (f"test_r_{tag}_images.npz", f"test_q_{tag}_images.npz"):
        f = os.path.join(T.RUNS, name)
        if os.path.exists(f):
            z = np.load(f)
            return dict(prim=z["prim"], sec=z["sec"], ok=z["ok"])
    rs, cs = float(d["row_ss"]), float(d["col_ss"])
    n = d["ok"].size
    prim, sec = np.zeros((n, T.NPOS, T.NZ - T.ZMIN_ROW)), np.zeros((n, T.NPOS, T.NZ))
    for k in range(n):
        if d["ok"][k]:
            prim[k], sec[k] = Q.images(T.displacement(d["crops"][k], d["px"][k][None], rs, cs)[0])
            print(tag, "line", k, flush=True)
    np.savez_compressed(os.path.join(T.RUNS, f"test_r_{tag}_images.npz"), prim=prim, sec=sec, ok=d["ok"])
    return dict(prim=prim, sec=sec, ok=d["ok"])


def control_images(d, tag):
    f = os.path.join(T.RUNS, f"test_r_{tag}_control.npz")
    if os.path.exists(f):
        z = np.load(f)
        return z["prim"], z["sec"]
    k = int(d["ctrl_line"]) if "ctrl_line" in d else int(np.argmax(d["ok"]))
    p, s = Q.images(planted_displacement(d["crops"][k].copy(), d["px"][k], float(d["row_ss"]), float(d["col_ss"])))
    np.savez_compressed(f, prim=p, sec=s)
    return p, s


def evaluate(site, labs, data, ctrl, need):
    ok = np.all([data[l]["ok"] for l in labs], axis=0)
    idx = np.where(ok)[0]
    n = idx.size
    rng = np.random.default_rng(0)
    res = dict(site=site, n_lines=int(n), lines_used=idx.tolist(), pairs={})
    for ki, kind in enumerate(("prim", "sec")):
        P = []
        for a in range(len(labs)):
            for b in range(a + 1, len(labs)):
                A, B = data[labs[a]][kind][idx], data[labs[b]][kind][idx]
                Cm = np.array([[Q.corr(A[i], B[j]) for j in range(n)] for i in range(n)])
                same, diff = np.diag(Cm), Cm[~np.eye(n, dtype=bool)]
                eff = same.mean() - diff.mean()
                perm = np.empty(5000)
                for t in range(5000):
                    p = rng.permutation(n)
                    sm = Cm[np.arange(n), p]
                    perm[t] = sm.mean() - (Cm.sum() - sm.sum()) / (n * n - n)
                pv = float((1 + np.sum(perm >= eff)) / 5001)
                cc = Q.corr(ctrl[labs[a]][ki], ctrl[labs[b]][ki])
                r = dict(same=float(same.mean()), different=float(diff.mean()), effect=float(eff), p=pv,
                         control=float(cc), diff_p95=float(np.percentile(diff, 95)), control_pass=bool(cc > np.percentile(diff, 95)))
                res["pairs"][f"{kind}:{labs[a]}-{labs[b]}"] = r
                P.append(r)
        npair = len(P)
        thr = int(np.ceil(need * npair - 1e-9))
        if n < 8 or sum(x["control_pass"] for x in P) < thr:
            v = "INCONCLUSIVE"
        elif sum(x["p"] <= 0.05 and x["effect"] > 0 for x in P) >= thr:
            v = "REPEATS"
        elif sum(x["p"] > 0.20 for x in P) >= thr:
            v = "DOES NOT REPEAT"
        else:
            v = "MIXED"
        res["verdict_" + kind] = v
        res["controls_passed_" + kind] = f"{sum(x['control_pass'] for x in P)} of {npair}"
    return res


def selftest():
    rng = np.random.default_rng(3)
    labs, data, ctrl = ["A", "B", "C"], {}, {}
    nl = 6
    m = np.zeros(T.CROP); m[100:900] = 1
    def speckle():
        w = rng.standard_normal((T.CROP, T.CROP)) + 1j * rng.standard_normal((T.CROP, T.CROP))
        return np.fft.ifft(np.fft.fft(w, axis=1) * m, axis=1).astype(np.complex64)
    for li, lab in enumerate(labs):
        step = (1.3, 2.0, 2.5)[li]                      # different pixel spacing per "pass"
        px = np.array([[330 + step * i, 512.0 + 0.2 * i] for i in range(T.NPOS)], np.float32)
        prim, sec = np.zeros((nl, T.NPOS, T.NZ - T.ZMIN_ROW)), np.zeros((nl, T.NPOS, T.NZ))
        for k in range(nl):
            prim[k], sec[k] = Q.images(T.displacement(speckle(), px[None], 0.5, 0.5)[0])
        data[lab] = dict(prim=prim, sec=sec, ok=np.ones(nl, bool))
        ctrl[lab] = Q.images(planted_displacement(speckle(), px, 0.5, 0.5))
        print("selftest pass", lab, "done", flush=True)
    res = evaluate("selftest", labs, data, ctrl, 2 / 3)
    P = [v for k, v in res["pairs"].items() if k.startswith("prim")]
    res["gate_control"] = sum(x["control_pass"] for x in P) >= 2
    res["gate_null"] = sum(x["p"] > 0.05 for x in P) >= 2
    res["GATE"] = "PASS" if res["gate_control"] and res["gate_null"] else "FAIL"
    json.dump(res, open(os.path.join(T.RUNS, "test_r_selftest.json"), "w"), indent=1)
    for k, v in res["pairs"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
    print({k: v for k, v in res.items() if k != "pairs"})


def run(site, pairs, control_only=False):
    labs = [l for l, _ in pairs]
    data, ctrl = {}, {}
    for lab, path in pairs:
        d = np.load(path)
        tag = lab if site == "giza" else f"{site}_{lab}"
        ctrl[lab] = control_images(d, tag)
        print(site, lab, "control done", flush=True)
        data[lab] = line_images(d, tag)
    res = evaluate(site, labs, data, ctrl, 2 / 3)
    json.dump(res, open(os.path.join(T.RUNS, f"test_r_{site}.json"), "w"), indent=1)
    for k, v in res["pairs"].items():
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
    print({k: v for k, v in res.items() if k != "pairs"})


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--selftest":
        selftest()
    elif a[0] == "--run":
        run(a[1], [x.split("=", 1) for x in a[2:]])
