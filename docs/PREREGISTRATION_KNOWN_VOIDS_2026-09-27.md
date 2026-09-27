# Pre-registration G — do known 5–30 m voids change the tomogram? (Giza cemeteries vs bare plateau) — 27 Sep 2026

*Committed BEFORE `src/known_voids_umbra.py` is run on any SICD. Only the synthetic selftest has run
(empty vs empty d = +0.003; planted vs empty d = −1.63). Open-data analogue of ejhong/sar R13; design
points from the Grok triage (GROK_TRIAGE_EJHONG, B4). Source for the idea: COMPARISON_EJHONG §6 Q1.*

## G.1 Question
The Western and Eastern Cemeteries hold hundreds of excavated mastaba shafts 5–30 m deep, next to bare
plateau. A method that claims 10 m shafts at 648 m must at least distinguish these. Does our unchanged
pipeline (the patent operator) produce a different depth output over the cemeteries than over bare
plateau in the same acquisition?

## G.2 Data, regions, pipeline (fixed now)
- The three Umbra Giza SICDs (all three footprints contain both cemeteries; checked from SICD
  ImageCorners). Pipeline identical to C.4 / test F: 768 crops, n_sub 11, overlap 0.8, Hann, patch 64,
  stride 24, degree-2 detrend, 300 bins, DFT. Nothing re-tuned.
- Regions (lat_min, lat_max, lon_min, lon_max), from published maps of the plateau, fixed before any
  crop is viewed:
  - W_cemetery 29.9785–29.9830 N, 31.1255–31.1320 E (target)
  - E_cemetery 29.9770–29.9805 N, 31.1365–31.1395 E (target)
  - P1_plateau 29.9700–29.9750 N, 31.1100–31.1170 E (control, open desert W of Menkaure)
  - P2_plateau 29.9600–29.9650 N, 31.1200–31.1270 E (control, open desert S of Menkaure)
- For each region: a 768 crop centred on the region centre (projected with sarpy ground_to_image_geo at
  the SCP height); tiles whose centre (image_to_ground_geo) falls inside the box are that region's tiles.

## G.3 Placement check (the only look allowed before the run)
`--placement` writes SLC-amplitude crops with the boxes drawn — no tomogram is built. Rule: the target
boxes must visibly contain rows of mastabas; the control boxes must contain no built structures, roads
or known tombs. If a box fails, it is moved by the smallest shift (≤ 300 m) that satisfies the rule, the
new coordinates are recorded in G.7 with the reason, and committed before the main run. Amplitude only;
no statistic is computed at this stage.

## G.4 Statistics and rule
Per tile: normalised depth profile P(z) = V(z)/ΣV. c = depth centroid Σ z·P (primary); f = fraction of P
in the 5–30 axis-unit band (ejhong's statistic; secondary — note that on our axis this band contains the
surface pin at ~1.7 cells, so f is reported for comparability, not as the rule).
- Brightness matching: tiles binned by pooled log-mean-|SLC| deciles; equal counts drawn per bin (seed 0).
- d = standardised difference (Cohen's d) of c, cemetery tiles (W+E) minus plateau tiles (P1+P2),
  brightness-matched. Reference: d_PP = P1 vs P2, same procedure.
- Per scene: **DIFFERS** iff |d| ≥ 0.2 AND |d| > |d_PP|; else **NULL**. INCONCLUSIVE if the positive
  control fails or any region has < 20 tiles.
- Overall: **KNOWN VOIDS DETECTED** iff ≥ 2 of 3 scenes DIFFER with the same sign; **NULL** iff ≥ 2 of 3
  are NULL; otherwise MIXED/INCONCLUSIVE. Effect-size thresholds, not p-values (tiles overlap).
- Also reported (not in the rule): d without brightness matching; tile counts; ejhong-style band d.

## G.5 Positive control (in displacement, before tracking)
In each cemetery crop, 25% of the in-box tiles (seed 11) get the test-F sinusoidal azimuth shift (0.5 px,
2 cycles over 11 looks) applied to their looks before tracking. Control passes if |d(planted cemetery
tiles vs plateau)| ≥ 0.2. Selftest: −1.63.

## G.6 What each outcome means
- NULL: known, surveyed, shallow voids do not move the output relative to bare rock — the minimum a
  deep-void claim must clear. It is not "nothing is under Giza".
- DETECTED: the output differs over cemeteries. That starts a search for a surface cause (mastaba
  superstructures, brightness, layover) before any subsurface reading; it would be reported as such.
- The C.4 and F results stand either way.

## G.8 Q3 coherence diagnostic (descriptive, same run, no rule)
On the P1 crop of each scene: look-to-centre-look and adjacent-look match scores for our 11-look bank,
with look spacing in seconds from the product. Reported to answer whether our increments are
decorrelation-limited (Grok B2 / ejhong R9).

## G.7 Placement record and result
*To be appended. Deliberately empty at commit time.*

**Placement record (27 Sep 2026, amplitude only — no tomogram had been built; recorded and committed
before the main run).** First `--placement` run (runs/known_voids_placement_*.png):
- 02-07 and 03-08: W and E cemetery boxes land on rows of mastabas — PASS. P2 lands on open desert with
  dunes/tracks — PASS. **P1 FAILS** in both: it contains a built compound with a road.
- **02-08 FAILS as a scene:** both cemetery boxes land on roads/highway. Its SICD geolocation disagrees
  with 02-07 by ~500 m: registering 02-08 amplitude to 02-07 over the pyramid area gives correlation 0.50
  at the offset vs −0.02 at zero (city NE 0.17, E cemetery 0.45 at the same offset).

Amendments (the G.3 rule — "shift ≤ 300 m" — did not anticipate these, so they are stated here):
1. **P1 is dropped** rather than relocated by judgment. The only control is P2; the plateau-vs-plateau
   reference d_PP becomes P2's northern half vs its southern half (split at the median tile latitude).
2. **02-08 becomes SECONDARY:** run with a fixed pixel correction (+576 rows, −420 cols, from the
   amplitude registration above) and reported, but **not in the verdict**. The verdict uses 02-07 and
   03-08 only: KNOWN VOIDS DETECTED iff both DIFFER with the same sign; NULL iff both are NULL; else MIXED.
3. Tiles with mean |SLC| < 1% of their crop's median (image-edge no-data) are excluded.
A second `--placement` run must show the corrected 02-08 cemetery boxes on mastaba rows; if not, 02-08
is dropped entirely. All other G.2–G.6 choices unchanged.

**Second placement check (after commit `0bc7d7d`, still no tomogram):** corrected 02-08 W and E boxes now
land on mastaba rows matching 02-07 — correction ACCEPTED; 02-08 stays SECONDARY. 02-08's P2 box lies
largely outside the image edge, so its tile count may fall below 20 (→ INCONCLUSIVE for that secondary
scene, by the existing rule).

**Result (appended 27 Sep 2026, run at `0bc7d7d`).** d(centroid) cemetery − plateau: 02-07 −0.10 (plateau
halves +0.12), 03-08 −0.03 (−0.14) → both NULL; control detected in all scenes (−1.86, −2.03; secondary
−1.50). **Overall: NULL.** Secondary 02-08: +0.30 vs plateau halves −0.28, 61 matched tiles → DIFFERS but
excluded by rule. → `docs/RESULTS_KNOWN_VOIDS_2026-09-27.md`; `runs/known_voids_umbra.json`.
