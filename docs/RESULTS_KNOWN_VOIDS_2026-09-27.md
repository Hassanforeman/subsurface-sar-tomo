# Known voids do not change the output — pre-registered test G — 27 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_KNOWN_VOIDS_2026-09-27.md` (committed `4a4a57d`; placement
amendments committed `0bc7d7d` before any tomogram was built). **Script:** `src/known_voids_umbra.py`
(run at `0bc7d7d`). **Output:** `runs/known_voids_umbra.json`. Open-data analogue of ejhong/sar R13.

## 1. Primary result: NULL — the surveyed shafts are not distinguished from bare plateau

| Scene | tiles W / E / P2 | matched n | d (centroid), cemetery − plateau | d, plateau − plateau | d (band) | control | verdict |
|---|---|---|---|---|---|---|---|
| 02-07 U05 | 759 / 299 / 661 | 91 | **−0.10** | +0.12 | −0.13 | −1.86 | NULL |
| 03-08 U04 (prereg primary) | 900 / 888 / 900 | 469 | **−0.03** | −0.14 | −0.02 | −2.03 | NULL |
| 02-08 U04 (SECONDARY, corrected geolocation) | 780 / 312 / 189 | 61 | +0.30 | −0.28 | +0.28 | −1.50 | DIFFERS (not in verdict) |

Both primary scenes are NULL: the cemetery-vs-plateau difference is smaller than 0.2 and smaller than the
difference between two halves of the same empty desert. **Overall: NULL.** The positive control —
displacement planted in a quarter of the cemetery tiles before tracking — was detected in every scene
(|d| 1.5–2.0), so the test could see a real change in the input; the known voids produce none.

**Secondary scene, stated plainly:** 02-08 crosses the bar (+0.30), but its desert-vs-desert difference
is almost as large (−0.28), it has the fewest matched tiles (61; its P2 box lies largely off the image),
and its sign is opposite to the two primary scenes. It is excluded from the verdict by the rule fixed
before the run, and it reads as noise at this sample size, not a detection.

**Caveat on matching:** the cemeteries are much brighter than the desert, so brightness matching keeps
few tiles in 02-07 (91) and 02-08 (61); 03-08 (finer pixels) keeps 469. Unmatched differences are also
small (+0.04, −0.02; +0.12 secondary).

## 2. What it means
- Hundreds of excavated 5–30 m shafts — the easiest real target on the plateau — do not move the output
  of the single-pass method relative to bare rock, on free public data, with the operator unchanged.
  Independent of, and in agreement with, ejhong's ICEYE result (+0.031). A method that claims 10 m shafts
  at 648 m has to clear this first.
- It does not show "nothing is under Giza"; it shows this output does not respond to voids that are
  known to be there.

## 3. Q3 coherence diagnostic (descriptive, no rule)
Look-to-centre-look magnitude match for our 11-look bank (P2 desert crop):

| Scene | adjacent looks | 2 looks apart | ≥ 3 looks apart | look spacing |
|---|---|---|---|---|
| 02-07 | 0.59–0.65 | 0.19 | 0.10 | 0.085 s |
| 02-08 | 0.64–0.71 | 0.27 | 0.18 | 0.079 s |
| 03-08 | 0.58–0.64 | 0.16 | 0.06 | 0.336 s |
| pure synthetic speckle (selftest) | 0.55–0.61 | — | — | — |

Adjacent-look similarity on real Giza (~0.6) is about what the 80%-overlap filter bank gives for pure
speckle (~0.56); looks that share no spectrum match at the speckle floor (0.06–0.18). So each tracked
increment is carried by the filter-bank overlap, not by a coherent scene seen across the aperture; the
accumulated trajectory is accumulated registration noise. This measures, rather than infers, the step in
our mechanism (answers Grok B2 / ejhong R9 for the single-SLC method). Note: match_score is magnitude
correlation, not complex interferometric coherence.

## 4. Side finding
02-08's SICD geolocation is off by ~500 m (both cemetery boxes landed on roads; corrected by amplitude
registration to 02-07). Earlier tests used scene-centre crops, not coordinates, so they are unaffected.
