# What the 2022 paper's paired figures contain — pre-registered C.4 step 2 — 27 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_FIGURES_2026-09-27.md`, committed and pushed as `936e4ce`
**before the paper was obtained**; statistic revised (D.4a) after its controls failed, also before
the paper was obtained. Source: arXiv:2208.00811 v1 (the preprint of Remote Sens. 14(20):5231; the
journal PDF was blocked by MDPI, the pre-registered fallback applied), SHA-256
`906b9c64e2537a24d8e473a9dbce00c2a866a8e4dd98d6e6042cd0575c53d35c`, kept out of git under `data/`.
Scripts: `src/figure_information.py` (statistics, extraction), `src/figure_layout.py` (the one
cropping rule), `src/figure_information_secondary.py` (robustness). Outputs:
`runs/figure_information.json`, `runs/figure_information_secondary.json`,
`reference/figure_layout.json`.

Units: all 16 figures captioned "Tags association from tomography to 3D model. (a): 3D model of
Khnum-Khufu. (b): Tomographic reconstruction (magnitude)." — Figs 34-40 and 42-50. (Fig 41 is a
plain SLC image, excluded by rule D.3.) The cropping rule was set from a layout-only look at Figs 34
and 35 and applied automatically to all 16; the primary measurement was run immediately after the
crops were verified, before the panels were examined further.

## 1. Pre-registered result

| Prediction | Result |
|---|---|
| **P1** (primary) — N(model) > N(tomogram) in a majority of pairs | **HIT: 15 / 16** |
| **P1b** — median N(model)/N(tomogram) >= 4 | **HIT: 9.69x** |
| P2 — fine-detail fraction | not used (its statistic failed its control before the data, D.4a); descriptive 6/16 |
| P3 — tomogram resolution coarser than the claimed 3.71 m | **untestable: no tomogram panel carries axes or a scale** |

Per-pair N (independent samples, S2 v2): model panels 11 458-73 152; tomogram panels 69-15 438
except Fig 49 (172 820, see §3).

## 2. Robustness (not pre-registered; cannot overturn §1)

| Check | Model richer | Median ratio |
|---|---|---|
| 12 pure-tomogram pairs (Figs 46-49 excluded, §3) | 12/12 | 11.8x |
| Same median filter on both panels (erases tags, arrows, text on both sides) | 15/16 | 5.7x |
| Resolution only, r(tomogram)/r(model) (removes panel area) | 15/16 | 3.35x (pure: 3.65x) |

## 3. What the panels are (descriptive — visual inspection, no statistic, no verdict)

- **Every tomogram panel is a 2-D colour-mapped image (jet colour map) with no axes, no depth or
  distance units, no scale bar.** There is no rendered tomographic volume in any of the 16 figures.
  All three-dimensional geometry on the page is the CAD model's.
- **The association is made by hand-placed annotations:** numbered tags on the model, yellow arrows
  and "Tag N" labels on the tomogram. Because the tomogram panel has no scale, a reader cannot check
  that a tagged streak lies at the depth or position of the model element it is tagged to.
- **In 4 of 16 pairs (Figs 46, 47, 48, 49) the "tomographic reconstruction" panel is a semi-transparent
  heat-map composited over pre-existing imagery of the pyramid's known interior**: a technical
  cross-section drawing (46, 48), a drawing plus a photograph of the apex with a compass and an
  Eye-of-Horus logo (47), and a finely hatched engraving of the face (49).
- In three of those (46, 48, 49) the model panel itself embeds a scanned 2-D cross-section drawing
  with Italian labels and dimensions ("146,6 mt"), placed as a plane in the 3-D scene.
- **Fig 49, the one exception to P1, is explained by its underlay:** the engraving's dense hatching
  supplies the high-frequency content; the heat-map over it is smooth. The exception is the drawing's
  detail, not the radar's.

## 4. How strong is this? (honest reading)

- P1 was a **weak test by design**: a flat-shaded CAD render would be expected to carry more detail
  than a heat-map. The hit confirms, with numbers, what the caption already implies; it is not a
  surprise and should not be sold as one. The effect is large and robust (roughly 10x more samples,
  ~3.4x finer linear resolution), which rules out "the tomogram is just as detailed and we
  mis-read it".
- The more informative findings are in §3 and need no statistic: no scale on any tomogram, a manual
  tag-association, and four tomogram panels laid over the known interior drawings. That is the same
  move as the 2026 Titanic frame ("In-situ Photo Overlay"), here inside the peer-reviewed 2022 paper.
- **It updates our own earlier hypothesis.** §7 of our paper tried four times to reproduce a 3-D
  *rendered volume*. For the 2022 paper there is no rendered volume to reproduce: the 3-D appearance
  is the CAD model, the tomography is 2-D slices, and the linkage is hand-drawn. (The 2025 Giza
  imagery may be made differently; nothing here speaks to it.)

## 5. What this does not show (D.7)

It measures published images. It does not show intent, what the authors' raw volume contained, or
that any tagged streak is or is not a real feature — only that the displayed geometry is not
derivable from the displayed tomogram, and that no displayed tomogram carries the scale needed to
check the association.

## 6. Replication on the journal version (added 27 Sep 2026, same day)

The pre-registered source was the journal PDF; we measured arXiv v1 under the D.2 fallback. The
journal figures were then fetched from MDPI's image server (`fetch_journal_figures.sh`, g039-g056,
kept out of git under `data/biondi2022/journal/`).

- **Mapping.** The 16 pairs are journal Figs 39-47, 49-52, 54-56 (identified by the "3D model" (a)
  panel). Non-pairs: Fig 48 = arXiv Fig 41 (SLC image + tomogram + overlay on a pyramid drawing);
  Fig 53 = "Entrance of the new corridor" photo + "Tomographic imaging of the new corridor". Fig 53
  is not in the arXiv Figs 34-50 block.
- **The 16 pair images did not change.** Same crop rule (`figure_layout.py --journal`), then the
  z-scored luminance of each journal crop was correlated with its arXiv counterpart: r = 1.00 for
  all 32 panels (0.99 for J55(b), i.e. arXiv Fig 49(b)). The 2022 reviewer asked for "meaningful
  axes"; **no axes or scale were added to any of the 16 tomogram panels** in the published version.
- **Measurement replicates** (expected, given identical images): P1 15/16, P1b median 10.47x (arXiv
  9.69x; the difference is image resolution only), single miss J55 = arXiv Fig 49.
  → `runs/figure_information_journal.json`, `reference/figure_layout_journal.json`.
- **The only tomogram panels with axes anywhere in this block (Figs 48 and 53) are labelled in
  pixels** — "Range (pixel)", "Height (pixel)", "Azimuth (pixel)" — not metres. Fig 53(b) is itself a
  heat-map overlaid on the known cross-section drawing, so it is a fifth overlay (outside the 16).
  By contrast, the CAD model is dimensioned in metres (e.g. "72.69 m", "23.498 m" in arXiv Figs 51-53).
  So the metric scale on the page belongs to the model, not to the measurement.
