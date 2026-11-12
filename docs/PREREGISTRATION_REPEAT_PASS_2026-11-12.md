# Pre-registration Q — does the patch pattern repeat between passes over the same ground? (Giza, 3 Umbra passes) — 12 Nov 2026

*Committed before `src/test_q_repeat_pass.py` exists. Asked for by Hassan ("show that multiple scans of the
same thing can have completely different data").*

**Disclosure (already seen):** a post-hoc look at one line (the Osiris-shaft line, 7 Feb vs 8 Mar) gave
correlations of 0.10 / -0.03 / -0.05 (RESULTS_FAKE_TARGETS s5). That line is excluded from Test Q.

## Q.1 Question
A subsurface structure does not move between satellite passes. If the S-like image shows structure, the
image of a ground line on one pass should resemble the image of the same line on another pass more than
it resembles the image of a different line.

## Q.2 Data and lines (fixed now)
- Passes: Umbra Giza 2023-02-07 (U05), 2023-02-08 (U04, with the test-G pixel correction +576 rows,
  -420 cols), 2023-03-08 (U04). Look directions within 2 deg; incidence 37 / 29 / 35 deg.
- 16 ground lines: a 4 x 4 grid of line centres, 200 m spacing east and north, grid centre 29.9760 N,
  31.1312 E; each line 149 positions at 1 m, heading 102.45 deg (as Test P). A line is dropped (in all
  passes) if in any pass its patches fall outside the image or on no-data; at least 10 lines must
  remain or the test is INCONCLUSIVE. Geometry check only; no image is viewed.
- Projection uses the scene-centre height; the plateau's relief (tens of metres) can misplace a line by
  some metres between passes of different incidence. Stated limit, not corrected.

## Q.3 Pipeline (frozen)
Test P's S-like pipeline (P.8 amendments A1-A7), one line per 1024 x 1024 crop, no line-shift knob.
- **Primary image:** s = 1, no smoothing, depth rows deeper than 4 m.
- **Secondary image ("look-alike" settings, fixed from the exploration):** high-pass 15 on the series,
  s = 1.24, frequency offset 3.0, run length 3, floor 0.02, smoothing 3.
Comparison statistic for two images: Pearson correlation after 3-pixel smoothing and removal of each
depth row's mean.

## Q.4 Test
For each pass pair (Feb7-Feb8, Feb7-Mar8, Feb8-Mar8): S = mean correlation over lines of (line i in pass A,
line i in pass B); D = mean over all i != j of (line i in A, line j in B). Effect = S - D. p = share of
5,000 random relabellings of the lines in pass B with effect >= observed (plus-one rule).
- **Positive control:** line 0 is processed a second time in every pass with the Test P planted signal
  (P.6) at position 60. Its cross-pass correlation must exceed the 95th percentile of the different-line
  correlations in at least 2 of 3 pairs, else INCONCLUSIVE.
- **REPEATS** iff p <= 0.05 and effect > 0 in at least 2 of 3 pairs. **DOES NOT REPEAT** iff p > 0.20 in at
  least 2 of 3 pairs. Otherwise MIXED. Reported for primary and secondary images; verdict from primary.

## Q.5 Reading
- DOES NOT REPEAT: the patches are not tied to the ground in our reconstruction. Not a statement about
  his code or data.
- REPEATS: something tied to the ground drives the image. Surface structures (walls, mastabas, relief)
  are the first candidates, because tracking depends on image brightness; a surface-vs-subsurface check
  would be needed before any underground reading. Reported either way.

## Q.6 Record and result
*To be appended.*
