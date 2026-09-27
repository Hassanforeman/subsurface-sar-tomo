#!/usr/bin/env python3
"""figure_information_secondary.py — NOT pre-registered robustness checks for C.4 step 2.
(1) pure-tomogram subset: excludes the 4 pairs whose (b) panel is a heat-map composited over a drawing/
    photograph (Figs 46-49; classified by visual inspection, descriptive).
(2) annotation robustness: the SAME median filter applied to both panels (kernel ~0.6% of panel width),
    which erases thin marks (tag text, arrows, leader lines) on both sides equally.
(3) resolution only: r(b)/r(a), which removes the panel-area term from N = area / r^2.
Output: runs/figure_information_secondary.json"""
import json, sys, os
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figure_information import s1_s2, luminance

COMPOSITE = {"Fig46", "Fig47", "Fig48", "Fig49"}
L = json.load(open("reference/figure_layout.json"))

def panel(fn, box, med=0):
    im = Image.open(fn).convert("RGB").crop(tuple(box))
    if med:
        im = im.filter(ImageFilter.MedianFilter(med))
    return luminance(np.asarray(im, float))

ROWS = "runs/figure_information_secondary_rows.json"
rows = json.load(open(ROWS)) if os.path.exists(ROWS) else {}
only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] != "summarize" else None
for p in L["pairs"]:
    fid = p["id"]
    if (only is not None and fid not in only) or (len(sys.argv) > 1 and sys.argv[1] == "summarize"):
        continue
    A = panel(p["a"]["file"], p["a"]["box"]); B = panel(p["b"]["file"], p["b"]["box"])
    k = max(3, int(round(0.006 * min(A.shape[1], B.shape[1]))) | 1)
    Am = panel(p["a"]["file"], p["a"]["box"], k); Bm = panel(p["b"]["file"], p["b"]["box"], k)
    sa, sb, sam, sbm = s1_s2(A), s1_s2(B), s1_s2(Am), s1_s2(Bm)
    rows[fid] = dict(composite=fid in COMPOSITE, N_ratio=sa["N"] / sb["N"],
                     N_ratio_median=sam["N"] / sbm["N"], median_kernel=k,
                     r_a=sa["r_px"], r_b=sb["r_px"], r_ratio=sb["r_px"] / sa["r_px"])
    print(f"{fid:<6}{'  composite' if fid in COMPOSITE else '           '}  N ratio {rows[fid]['N_ratio']:8.2f}"
          f"   after equal median({k}) {rows[fid]['N_ratio_median']:8.2f}   r(b)/r(a) {rows[fid]['r_ratio']:6.2f}")
    json.dump(rows, open(ROWS, "w"), indent=1)
if len(rows) < len(L["pairs"]):
    print(f"{len(rows)}/{len(L['pairs'])} figures done; rerun for the rest"); sys.exit(0)

def summ(sel, key):
    v = [rows[f][key] for f in sel]
    return dict(n=len(v), hits=int(sum(x > 1 for x in v)), median=float(np.median(v)))
pure = [f for f in rows if not rows[f]["composite"]]
out = dict(rows=rows,
           pure_N_ratio=summ(pure, "N_ratio"), all_median_filtered=summ(list(rows), "N_ratio_median"),
           pure_median_filtered=summ(pure, "N_ratio_median"),
           all_r_ratio=summ(list(rows), "r_ratio"), pure_r_ratio=summ(pure, "r_ratio"))
for k in ("pure_N_ratio", "all_median_filtered", "pure_median_filtered", "all_r_ratio", "pure_r_ratio"):
    s = out[k]; print(f"{k:<22} ratio>1 in {s['hits']}/{s['n']}  median {s['median']:.2f}")
json.dump(out, open("runs/figure_information_secondary.json", "w"), indent=1)
print("-> runs/figure_information_secondary.json")
