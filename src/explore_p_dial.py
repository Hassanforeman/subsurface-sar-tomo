"""EXPLORATION (not a test): how far does more tuning push the resemblance to his scan 1?
Equal budget for the shaft line, bare desert and pure noise; objective = correlation only.
Extra dials vs explore_p_lookalike: sideways slide of our image (+-20 positions), mirror, vertical smoothing.
Usage: python src/explore_p_dial.py 03-08 [draws]
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T
import explore_p_lookalike as E

label = sys.argv[1]
DRAWS = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
his = np.nan_to_num(E.his_image("arf_manu_OS1_full.jpg", (50, 1458, 127, 636), 0.3022, 0.0, 149.0))
hs = uniform_filter(his, 3)
M = np.load(os.path.join(T.RUNS, f"explore_p_{label}_maps.npz"))
res, imgs = {}, {}
for kind in ("osiris", "desert", "noise"):
    rng = np.random.default_rng(5)
    trace, best, bimg = [], -9, None
    for d in range(DRAWS):
        mode = E.PRE[rng.integers(len(E.PRE))]
        S = M[f"osiris_{mode}_2"] if kind == "osiris" else M[f"{kind}_{mode}"]
        s = float(np.exp(rng.uniform(np.log(0.15), np.log(2.0))))
        c0 = float(rng.uniform(0, 4)); p = int(rng.integers(2, 9)); fl = float(rng.uniform(0, 0.12))
        sm = int(rng.choice([1, 3, 5])); vs = int(rng.choice([1, 3, 5])); slide = int(rng.integers(-20, 21)); mir = bool(rng.integers(2))
        img = E.render(S, s, c0, p, fl, sm)
        if vs > 1:
            img = uniform_filter(img, size=(1, vs), mode="constant")
        if mir:
            img = img[::-1]
        img = np.roll(img, slide, axis=0)
        if img.std() == 0:
            continue
        c = float(np.corrcoef(uniform_filter(img, 3).ravel(), hs.ravel())[0, 1])
        if c > best:
            best, bimg = c, img
            bpar = dict(mode=mode, s=s, c0=c0, p_run=p, floor=fl, smooth=sm, vsmooth=vs, slide=slide, mirror=mir)
        if d + 1 in (100, 300, 1000, 3000, 10000, 30000):
            trace.append([d + 1, round(best, 3)])
    res[kind] = dict(best_corr=best, params=bpar, best_after_n_draws=trace)
    imgs[kind] = bimg
    print(kind, round(best, 3), trace, flush=True)
json.dump(dict(label=label, draws=DRAWS, result=res), open(os.path.join(T.RUNS, f"explore_p_{label}_dial.json"), "w"), indent=1)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(4, 1, figsize=(11, 14))
ax[0].imshow(his.T, aspect="auto", cmap="magma", extent=[0, 149, 50, 0], vmin=0, vmax=0.30)
ax[0].set_title("HIS scan 1")
for a, k, t in zip(ax[1:], ("osiris", "desert", "noise"), ("OURS: shaft line", "OURS: bare desert", "OURS: pure noise")):
    a.imshow(imgs[k].T, aspect="auto", cmap="magma", extent=[0, 149, 50, 0], vmin=0, vmax=float(np.percentile(imgs[k], 99.8)))
    a.set_title(f"{t}, best of {DRAWS} tunings: correlation with his {res[k]['best_corr']:.2f}")
fig.suptitle("EXPLORATION: tuned to resemble his image - not evidence of anything underground", y=0.995)
fig.tight_layout(); fig.savefig(os.path.join(T.RUNS, f"explore_p_{label}_dial.png"), dpi=100)
