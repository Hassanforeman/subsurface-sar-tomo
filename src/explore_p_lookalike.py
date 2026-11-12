"""EXPLORATION (not a test, not pre-registered): tune freely to make an S-like image look like the
Osiris-shaft image shown in "The Biondi Validation" video. Asked for by Hassan 12 Nov 2026.
Nothing here is evidence for or against a detection; it measures how far tuning alone goes.

  --prep IN.npz LABEL     compute displacement series for osiris / desert / noise lines (cached)
  --maps LABEL            score maps for each preprocessing variant (cached)
  --search LABEL          search cheap knobs to maximise similarity to his image; write PNG + JSON
"""
import json, os, sys
import numpy as np
from scipy.ndimage import uniform_filter, uniform_filter1d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T

RUNS = T.RUNS
FRAMES = os.path.join(T.HERE, "..", "docs", "img", "validation_video_2026-11-12")
PRE = ("none", "poly2", "poly4", "hp31", "hp15", "diff")


def his_image(name, box, vmax, pos0, pos1):
    """Read his heat map off a video frame -> array [position, depth 0.5 m bins], NaN where unreadable."""
    from PIL import Image
    import matplotlib
    lut = (matplotlib.colormaps["magma"](np.linspace(0, 1, 256))[:, :3] * 255)
    im = np.asarray(Image.open(os.path.join(FRAMES, name)).convert("RGB"), float)
    x0, x1, y0, y1 = box
    sub = im[y0:y1, x0:x1]
    val = np.zeros(sub.shape[:2])
    bad = np.zeros(sub.shape[:2], bool)
    for r in range(sub.shape[0]):                      # row by row (memory)
        d = ((sub[r][:, None, :] - lut[None]) ** 2).sum(-1)
        val[r] = d.argmin(-1) / 255.0 * vmax
        bad[r] = np.sqrt(d.min(-1)) > 40               # overlay lines, captions
    val[bad] = np.nan
    npos = int(round(pos1 - pos0))
    out = np.full((npos, T.NZ), np.nan)
    xs = np.linspace(0, sub.shape[1], npos + 1).astype(int)
    ys = np.linspace(0, sub.shape[0], T.NZ + 1).astype(int)
    for i in range(npos):
        for j in range(T.NZ):
            c = val[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            if np.isfinite(c).mean() > 0.5:
                out[i, j] = np.nanmedian(c)
    return out


def preprocess(q, mode):
    q = q.astype(np.float64)
    if mode == "none":
        return q
    if mode.startswith("poly"):
        n = np.arange(q.shape[1]) / q.shape[1]
        V = np.vander(n, int(mode[4:]) + 1)
        P = V @ np.linalg.pinv(V)
        return q - np.einsum("nm,tmc->tnc", P, q)
    if mode.startswith("hp"):
        return q - uniform_filter1d(q, int(mode[2:]), axis=1, mode="nearest")
    if mode == "diff":
        d = np.diff(q, axis=1)
        return np.concatenate([d, d[:, -1:]], axis=1)
    raise ValueError(mode)


def render(S, s, c0, p_run, floor, smooth):
    """S[pos, NFREQ] -> image[pos, 100]; c0 = frequency offset in cycles/window at depth 0."""
    z = T.DZ * (np.arange(T.NZ) + 1)
    idx = np.clip(np.round((c0 + s * z * T.CYC50 / 50.0) / T.CSTEP).astype(int) - 1, 0, T.NFREQ - 1)
    img = S[:, idx].copy()
    img[img < floor] = 0
    old = T.P_RUN
    T.P_RUN = p_run
    img = T.run_filter(img)
    T.P_RUN = old
    if smooth > 1:
        img = uniform_filter(img, size=(smooth, 1), mode="constant")
    return img


def stats(img):
    lit = img > 0.02
    prof = np.array([np.nanmean(lit[:, a:a + 20]) for a in range(0, 100, 20)])
    return float(np.nanmean(lit)), prof


def prep(path, label):
    d = T.load(path)
    rs, cs = float(d["row_ss"]), float(d["col_ss"])
    rng = np.random.default_rng(0)
    out = {}
    out["osiris"] = T.displacement(d["crop_osiris"], d["px_osiris"], rs, cs)
    out["desert"] = T.displacement(d["crop_desert"], d["px_desert"][2:3], rs, cs)
    out["noise"] = T.displacement(T.noise_like(d["crop_osiris"], rng), d["px_osiris"][2:3], rs, cs)
    np.savez_compressed(os.path.join(RUNS, f"explore_p_{label}_q.npz"), **out)


def maps(label):
    q = np.load(os.path.join(RUNS, f"explore_p_{label}_q.npz"))
    out = {}
    for mode in PRE:
        for li in range(5):
            out[f"osiris_{mode}_{li}"] = T.score_map(preprocess(q["osiris"][li], mode))
        out[f"desert_{mode}"] = T.score_map(preprocess(q["desert"][0], mode))
        out[f"noise_{mode}"] = T.score_map(preprocess(q["noise"][0], mode))
        print("done", mode, flush=True)
        np.savez_compressed(os.path.join(RUNS, f"explore_p_{label}_maps.npz"), **out)


def search(label, smin=0.15, tag=''):
    his = his_image("arf_manu_OS1_full.jpg", (50, 1458, 127, 636), 0.3022, 0.0, 149.0)   # full line, ARF page copy
    kh = his_image("khafre_west_83m.png", (45, 1172, 216, 626), 0.4368, 0, 216.5)
    his_lit, his_prof = stats(np.nan_to_num(his))
    kh_lit, kh_prof = stats(np.nan_to_num(kh))
    M = np.load(os.path.join(RUNS, f"explore_p_{label}_maps.npz"))
    lo = 0
    hv = np.nan_to_num(his)
    ok = np.isfinite(his)
    best = {}
    rng = np.random.default_rng(1)
    for kind in ("osiris", "desert", "noise"):
        top = (-9, None)
        for mode in PRE:
            lines = range(5) if kind == "osiris" else [0]
            for li in lines:
                S = M[f"osiris_{mode}_{li}"] if kind == "osiris" else M[f"{kind}_{mode}"]
                for _ in range(400):
                    s = float(np.exp(rng.uniform(np.log(smin), np.log(2.0))))
                    c0 = float(rng.choice([0, 0, 0.5, 1, 1.5, 2, 3]))
                    p_run = int(rng.choice([3, 4, 5, 6, 7, 8]))
                    floor = float(rng.choice([0, 0.02, 0.04, 0.06, 0.08, 0.1]))
                    sm = int(rng.choice([1, 1, 3]))
                    img = render(S, s, c0, p_run, floor, sm)
                    a = img[lo:lo + hv.shape[0]]
                    if a.std() == 0:
                        continue
                    corr = float(np.corrcoef(uniform_filter(a, 3)[ok], uniform_filter(hv, 3)[ok])[0, 1])
                    lit, prof = stats(img)
                    thr = np.percentile(img[img > 0], 50) if (img > 0).any() else 1
                    h = T.hits(img, thr, T.SHAFT_POS, T.REAL_DEPTHS)
                    score = corr - 0.5 * np.abs(prof - his_prof).mean() + 0.1 * h
                    if score > top[0]:
                        top = (score, dict(mode=mode, line=int(li), s=s, c0=c0, p_run=p_run, floor=floor, smooth=sm,
                                           corr_with_his=corr, lit=lit, depth_profile=prof.tolist(), levels_hit=int(h)))
        best[kind] = top[1]
        print(kind, json.dumps(top[1]), flush=True)
    res = dict(label=label, his=dict(osiris_lit=his_lit, osiris_profile=his_prof.tolist(), khafre_lit=kh_lit,
                                     khafre_profile=kh_prof.tolist()), best=best, n_trials_per_kind="400 x maps")
    json.dump(res, open(os.path.join(RUNS, f"explore_p_{label}{tag}.json"), "w"), indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(4, 1, figsize=(11, 14))
    ax[0].imshow(his.T, aspect="auto", cmap="magma", extent=[0, 149, 50, 0], vmin=0, vmax=0.30)
    ax[0].set_title("HIS image (Seyfzadeh scan 1, read off the copy on archaeologicalrescue.org)")
    for a, kind, ttl in zip(ax[1:], ("osiris", "desert", "noise"),
                            ("OURS, tuned: Osiris-shaft line", "OURS, tuned: bare desert (no shaft)",
                             "OURS, tuned: pure noise (no radar scene)")):
        b = best[kind]
        S = M[f"osiris_{b['mode']}_{b['line']}"] if kind == "osiris" else M[f"{kind}_{b['mode']}"]
        img = render(S, b["s"], b["c0"], b["p_run"], b["floor"], b["smooth"])
        a.imshow(img[lo:].T, aspect="auto", cmap="magma", extent=[0, 149, 50, 0], vmin=0,
                 vmax=max(1e-6, float(np.percentile(img, 99.8))))        # own heat-map scale, as his plots use
        a.set_title(f"{ttl}  [{label}; correlation with his {b['corr_with_his']:.2f}; levels 'hit' {b['levels_hit']}/3]")
    for a in ax:
        a.plot([120] * 3, T.REAL_DEPTHS, "c+", ms=13, mew=2)
        a.set_ylabel("nominal depth (m)")
    ax[-1].set_xlabel("line position (about 1 m spacing); crosses = shaft levels 10 / 22 / 33 m at position 120")
    fig.suptitle("EXPLORATION, tuned after the fact to resemble his image - not evidence of anything underground", y=0.995)
    fig.tight_layout()
    fig.savefig(os.path.join(RUNS, f"explore_p_{label}{tag}.png"), dpi=110)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--prep":
        prep(a[1], a[2])
    elif a[0] == "--maps":
        maps(a[1])
    elif a[0] == "--search":
        search(a[1])
    elif a[0] == "--search2":
        search(a[1], smin=1.0, tag="_fine")
