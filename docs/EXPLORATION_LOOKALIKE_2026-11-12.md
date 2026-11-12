# Exploration: tuning our image to look like Seyfzadeh's Osiris scan — 12 Nov 2026

> **Status: EXPLORATION, not a test.** Asked for by Hassan ("tune and play ... make an image that looks as
> similar to his as possible"). Done after Test P, with free tuning and his image as the target. Nothing
> here is evidence for or against a detection. The pre-registered result is RESULTS_FAKE_TARGETS_2026-11-12.md.

**Script:** `src/explore_p_lookalike.py` (`--prep`, `--maps`, `--search`, `--search2`). **Outputs:**
`runs/explore_p_03-08.json/.png` (first pass), `runs/explore_p_03-08_fine.json/.png` (second pass).
Scene: Umbra 03-08. Target: his "scan 1" (K=295), read off the copy published at
archaeologicalrescue.org/biondi-validation (frame `arf_manu_OS1_full.jpg`).

## What was tuned (beyond Test P's knobs)
Series preprocessing (none / polynomial detrend 2 or 4 / moving-average high-pass 31 or 15 / first
difference), depth scale 0.15-2 (second pass 1-2), a frequency offset at depth zero, run length P 3-8, a
black-level floor, smoothing, and for the Osiris line which of five line shifts. 400 random draws per
map, objective = correlation with his image + depth-profile match + a bonus for "hits" at 10/22/33 m.

## Result
- **Second pass (finer depth texture, own heat-map scale as his plots use):** Osiris line: correlation
  with his image 0.37, 3/3 levels "hit". Bare desert: 0.27, 3/3. Pure noise: 0.19, 3/3. All three show a
  busy field of patches fading with depth, with patches at the three crosses.
- First pass (coarse): 0.34 / 0.24 / 0.26, 3/3 in all three, but tall smeared columns unlike his texture.
- The decisive tuning steps were a high-pass on the displacement series (removes the bright surface band
  our untuned images had; his have none) and stretching the depth scale.
- The tuned Osiris-line image has a cluster of patches around positions 105-130, as his does. Caution: the
  search rewarded resemblance to his image and hits at position 120, and the Osiris line had five times as
  many draws (five line shifts), so this cannot be read as agreement. A surface cause (shaft mouth,
  causeway masonry) is also possible. Untested.

## What it shows
With free tuning, an image of his general kind, with patches at all three shaft levels, can be produced
from a line with a known shaft, from empty desert, and from noise. It does not show his image is an
artifact (different data, different code).

## Facts read from the ARF page (same day)
- No code, no scene IDs. Scan images and three interactive 3-D HTML models are posted; the Western
  Cemetery one (6.6 MB, plotly) appears to embed tomogram values and could be analysed.
- His scan 3 (the "more filtering" image; K=3360, W=1990, P=8, "unrestricted modes", 0-100 m): colour
  scale is **adjusted R^2 0 to about 0.009**. Its own caption: survey-model silhouettes "not fitted to
  this heat map"; the silhouette is drawn at positions about 134-143, where the heat map is nearly empty.
  Frame: `arf_manu_OS3_K3360.jpg`.
- Page claims: "independent, 3rd party replication"; retraction "politically motivated"; Grassi "in
  constant communication with them both"; Seyfzadeh "plans to present the work ... for peer review".
- Links: MDPI litigation PDF; a ChatGPT conversation page (opusmagnum.org/cracking-the-biondi-code-with-ai).
