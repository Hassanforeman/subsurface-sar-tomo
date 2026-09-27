# Pre-registration — descriptive audit of the 2026 "Second Sphinx" press images — 27 Sep 2026

*Written and committed BEFORE the images are downloaded or viewed. Descriptive, not a hypothesis test.
Purpose: record what the published 2026 imagery actually is, so that the next pre-registered test
(the "shafts are surface-driven" test, open item in STATE §3) is built on facts, not guesses.*

## E.1 Source
Images posted "with permission from Dr. Biondi" on archaeologicalrescue.org/secondsphinx/
(T. Grassi, 26 Jun 2026; Bologna press conference, 21 Jun 2026). Fetched on Hassan's Mac by
`fetch_press_images.sh` into `data/secondsphinx_2026/` (gitignored; not redistributed). The script
tries the original upload first (may keep EXIF), then the 1024x767 resize. Book covers, tour photos
and screenshots of social posts are excluded; every image the page presents as a scan is included
(files 07, 08, 17, 19-35, 37-44, 41-1, 46-58, 55-1, 60-64, 62-1, 66, 69-74, 78-1, 79, 80).

## E.2 Per-image checklist (recorded for every image, in this order, before any interpretation)
1. Type: 2-D slice/line | 3-D render (mesh/isosurface/point cloud/volume) | photo | drawing/map |
   composite | text/title slide.
2. Axes present? Units: metres | pixels | none.
3. Colour bar present? Labelled quantity?
4. Any metric scale: scale bar, voxel size, depth labels (record the numbers as printed).
5. Threshold / isosurface level / transfer function stated?
6. Overlay or underlay of pre-existing imagery (photo, drawing, map, model of a known monument)?
7. Software evidence: UI chrome, view-cube, grid floor, gizmos, watermark, window title, EXIF
   Software/Make tags (from `src/press_image_audit.py`).
8. SAR source stated (sensor, date, product ID)?
9. Geometric regularity suggesting modelled primitives (identical copies, exact symmetry, perfect
   cylinders/boxes, smooth analytic surfaces) — note only, no statistic.
10. Is the image a 2-D line consistent with the 2022 format (range x depth heat-map)?

## E.3 Expectations stated in advance (so they can be wrong)
- X1: no image states both a metric voxel size and a threshold/iso level.
- X2: at least one 3-D image shows modeller/render-engine UI traits or smooth primitive geometry.
- X3: the 2-D lines, if present, are the same range x depth heat-map format as 2022, still without
  metric axes.
Each is scored hit/miss in E.5. A miss is reported as a miss.

## E.4 What this cannot show
Intent; whether any feature is real; which software made an image unless the image or its metadata
says so. EXIF absence proves nothing (WordPress strips it on resize).

## E.5 Result
*To be appended after the audit. Deliberately empty at commit time.*

**Appended 27 Sep 2026.** 58 images audited. X1 HIT (no threshold/iso-level stated anywhere); X2 HIT
(78-1/79: navigation control, grid floor, identical primitives); X3 PARTIAL (Second Sphinx lines are
unscaled 2022-format heat-maps; the Great Sphinx figure 07/08 has a metric depth axis 0 to -1200 m).
Key descriptive result: the deck itself lists a Thermal-to-Visible GAN, face-landmark and face-
embedding tools and chatbot dialogue (Grok, Gemini) in the pipeline; the 3-D renders carry the known
Great Sphinx's form. → `docs/RESULTS_PRESS_IMAGES_2026-09-27.md`; `runs/press_image_audit.json`.
