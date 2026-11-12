"""EXPLORATION (not a test): tune an S-like image along a range line through the Vesuvius crater
(Umbra 2023-11-15) to resemble Fig. 8(b) of Biondi 2022 (Remote Sens. 14, 3828), then apply the same
search to (i) noise carrying only the scene's brightness envelope and (ii) pure noise.
Biondi's data were COSMO-SkyMed and his code is not public; ours is Umbra and our reconstruction.
  --prep STRIP.npz      displacement series for the three inputs (cached)
  --maps                score maps per preprocessing (cached)
  --search [draws]      random tuning search; PNG + JSON
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter, uniform_filter1d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T
import explore_p_lookalike as E

RUNS = T.RUNS
STEP = 8
NPOSV = 2200
PRE = ("none", "poly2", "hp31", "hp15")
T.NFREQ, T.CSTEP = 400, 0.06                    # coarser frequency grid (up to 24 cycles), for speed


def his_fig():
    from PIL import Image
    import matplotlib
    lut = matplotlib.colormaps["jet"](np.linspace(0, 1, 256))[:, :3] * 255
    im = np.asarray(Image.open(os.path.join(E.FRAMES, "biondi_vesuvius_fig8.jpg")).convert("RGB"), float)
    sub = im[150:514, 850:1488]
    val = np.zeros(sub.shape[:2]); bad = np.zeros(sub.shape[:2], bool)
    for r in range(sub.shape[0]):
        d = ((sub[r][:, None, :] - lut[None]) ** 2).sum(-1)
        val[r] = d.argmin(-1) / 255.0
        bad[r] = (np.sqrt(d.min(-1)) > 80) | (val[r] > 0.97)      # annotations, DEM curve (dark red)
    val[bad] = np.nan
    out = np.full((300, 100), np.nan)
    xs = np.linspace(0, sub.shape[1], 301).astype(int); ys = np.linspace(0, sub.shape[0], 101).astype(int)
    for i in range(300):
        for j in range(100):
            c = val[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            if np.isfinite(c).mean() > 0.4:
                out[i, j] = np.nanmedian(c)
    return out


def prep(path):
    d = np.load(path)
    img = d["strip"]
    rs, cs = float(d["row_ss"]), float(d["col_ss"])
    r = 96 + STEP * np.arange(NPOSV)
    px = np.c_[r, np.full(NPOSV, 512.0)].astype(np.float32)
    rng = np.random.default_rng(0)
    env = np.sqrt(uniform_filter(np.abs(img).astype(np.float32) ** 2, 33))
    out = dict(amp=np.array([env[int(a) - 16:int(a) + 16, 500:524].mean() for a in r]))
    print("real", flush=True)
    out["real"] = T.displacement(img, px[None], rs, cs)[0]
    np.savez_compressed(os.path.join(RUNS, "explore_ves_q.npz"), **out)
    noise = T.noise_like(img, rng)
    print("envelope noise", flush=True)
    out["envnoise"] = T.displacement((noise / (np.sqrt(uniform_filter(np.abs(noise) ** 2, 33)) + 1e-9) * env).astype(np.complex64), px[None], rs, cs)[0]
    np.savez_compressed(os.path.join(RUNS, "explore_ves_q.npz"), **out)
    print("pure noise", flush=True)
    out["noise"] = T.displacement(noise, px[None], rs, cs)[0]
    np.savez_compressed(os.path.join(RUNS, "explore_ves_q.npz"), **out)
    print("PREP DONE", flush=True)


def maps():
    q = np.load(os.path.join(RUNS, "explore_ves_q.npz"))
    out = dict(amp=q["amp"])
    for kind in ("real", "envnoise", "noise"):
        for mode in PRE:
            out[f"{kind}_{mode}"] = T.score_map(E.preprocess(q[kind], mode))
            print(kind, mode, flush=True)
            np.savez_compressed(os.path.join(RUNS, "explore_ves_maps.npz"), **out)
    print("MAPS DONE", flush=True)


def render(S, amp, s, c0, vs, hs, gamma, aw):
    j = np.clip(np.round((c0 + s * np.linspace(0.12, 12, 100)) / T.CSTEP).astype(int) - 1, 0, T.NFREQ - 1)
    img = S[:, j].astype(np.float64)
    img = img * (amp[:, None] / np.median(amp)) ** aw                  # optional brightness weighting
    img = img.reshape(300, -1, 100)[:, :NPOSV // 300].mean(axis=1) if False else np.array([img[a:b].mean(axis=0) for a, b in zip(np.linspace(0, NPOSV, 301).astype(int)[:-1], np.linspace(0, NPOSV, 301).astype(int)[1:])])
    img = uniform_filter(img, size=(hs, vs))
    img = np.clip(img, 0, None) ** gamma
    m = np.percentile(img, 99.5)
    return img / m if m > 0 else img


def search(draws=4000):
    his = his_fig()
    ok = np.isfinite(his)
    hsm = np.where(ok, his, np.nanmean(his))
    M = np.load(os.path.join(RUNS, "explore_ves_maps.npz"))
    amp = M["amp"]
    res, imgs = {}, {}
    for kind in ("real", "envnoise", "noise"):
        rng = np.random.default_rng(2)
        best, trace = -9, []
        for d in range(draws):
            mode = PRE[rng.integers(len(PRE))]
            par = dict(mode=mode, s=float(np.exp(rng.uniform(np.log(0.1), np.log(2.0)))), c0=float(rng.uniform(0, 3)),
                       vs=int(rng.choice([1, 3, 5, 9, 15])), hs=int(rng.choice([1, 3, 5, 9])),
                       gamma=float(rng.choice([0.5, 0.75, 1.0, 1.5])), aw=float(rng.choice([0, 0, 0.5, 1.0])),
                       mirror=bool(rng.integers(2)))
            img = render(M[f"{kind}_{mode}"], amp, par["s"], par["c0"], par["vs"], par["hs"], par["gamma"], par["aw"])
            if par["mirror"]:
                img = img[::-1]
            c = float(np.corrcoef(img[ok], hsm[ok])[0, 1]) if img.std() > 0 else -1
            if c > best:
                best, bpar, bimg = c, par, img
            if d + 1 in (100, 1000, draws):
                trace.append([d + 1, round(best, 3)])
        res[kind] = dict(best_corr=best, params=bpar, trace=trace)
        imgs[kind] = bimg
        print(kind, round(best, 3), trace, bpar, flush=True)
    json.dump(dict(draws=draws, result=res), open(os.path.join(RUNS, "explore_ves.json"), "w"), indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(4, 1, figsize=(11, 14))
    ext = [0, 5400, -2400, 1400]
    ax[0].imshow(his.T, aspect="auto", cmap="jet", extent=ext, vmin=0, vmax=1)
    ax[0].set_title("Biondi 2022, Vesuvius Fig. 8(b), read off the published figure (annotations masked)")
    for a, k, t in zip(ax[1:], ("real", "envnoise", "noise"),
                       ("OURS, tuned: real Umbra line through the crater", "OURS, tuned: noise with only the scene's brightness pattern",
                        "OURS, tuned: pure noise")):
        a.imshow(imgs[k].T, aspect="auto", cmap="jet", extent=ext, vmin=0, vmax=1)
        a.set_title(f"{t}  [correlation with his figure {res[k]['best_corr']:.2f}]")
    for a in ax:
        a.set_ylabel("nominal height (m)")
    ax[-1].set_xlabel("range direction (his pixel scale)")
    fig.suptitle("EXPLORATION: tuned after the fact to resemble his figure - different satellite, our reconstruction", y=0.995)
    fig.tight_layout(); fig.savefig(os.path.join(RUNS, "explore_ves.png"), dpi=100)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--prep":
        prep(a[1])
    elif a[0] == "--maps":
        maps()
    elif a[0] == "--search":
        search(int(a[1]) if len(a) > 1 else 4000)
    elif a[0] == "--all":
        prep(a[1]); maps(); search()
