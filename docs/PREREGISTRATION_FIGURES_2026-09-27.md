# Pre-registration — C.4 step 2: what the 2022 paper's paired figures actually contain

**Written 27 Sep 2026, before the 2022 paper's figure images have been obtained, extracted or
measured in this repository.** Step 1 (real Giza volumes) is complete and committed
(`a7c7d7a`, RESULTS_SHAPE_METRIC_GIZA_2026-09-26.md), so the ordering rule in
PREREGISTRATION_MINES_AND_GRANSASSO.md C.4 now permits this step. The results section at the end is
deliberately empty and will be appended in a later commit; nothing above it will be edited.

Honest disclosure of prior exposure: earlier sessions read the paper's text and the caption of its
paired figures ("Tags association from tomography to 3D model. (a): 3D model of Khnum-Khufu.
(b): Tomographic reconstruction (magnitude)."). No figure has been measured.

## D.1 Question

The paper's 3-D figures pair (a) a 3-D model with (b) a "tomographic reconstruction (magnitude)".
How much independent spatial information does each panel carry, and does panel (a) contain detail
finer than anything panel (b) carries? If (a) holds structure that (b) cannot, the published
geometry comes from the model, not the radar — measured on the authors' own figures.

## D.2 Source

The published article, Remote Sens. 2022, 14(20), 5231 (CC-BY 4.0; retracted 10 Aug 2026, still
hosted with a retraction mark). Fallback if the journal PDF cannot be obtained: arXiv:2208.00811.
The file is kept out of git (it lives under `data/`); its URL and SHA-256 are recorded in the results.
Figures are extracted as the embedded raster images at native resolution — no re-rendering.

## D.3 Units of analysis

Every figure whose caption pairs "(a) 3D model" with "(b) Tomographic reconstruction". If a figure is
a single embedded image containing both panels, the split is set from the layout (panel boundaries,
axes, colour bars, labels) and **the same cropping rule is applied to every figure**. A one-time
**layout-only** inspection is permitted to set that rule; it records panel positions only, and no
statistic may be computed or changed after it. Axes, tick labels, colour bars and text are excluded
from the analysed region. Each panel is converted to luminance (Rec. 601) before measurement.

## D.4 Statistics (fixed now)

For each panel, on the cropped luminance image (mean-subtracted, Hann-windowed):

- **S1 effective resolution r (pixels).** Radially averaged power spectrum P(f). Floor = median of P
  over the top 10% of radial frequencies. Cutoff f_c = the highest frequency at which P(f) still
  exceeds 2x the floor. r = 1 / f_c.
- **S2 independent samples N = (panel area in px) / r^2.**
- **S3 fine-detail fraction.** For a pair, using panel (b)'s cutoff f_c(b): the fraction of
  panel (a)'s spectral energy above f_c(b), E_a, and the same fraction for panel (b), E_b.
- **S4 (conditional).** Where panel (b) carries a labelled metric scale, r(b) in metres, compared
  with the paper's own claimed depth resolution of ~3.71 m.

Plus two descriptive records per figure (not statistics, no verdict attached): rendering type of
(b) (slice / voxel cloud / isosurface / other) and whether (a) and (b) share the same camera view.

### D.4a Revision after the controls failed — made 27 Sep 2026, still BEFORE any figure was obtained

The D.5 controls were run the same day, before the paper's figures were downloaded. Two failures, recorded
here rather than quietly patched (the same practice as C.1):

1. **S1 as written above (floor-relative cutoff) failed its positive control.** It ranked the
   Gaussian-blurred render as *higher* resolution than the sharp original (N 34 040 vs 17 292). Cause:
   it assumes a noise floor; a blurred, noise-free spectrum has none, so the cutoff lands on numerical
   noise. Quantising the control to 8 bits (as every published figure is stored) rescued the sigma-4 case
   but a blur ladder showed it still inverting at sigma 1 (ratio ~0.5). It does not measure resolution.
   **Withdrawn.** Kept in the code as `s1_s2_v1_withdrawn` for the record.
2. **Replacement S1 (v2), fixed now:** f_E = the radial frequency below which **95%** of the image's
   non-DC spectral energy lies (Hann-windowed, mean-subtracted, measured on the stored 8-bit image);
   r = 1/f_E; S2 N = area / r^2 unchanged. Controls, 8-bit: sharp vs sigma-4 blur N ratio **19.0x**;
   blur ladder sigma 1/2/4/8 gives 3.1-3.8 / 5.7-7.6 / 12.0-17.2 / 26.8-41.3x (strictly monotonic,
   5 seeds each); null 0.92x; invariant to contrast scaling (1921 vs 1940 at half contrast). **S2 passes.**
   (95% rather than 99% chosen because it is less sensitive to JPEG/compression noise in real figures.)
3. **S3 (fine-detail fraction) fails its positive control under v2.** With the 95%-energy cutoff, E_b is
   0.05 by construction, so the pre-set 5x bar requires E_a >= 0.25; a crisp CAD-like render reaches only
   0.185 (3.7x) because most image energy sits in the large shapes. The bar is **not** lowered to make it
   pass. Per D.5, **S3 and prediction P2 are not used**; E values are reported descriptively only.

Script: `src/figure_information.py` (`--controls`) -> `runs/figure_information_controls.json`.

## D.5 Controls (run before the figures, reported alongside)

- **Positive:** a synthetic sharp-edged polygon render vs the same render Gaussian-blurred (sigma 4
  px). S2 and S3 must show the sharp render carrying more samples and >= 5x the fine-detail fraction.
- **Null:** two independent blurred-noise images of equal smoothness. Neither S2 ratio may exceed
  2x, and the S3 ratio must be < 5x. If either control fails, the statistic is not used.

## D.6 Predictions (fixed now; if wrong, the wrongness is the result)

- **P1** In a majority of pairs, N(a) > N(b).
- **P2** In a majority of pairs, E_a >= 5 x E_b: the model panel carries detail finer than anything
  in the tomogram panel.
- **P3** Where S4 is computable, r(b) is coarser than the claimed 3.71 m.

*Status after D.4a:* **P1 is the primary test** (S2 passed its controls). **P2 is not used** (S3 failed its
control). Added before any figure was obtained, as a secondary effect-size bar: **P1b** — the median
N(a)/N(b) across pairs is >= 4, i.e. at least the difference a ~2-pixel blur produces in the controls.

A pair where P2 fails (the tomogram carries detail comparable to the model) is evidence *against* the
"detail comes from the model" account and will be reported as such.

## D.7 What this can and cannot show

It measures information content in published images; it cannot show intent, and it cannot show
what the authors' raw volume contained before rendering. A P2 hit shows that the published model
panel contains structure the published tomogram panel does not — i.e. the displayed geometry is not
derivable from the displayed tomogram.

## D.8 Result

*To be appended after the run. Deliberately empty at commit time.*

**Appended 27 Sep 2026.** Source: arXiv:2208.00811 (journal PDF blocked; D.2 fallback), SHA-256
906b9c64…d35c. 16 pairs (Figs 34-40, 42-50). **P1 HIT 15/16; P1b HIT (median 9.69x); P2 not used
(D.4a); P3 untestable — no tomogram panel has axes or a scale.** The single P1 miss (Fig 49) is a
heat-map composited over an engraving whose hatching carries the detail. Robust to equal median
filtering (15/16, 5.7x) and to removing panel area (tomogram 3.35x coarser). Descriptive: 4/16
tomogram panels are overlays on pre-existing drawings/photographs of the known interior; no panel is
a rendered volume. Full account: `docs/RESULTS_FIGURES_2026-09-27.md`.

**Journal-version addendum (27 Sep 2026).** The pre-registered source (journal) was obtained as images
after the fallback run. The 16 pair images are identical to arXiv v1 (r = 1.00 per panel); the
identical rule gives P1 15/16, P1b 10.47x. No axes were added. → RESULTS_FIGURES §6;
`runs/figure_information_journal.json`.
