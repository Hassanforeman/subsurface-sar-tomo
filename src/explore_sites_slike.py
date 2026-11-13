"""EXPLORATION (13 Nov 2026, not pre-registered): the S-like pipeline of Test P, unchanged, on three
scenes where nobody claims a buried structure (Butte, Komati, central Cairo), plus a noise scene and
a planted control for each.  Question: how often does the pipeline show a "three-level shaft" at an
INVENTED target (the 200 fake targets fixed for Test P) on ground with no claim attached?

"S-like" = OUR reconstruction of M. Seyfzadeh's publicly described pipeline; it is not his code.
Single passes only: this says nothing about repeatability.
Input: crops made on the Mac by runs/_sites_extract.py (1024 x 1024 at the scene centre, five
parallel lines of 149 positions along azimuth, 2 m apart in range).
Usage: python src/explore_sites_slike.py IN.npz LABEL -> runs/explore_sites_<LABEL>.json (+ PNG)
"""
import json, os, sys
import numpy as np
import test_p_fake_targets as P


def run(path, label):
    z = np.load(path)
    rs, cs = float(z["row_ss"]), float(z["col_ss"])
    img, px = z["crop_site"], z["px_site"]
    fakes = P.fake_targets()
    rng = np.random.default_rng(0)
    fam = {}
    q = P.displacement(img, px, rs, cs)
    fam["site"] = np.array([P.score_map(q[i]) for i in range(q.shape[0])])
    q = P.displacement(img.copy(), px, rs, cs, plant_at=px[2, P.CTRL_POS])
    fam["planted"] = np.array([P.score_map(q[i]) for i in range(q.shape[0])])
    q = P.displacement(P.noise_like(img, rng), px, rs, cs)
    fam["noise"] = np.array([P.score_map(q[i]) for i in range(q.shape[0])])

    F_s, T_s, busy_s = P.evaluate(fam["site"], fakes)
    F_n, T_n, busy_n = P.evaluate(fam["noise"], fakes)
    F_p, T_p, busy_p = P.evaluate(fam["planted"], [(P.CTRL_POS, P.REAL_DEPTHS)])
    F_o, T_o, _ = P.evaluate(fam["site"], [(P.CTRL_POS, P.REAL_DEPTHS)])       # same spot, nothing planted
    stat = lambda S: dict(max=float(S.max()), p99=float(np.percentile(S, 99)), median=float(np.median(S)),
                          share_positive=float((S > 0).mean()))
    res = dict(label=label, source=os.path.basename(path), lat=float(z["lat"]), lon=float(z["lon"]),
               collect=str(z["collect"]), duration_s=float(z["dur"]), row_ss=rs, col_ss=cs,
               step_px=float(z["step_px"]), position_spacing_m=float(z["step_px"]) * cs,
               n_configs=len(P.SHIFTS_M) * len(P.S_GRID) * len(P.SMOOTH), n_fakes=len(fakes),
               share_fakes_3of3_some_config=dict(site=float(T_s.mean()), noise=float(T_n.mean())),
               median_F_fakes=dict(site=float(np.median(F_s)), noise=float(np.median(F_n))),
               max_F_fakes=dict(site=float(F_s.max()), noise=float(F_n.max())),
               busyness=dict(site=busy_s, noise=busy_n, planted=busy_p),
               control=dict(F_planted=float(F_p[0]), F_same_spot_unplanted=float(F_o[0]),
                            p_vs_site_fakes=P.pval(F_p[0], F_s)),
               adjR2=dict(site=stat(fam["site"]), noise=stat(fam["noise"])))
    res["control_ok"] = bool(res["control"]["p_vs_site_fakes"] <= 0.05)
    json.dump(res, open(os.path.join(P.RUNS, f"explore_sites_{label}.json"), "w"), indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(11, 10))
    for a, (name, title) in zip(ax, (("site", "real scene, nothing claimed here"),
                                     ("planted", "same scene + planted signal at position 60"),
                                     ("noise", "pure noise (no radar scene)"))):
        im = P.image_for(fam[name][2], 1.0, 1)
        a.imshow(im.T, aspect="auto", cmap="magma", extent=[0, P.NPOS, 50, 0])
        a.set_title(f"{label}: {title}  [S-like, s=1, no smoothing, no line shift]")
        a.set_ylabel("nominal depth (m)")
    ax[1].plot([P.CTRL_POS] * 3, P.REAL_DEPTHS, "c+", ms=12)
    ax[-1].set_xlabel("line position")
    fig.tight_layout()
    fig.savefig(os.path.join(P.RUNS, f"explore_sites_{label}.png"), dpi=110)
    print(json.dumps(res, indent=1), flush=True)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
