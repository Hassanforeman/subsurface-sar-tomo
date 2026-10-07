# Pre-registration — Test I: common-reference tracking (7 Oct 2026)

Status: **registered before any common-reference result on Giza data was computed.** Script:
`src/common_reference.py` (selftest passes in the sandbox). Output: `runs/common_reference.json`.
Origin: hostile-panel review 1a (docs/private/TRIAGE_HOSTILE_PANEL_2026-10-07.md) — our 1.68-cell mechanism
was derived for adjacent-pair accumulation (`np.cumsum`); is the shallow peak specific to that, or does it
appear without a running total?

## Design
Identical to E8 / test H except the tracker. 512 centre crop, patch 64, 24 patches on the centre row,
n_sub 11, overlap 0.8, Hann, degree-2 detrend, 300 depth bins, guard 2 cells, depth axis as E8.

- **Common-reference (CR) trajectory:** each look k is registered directly to the centre look (index 5);
  t_5 = 0; no cumulative sum.
- **Primary estimator:** normalised cross-correlation + parabolic refine (`est_ncc_parabolic`).
  **Secondary (descriptive):** the pipeline's phase correlation (`est_phasecorr_parabolic`).
- **Trackability control (per scene):** plant a 2-cycle, 0.5-px sinusoidal azimuth shift in every patch's looks;
  the scene is TRACKABLE if the CR trajectory correlates r ≥ 0.9 with the planted shift in ≥ 20/24 patches.
- **Common-mode statistic:** 24·‖patch-mean trajectory‖² / Σ per-look variance (≈1 when patches share nothing).

### Part 1 — synthetic (fixed seed 20261007)
Analytic expected depth curves for random-walk and white trajectory noise; CR on 50 pure-speckle images
(untrackable case); CR on 50 motion-free scenes (speckle + 3 persistent point scatterers per patch) at each of
three scatterer strengths (5, 15, 30); CR on 25 scenes (strength 15) with a planted genuine smooth shift of
0.1 and 0.3 px (1.5 cycles).

### Part 2 — Giza (the three Umbra scenes)
Per scene: trackability control (both estimators), CR peak and common-mode, plus the adjacent-pair (cumsum)
and increments peaks recomputed in the same run for side-by-side reference.

## Pre-stated decision rules (`verdict()` in the script)
- **NOT TRACKABLE** if fewer than 2 scenes pass the control. Then the test cannot separate the mechanisms
  and we say so; the v6.1 abstract scope ("in this reconstruction") stands unchanged.
- Otherwise, on trackable scenes:
  - **A = PIN WITHOUT ACCUMULATION** if ≥ 2 pin (peak ≤ 2 cells) → the shallow peak is not specific to the
    running total; the paper may say the pin arises from the tracking-error structure generally.
    **A = ACCUMULATION-DEPENDENT** if ≤ 1 pins → the pin in our pipeline depends on accumulation; scope stays.
  - **B = COMMON SHIFT PRESENT** if ≥ 2 trackable scenes exceed the largest motion-free null 95th percentile
    of the common-mode statistic → a scene-wide look-dependent shift exists. Cause unknown (platform/focusing
    residuals and real surface motion are candidates). A scene-wide shift is **not** a subsurface indicator.
    Otherwise **B = NO COMMON SHIFT** beyond motion-free tracking noise.
- Detections of buried structure: none expected and none will be claimed from this test.

## Disclosed before registration (design-phase synthetic checks — they shaped the design)
1. **Pure speckle cannot be tracked across the aperture by any of our estimators.** Looks more than ~2 apart
   share almost no spectrum (|look| correlation with the centre look: 0.02, 0.02, 0.00, 0.10, 0.58, 1, 0.56,
   0.10, 0.00, 0.03, 0.01). Hence the per-scene control.
2. **The pipeline's phase-correlation estimator failed the control even on persistent point scatterers**
   (2/24 patches); NCC passed (22/24). Hence NCC as primary. This is a choice made after seeing synthetic
   behaviour, not Giza behaviour.
3. **Pinning under CR is not diagnostic on its own.** In the selftest, motion-free scenes pinned 0%, 100% and
   38% at scatterer strengths 5, 15, 30, and planted genuine shifts pinned 100%. The expected-power formula
   (`derive_depth_constant`) with a general covariance shows why: any trajectory-error covariance with
   low-order structure (e.g. error variance growing with distance from the reference) produces a shallow
   argmax, as does a real smooth shift. White noise gives no strongly preferred location. Hence reading B.
4. The analytic random-walk peak at n = 11 is 1.71 cells (1.68 asymptotically) — reproduced by the script.

We have seen whole-scene adjacent-pair results on all three Giza scenes before (E8, test H). No
common-reference statistic has been computed on Giza data.

## What each outcome would change in the paper
- A = PIN WITHOUT ACCUMULATION → §4.2 gains one paragraph: the shallow peak also appears with common-reference
  tracking, so ejhong's common-reference route and ours share it; abstract wording can drop the
  "adjacent-pair" restriction for the *pin* (not for the 1.68 constant, which is accumulation-specific).
- A = ACCUMULATION-DEPENDENT → §4.2 states the pin is a property of accumulation; common-reference routes need
  separate analysis; the scope note stays.
- B = COMMON SHIFT PRESENT → reported as an unexplained scene-wide effect, with candidate causes; no
  subsurface reading.
- NOT TRACKABLE → reported as a limitation: with this bank, Giza cannot be registered across the aperture,
  which is itself why adjacent-pair accumulation is the practical route.

Run on Hassan's Mac: `python3.13 src/common_reference.py` (estimated 10–20 min).
