#!/usr/bin/env python3
"""
figure_layout.py — the single, automatic cropping rule for the 16 paired figures (Figs 34-40, 42-50)
of Biondi & Malanga (arXiv:2208.00811), per PREREGISTRATION_FIGURES_2026-09-27.md D.3.

Rule (fixed from a layout-only look at Figs 34 and 35, before any statistic was computed):
  1. Luminance < 235 marks "ink"; rows/columns that are >= 97% white are background.
  2. Split point = the whitest column in the central 35-65% of the width (the gutter between panels).
  3. For each half: keep the longest contiguous run of ink rows (drops the title strip above and the
     "(a)"/"(b)" labels below), then trim white columns at both ends.
  4. Inset 1.5% on every side to remove frame lines.
  In-panel annotations (tag circles/numbers in (a), yellow arrows/"Tag N" text in (b)) cannot be
  cropped out and are LEFT IN. A secondary run masks them (see figure_information measure --mask).

  python3 src/figure_layout.py            -> reference/figure_layout.json + runs/figure_layout_contact.png
  python3 src/figure_layout.py --journal  -> reference/figure_layout_journal.json (+ _journal_contact.png)
"""
import json, os, sys
import numpy as np
from PIL import Image

PAIRS = [34, 35, 36, 37, 38, 39, 40, 42, 43, 44, 45, 46, 47, 48, 49, 50]
IMGDIR = "data/biondi2022/images"
PDF = "data/biondi2022/biondi_malanga_2022_arxiv_2208.00811.pdf"
# Replication on the JOURNAL version (Remote Sens. 2022, 14, 5231; figures from MDPI's image server via
# fetch_journal_figures.sh). Same rule, unchanged; only the file list differs. Pairs identified by the
# "3D model" (a) panel: g039-g047, g049-g052, g054-g056. Non-pairs: g048 (SLC + tomogram + overlay),
# g053 (corridor photo + tomogram overlay).
JPAIRS = [39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 54, 55, 56]
JDIR = "data/biondi2022/journal"
INK, WHITE_FRAC, INSET = 235, 0.97, 0.015


def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def longest_run(mask):
    best, cur, bs, s = 0, 0, 0, 0
    for i, v in enumerate(mask):
        if v:
            if cur == 0:
                s = i
            cur += 1
            if cur > best:
                best, bs = cur, s
        else:
            cur = 0
    return bs, bs + best


def crop_half(L, x0, x1):
    sub = L[:, x0:x1]
    ink_rows = (sub < INK).mean(axis=1) > (1 - WHITE_FRAC)
    y0, y1 = longest_run(ink_rows)
    band = sub[y0:y1]
    ink_cols = np.where((band < INK).mean(axis=0) > (1 - WHITE_FRAC))[0]
    cx0, cx1 = x0 + ink_cols[0], x0 + ink_cols[-1] + 1
    w, h = cx1 - cx0, y1 - y0
    dx, dy = int(INSET * w), int(INSET * h)
    return [int(cx0 + dx), int(y0 + dy), int(cx1 - dx), int(y1 - dy)]


def find_file(fig):
    for f in sorted(os.listdir(IMGDIR)):
        if f.endswith(f"_Im{fig}.jpg") or f.endswith(f"_Im{fig}.png"):
            return os.path.join(IMGDIR, f)
    raise FileNotFoundError(fig)


def main(journal=False):
    if journal:
        figs, pfx = JPAIRS, "J"
        src, sha = "MDPI journal images g039-g056 (fetch_journal_figures.sh)", None
        out_json, out_png = "reference/figure_layout_journal.json", "runs/figure_layout_journal_contact.png"
    else:
        idx = json.load(open(os.path.join(IMGDIR, "_index.json")))
        figs, pfx, src, sha = PAIRS, "Fig", PDF, idx["sha256"]
        out_json, out_png = "reference/figure_layout.json", "runs/figure_layout_contact.png"
    pairs, thumbs = [], []
    for fig in figs:
        fn = os.path.join(JDIR, f"remotesensing-14-05231-g0{fig}.png") if journal else find_file(fig)
        a = np.asarray(Image.open(fn).convert("RGB")).astype(float)
        L = lum(a)
        H, W = L.shape
        lo, hi = int(0.35 * W), int(0.65 * W)
        colwhite = (L[:, lo:hi] >= INK).mean(axis=0)
        split = lo + int(np.argmax(colwhite))
        boxA, boxB = crop_half(L, 0, split), crop_half(L, split, W)
        pairs.append(dict(id=f"{pfx}{fig}", a=dict(file=fn, box=boxA), b=dict(file=fn, box=boxB),
                          split_col=split, image_size=[W, H],
                          desc=dict(b_render="2-D colour-mapped magnitude image (jet), no axes/scale",
                                    a_render="3-D perspective CAD model with numbered tags",
                                    shared_camera=False, b_metric_scale=False)))
        for box in (boxA, boxB):
            t = Image.fromarray(a[box[1]:box[3], box[0]:box[2]].astype("uint8"))
            t.thumbnail((360, 200)); thumbs.append(t)
    L = dict(pdf=src, pdf_sha256=sha,
             crop_rule=__doc__.split("Rule")[1].split("python3 src")[0].strip(),
             pairs=pairs)
    os.makedirs("reference", exist_ok=True)
    json.dump(L, open(out_json, "w"), indent=1)
    cols, rows = 4, (len(thumbs) + 3) // 4
    sheet = Image.new("RGB", (cols * 370, rows * 210), "white")
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 370, (i // cols) * 210))
    os.makedirs("runs", exist_ok=True)
    sheet.save(out_png)
    print(f"{len(pairs)} pairs -> {out_json}; crops -> {out_png}")


if __name__ == "__main__":
    main(journal="--journal" in sys.argv)
