"""EXPLORATION (not a test): tune until our blobs loosely match the size, intensity and location of the
blobs Seyfzadeh/Grassi point to in his Osiris scan 1 (ovals at position ~120: 10, 22, 33 m and the deeper
"unknown" one near 46 m).  Equal budget for the shaft line, bare desert and pure noise.
Intensity is relative to each image's own scale (his plots use "own heat-map scale").
Usage: python src/explore_p_blobs.py 03-08 [draws]
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T
import explore_p_lookalike as E

label = sys.argv[1]
DRAWS = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
OVALS = [(120, 10.0), (120, 22.0), (120, 33.0), (120, 46.0)]      # (position, depth m)
HALF_P, HALF_Z = 10, 3.0                                           # oval half-sizes (as in Test P)
LIT = 0.15                                                         # "lit" = above 15% of own scale


def norm(img):
    s = float(np.percentile(img, 99.8))
    return img / s if s > 0 else img


def runs_mean(mask, axis):
    m = mask if axis == 0 else mask.T
    tot = n = 0
    for col in m.T:
        d = np.diff(np.r_[0, col.astype(int), 0])
        ln = np.where(d == -1)[0] - np.where(d == 1)[0]
        tot += ln.sum(); n += ln.size
    return tot / n if n else 0.0


def describe(img):
    a = norm(img)
    lit = a > LIT
    ov = []
    for p, z in OVALS:
        z0, z1 = int((z - HALF_Z) / T.DZ) - 1, int((z + HALF_Z) / T.DZ)
        w = a[p - HALF_P:p + HALF_P + 1, max(z0, 0):min(z1, T.NZ)]
        ov.append((float(w.max()), float((w > LIT).mean())))
    return dict(ovals=ov, lit=float(lit.mean()), width=runs_mean(lit, 0), height=runs_mean(lit, 1) * T.DZ,
                prof=[float(lit[:, i:i + 20].mean()) for i in range(0, 100, 20)])


def distance(d, h):
    e = 0.0
    for (m, f), (hm, hf) in zip(d["ovals"], h["ovals"]):
        e += abs(np.log((m + 0.02) / (hm + 0.02))) + 2 * abs(f - hf)
    e += abs(np.log((d["width"] + 0.5) / (h["width"] + 0.5))) + abs(np.log((d["height"] + 0.25) / (h["height"] + 0.25)))
    e += 3 * abs(d["lit"] - h["lit"]) + 2 * float(np.mean(np.abs(np.array(d["prof"]) - np.array(h["prof"]))))
    return e


def loose_match(d, h, n=4):
    """Their standard, made explicit: a blob in every oval, intensity within a factor 2, blob size within a factor 2."""
    ok = all(m >= 0.5 * hm and f > 0 for (m, f), (hm, hf) in list(zip(d["ovals"], h["ovals"]))[:n])
    return bool(ok and 0.5 <= (d["width"] + 1e-9) / h["width"] <= 2 and 0.5 <= (d["height"] + 1e-9) / h["height"] <= 2)


his = np.nan_to_num(E.his_image("arf_manu_OS1_full.jpg", (50, 1458, 127, 636), 0.3022, 0.0, 149.0))
H = describe(his)
M = np.load(os.path.join(T.RUNS, f"explore_p_{label}_maps.npz"))
res, imgs = {"his": H}, {}
for kind in ("osiris", "desert", "noise"):
    rng = np.random.default_rng(11)
    best, bimg, npass, ntry, npass3 = 1e9, None, 0, 0, 0
    for _ in range(DRAWS):
        mode = E.PRE[rng.integers(len(E.PRE))]
        S = M[f"osiris_{mode}_2"] if kind == "osiris" else M[f"{kind}_{mode}"]
        s = float(np.exp(rng.uniform(np.log(0.15), np.log(2.0))))
        c0 = float(rng.uniform(0, 4)); p = int(rng.integers(2, 9)); fl = float(rng.uniform(0, 0.12))
        sm = int(rng.choice([1, 3, 5])); vs = int(rng.choice([1, 3, 5])); slide = int(rng.integers(-20, 21))
        img = E.render(S, s, c0, p, fl, sm)
        if vs > 1:
            img = uniform_filter(img, size=(1, vs), mode="constant")
        img = np.roll(img, slide, axis=0)
        if img.max() <= 0:
            continue
        ntry += 1
        d = describe(img)
        ok4 = loose_match(d, H)
        npass += ok4
        npass3 += loose_match(d, H, 3)
        e = distance(d, H) + (0 if ok4 else 100)          # prefer tunings that pass the loose match
        if e < best:
            best, bimg, bd = e, img, d
            bpar = dict(mode=mode, s=s, c0=c0, p_run=p, floor=fl, smooth=sm, vsmooth=vs, slide=slide)
    res[kind] = dict(distance=best, n_pass_4_ovals=int(npass), n_pass_3_known_levels=int(npass3), share_of_tunings_passing_loose_match=npass / ntry, n=ntry, best=bd, params=bpar,
                     corr_with_his=float(np.corrcoef(uniform_filter(bimg, 3).ravel(), uniform_filter(his, 3).ravel())[0, 1]))
    imgs[kind] = bimg
    print(kind, "pass4", npass, "pass3", npass3, "of", ntry, "best", json.dumps(bd)[:300], flush=True)
json.dump(dict(label=label, draws=DRAWS, ovals=OVALS, result=res), open(os.path.join(T.RUNS, f"explore_p_{label}_blobs.json"), "w"), indent=1)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
fig, ax = plt.subplots(4, 1, figsize=(11, 14))
panels = [("HIS scan 1 (Osiris Shaft line)", norm(his))] + [
    (f"OURS, tuned: {n}  [{res[k]['n_pass_4_ovals']} of {res[k]['n']} random tunings put a matching blob in all 4 ovals; {res[k]['n_pass_3_known_levels']} in the 3 known levels]", norm(imgs[k]))
    for k, n in (("osiris", "shaft line"), ("desert", "bare desert, no shaft"), ("noise", "pure noise, no radar scene"))]
for a, (t, im) in zip(ax, panels):
    a.imshow(im.T, aspect="auto", cmap="magma", extent=[0, 149, 50, 0], vmin=0, vmax=1)
    for p, z in OVALS:
        a.add_patch(Ellipse((p, z), 2 * HALF_P, 2 * HALF_Z, fill=False, ec="white", lw=1.5))
    a.set_title(t); a.set_ylabel("nominal depth (m)")
ax[-1].set_xlabel("line position (about 1 m spacing). Ovals: shaft levels 10 / 22 / 33 m and the deeper 'unknown' one, as pointed to in the video")
fig.suptitle("EXPLORATION: tuned after the fact so blobs fall in his ovals - not evidence of anything underground", y=0.995)
fig.tight_layout(); fig.savefig(os.path.join(T.RUNS, f"explore_p_{label}_blobs.png"), dpi=100)
