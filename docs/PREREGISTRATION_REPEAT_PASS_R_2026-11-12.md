# Pre-registration R — repeat-pass consistency, corrected design (Giza x3, Bingham x5) — 12 Nov 2026

*Successor to Test Q, which was INCONCLUSIVE because its control could not pass (PREREGISTRATION_REPEAT_PASS_2026-11-12.md).
Committed before `src/test_r_repeat_pass.py` exists. Approved by Hassan ("go ahead with the last two").*

## R.0 Gate: synthetic selftest first
No real scene is processed until `--selftest` passes on generated speckle: three synthetic "passes", six
lines each with independent speckle, plus a control line carrying the planted signal of R.3.
Pass condition: the control's cross-pass correlation exceeds the 95th percentile of the different-line
correlations in at least 2 of 3 pairs, **and** the unplanted lines give no effect (permutation p > 0.05 in
at least 2 of 3 pairs). If the selftest fails, the design is changed and re-tested on synthetic data
only, every change is recorded in R.6, and real data stay untouched until it passes.

## R.1 Question, pipeline, statistic
As Q.1 and Q.3 (Test P's S-like pipeline; primary image s = 1, rows deeper than 4 m; secondary =
look-alike settings). Statistic for two images: Pearson correlation after 3-pixel smoothing and removal
of each depth row's mean. Effect = mean same-line correlation minus mean different-line correlation;
p by 5,000 relabellings.

## R.2 Data
- **Giza x3** (Feb7, Feb8, Mar8): the 16 lines and crops of Test Q, unchanged. **Disclosure: their
  same-line and different-line correlations are already known** (Q.6: effect +0.103 p 0.014; -0.020 p
  0.675; -0.129 p 0.998). Only the control is new. The Giza verdict is therefore labelled "unblinded".
- **Bingham Canyon mine x5** (Umbra 2024-01-11, 01-12, 02-26, 03-11, 05-08): never processed with this
  pipeline; this is the blind application. Look directions differ by up to 60 deg and the pit is deep,
  so lines are placed by image matching, not by the scene-centre height:
  1. 16 candidate line centres on a 4 x 4 grid, 300 m spacing, centred on the scene centre.
  2. For each centre and pass, a 256 x 256 m amplitude chip at 1 m posting is geocoded at the
     scene-centre height; the chip of each pass is cross-correlated (log-amplitude, mean removed) with
     the 2024-01-12 chip; the peak gives that pass's ground offset, applied to the line.
  3. A line is kept only if, in all four non-reference passes, the normalised correlation peak is
     >= 0.15 and the offset is <= 60 m. At least 8 lines must remain, else Bingham is INCONCLUSIVE.
  Amplitude and geometry only; no S-like image is built or viewed in this step.

## R.3 Positive control (changed from Q)
On the first usable line of each site, in every pass, three **localised** signals are planted before
tracking: positions 22-38 at 12 m, 67-83 at 22 m, 112-128 at 33 m (0.5 px azimuth cosine, 0.25 px range
sine, at the frequency of that depth for s = 1), each inside a box around those positions' pixel path
(16-pixel margin). Localised in position, so the row-mean removal cannot erase them. Control passes if
its cross-pass correlation exceeds the 95th percentile of different-line correlations in at least
two-thirds of the pass pairs (2 of 3 for Giza, 7 of 10 for Bingham); else that site is INCONCLUSIVE.

## R.4 Decision (per site, primary image)
REPEATS iff p <= 0.05 and effect > 0 in at least two-thirds of pairs. DOES NOT REPEAT iff p > 0.20 in at
least two-thirds of pairs. Otherwise MIXED. Secondary image reported, not in the verdict.

## R.5 Reading
As Q.5. In addition: Bingham is an open pit with haul roads and benches; a REPEATS result there would
most likely be surface relief, and DOES NOT REPEAT there says nothing about Giza.

## R.6 Selftest record, amendments and results
**Bingham placement, first attempt (12 Nov ~14:40; amplitude only, no S-like image exists for Bingham):**
with single-pixel chips at 1 m posting, correlation peaks against the 2024-01-12 pass were 0.02-0.15 with
scattered offsets; no line met R.2 step 3 in any pass. **Amendment R-a (before any Bingham image):** chips
are smoothed with a 7 x 7 m box (speckle reduction) before matching; thresholds unchanged. One retry
only. If fewer than 8 lines survive, Bingham is INCONCLUSIVE and is not processed.

**Bingham placement, retry with R-a (14:45):** peaks rose to 0.10-0.57 but offsets scatter up to 167 m.
Lines passing R.2 step 3: 01-11 six, 02-26 six, 03-11 four, 05-08 five; **none passes in all four**.
Fewer than 8 lines: **Bingham is INCONCLUSIVE and is not processed.** Cause: pit relief plus look directions
57-118 deg; a terrain model is needed. Placement files stay on the Mac (runs/r_bing_*.npz).

**Selftest gate (14:35): FAIL.** runs/test_r_selftest.json. Null behaviour correct (unplanted lines:
p 0.20 / 0.24 / 0.78), but the planted control exceeded the different-line 95th percentile in 0 of 3 pairs
on the primary image (2 of 3 on the secondary). The statistic is not sensitive to the standard 0.5-pixel
plant. **No real scene has been processed under Test R.** Next (synthetic only): a power simulation with
plants at 1x, 2x and 4x the standard size and alternative statistics, to find what repeat signal the
comparison can detect (src/test_r_repeat_pass.py --power).

*Further records to be appended.*
