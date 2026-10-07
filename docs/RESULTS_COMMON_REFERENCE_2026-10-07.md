# Results — Test I: common-reference tracking (7 Oct 2026)

Pre-registration: docs/PREREGISTRATION_COMMON_REFERENCE_2026-10-07.md (committed 1474fd7 before the run).
Script: src/common_reference.py at 1474fd7. Output: runs/common_reference.json. Run on Hassan's Mac.

## Pre-registered verdict: **NOT TRACKABLE**
All three Giza scenes fail the trackability control: **0/24 patches** recover the planted 0.5-px shift with
either estimator (median r: NCC 0.34 / 0.43 / 0.04; phase correlation 0.63 / 0.66 / 0.57 for 02-07 / 02-08 /
03-08; the pass mark is r ≥ 0.9 in ≥ 20/24). Per the pre-registered rule, the test **cannot separate the
mechanisms**, and the v6.1 scope note ("this mechanism exists only where displacements are accumulated")
stands unchanged. Readings A and B are not evaluated.

## Why it failed (descriptive)
The common-reference tracking error is tiny next to the reference and enormous away from it, which is the
signature of decorrelated speckle seen in the synthetic speckle case:

| scene | CR error SD, looks 4 / 6 (px) | CR error SD, looks 0–3, 7–10 (px) |
|---|---|---|
| 02-07 | 0.06 / 0.06 | 0.4 – 11.4 |
| 02-08 | 0.15 / 0.21 | 5.8 – 10.6 |
| 03-08 | 0.08 / 0.06 | 11.7 – 18.4 |
| synthetic pure speckle (Part 1 design check) | 0.08 / 0.07 | 13 – 19 |

Looks more than about two steps apart share almost none of their spectrum, and the Giza centre crops do not
contain enough persistent scatterers to bridge that gap. Registration across the whole aperture is therefore
not possible on these scenes with this filter bank.

## Part 1 (synthetic, seed 20261007) — reproduced the design-phase behaviour
Random-walk expected peak 1.71 cells; white-noise curve near flat (best power inside the guard = 0.95 of the
global best). Motion-free point-scatterer scenes pinned 12% / 58% / 50% at strengths 5 / 15 / 30; planted real
shifts pinned 92% (0.1 px) and 100% (0.3 px). Common-mode medians: motion-free 0.9–2.5 (q95 ≤ 9.8), planted
0.1 px 11.6, 0.3 px 93.2. **Pinning under common-reference tracking is not diagnostic of anything by
itself**; it depends on the error structure of the tracker.

## Descriptive Giza numbers (not interpretable — tracking failed)
CR(NCC) peaks 1.75 / 3.94 / 3.79 cells; CR(phasecorr) 3.90 / 1.62 / 5.10; common-mode 1.4 / 1.9 / 0.7 (all
within the motion-free range). Adjacent-pair cumsum peaks recomputed in the same run: 1.75 / 1.67 / 1.77
(consistent with E8). Increments peaks: 1.88 / 3.83 / 1.95 (consistent with test H). These CR numbers come
from failed registrations and must not be read as evidence either way.

## What this means (interpretation, not part of the pre-registered rule)
- On these Umbra Giza scenes, the **only** way to build a look-to-look trajectory over the full aperture with
  this bank is to chain adjacent steps, i.e. to accumulate. The accumulation route our mechanism describes is
  therefore not an arbitrary choice for this data; it is the route that works at all.
- This does not tell us how the original pipeline tracks (undisclosed), and it says nothing about
  common-reference tracking on other sensors or longer dwells (e.g. ejhong's ICEYE dwell data, which we cannot
  access).
- It is consistent with Q3: the similarity between looks is carried by the filter-bank overlap; when the looks
  stop overlapping, the scene does not hold them together.
- The paper keeps the mechanism scoped to accumulation. The open limitation becomes: "a common-reference
  variant was attempted (pre-registered) but the scenes are not trackable across the aperture."
