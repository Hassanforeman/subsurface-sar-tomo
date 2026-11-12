# Pre-registration P — can analyst tuning make an invented shaft "appear"? (response to "The Biondi Validation") — 12 Nov 2026

*Committed BEFORE any Test P code that touches radar data exists. At commit time only
`src/test_p_targets.py` has run; it draws random numbers and reads no data. Approved by Hassan 12 Nov
("ok go ahead. lets do this"). Background: `REVIEW_BIONDI_VALIDATION_VIDEO_2026-11-12.md`.*

## P.0 What this is, and what it is not
In the video, M. Seyfzadeh shows a depth slice beside the Osiris Shaft and reports bright patches at its
three surveyed levels (10, 22, 33 m). By his own account the target was modelled first, the depth scale
was adjusted, the filtering was increased until the image "picks them up perfectly", and the match was
drawn by hand. No negative control was shown.

**Question:** given that amount of freedom, how often does an *invented* three-level shaft "match" as
well as the real one?

**Not a replication of his code.** His pipeline ("Biondi Protocol v1.9") is not public. The repository
that held v1.7 (`github.com/BiondiProtocol/Replication-and-Verification-Biondi-Protocol`) and
`github.com/ejhong/sar` both returned 404 on 12 Nov 2026 (GitHub API: BiondiProtocol has 0 public
repositories). The pipeline below is **our reconstruction** from the labels on his plots and his spoken
description; it is called **S-like** throughout. The result therefore speaks to the *procedure*
(tuning + matching by eye on this kind of image), and must be worded that way. The fake-target list is
public so that he can run the same test on his own code; that would be the stronger test.

## P.1 Stage 0 — allowed before the run (no tomogram, no statistic)
1. **Parameter capture.** Read Seyfzadeh's public posts (he says the steps are on his Facebook page)
   and record any parameter that differs from P.2. Changes go in P.8 and are committed before the run.
2. **Placement.** Osiris Shaft coordinates from a citable source (recorded in P.8, not from memory).
   Line: 149 positions at 1 m spacing along the Khafre causeway through the shaft mouth, shaft at
   position 120 (his statement: "expected … at around pixel 120"). Amplitude-only check as in test G.3:
   the shaft position must fall on the causeway. Bare-desert line: same length and heading, centred on
   the centre of region P2 of test G (29.9600–29.9650 N, 31.1200–31.1270 E); must contain no structure
   or road, else moved by the smallest shift ≤ 300 m, recorded in P.8.
3. **Synthetic selftest** of the code on generated speckle (no SICD).
Nothing else. No S-like image of any real scene is built or viewed before the P.8 commit.

## P.2 S-like pipeline (fixed; our reading of his labels "K=295, W=175, P=8, b/a > 0.1, adjusted R²")
1. Data: the three Umbra Giza SICDs of test G. Verdict from 02-07 and 03-08; 02-08 is SECONDARY with
   the fixed pixel correction of test G (+576 rows, −420 cols).
2. Looks: K = 295 azimuth sub-apertures, Hann, overlap 0.8 (ours; his is unknown).
3. Tracking per line position: 128×128 coarse then 24 (az) × 32 (rg) patch, unnormalised
   cross-correlation, sub-pixel peak, each look against the centre look (his co-registration slide).
4. Series: mean over P = 8 adjacent patches across the line; degree-2 detrend; central W = 175 looks.
5. For each of 100 frequency bins: least-squares elliptical (sin+cos in azimuth and range) fit;
   value = adjusted R²; set to 0 where fitted axis ratio b/a ≤ 0.1.
6. Nominal depth of bin j = s × 0.5 m × j (s = 1 baseline, so the image spans 0–50 m as his does).
Image = positions × depth, values = adjusted R².

## P.3 Analyst freedom allowed (the "knobs") — deliberately narrower than what the video describes
- Depth scale s: 21 values, log-spaced 0.5–2.0 (his depth law changed; ours may stretch 2× either way).
- Filtering: box smoothing 1, 3 or 5 pixels (his three scans: raw, noisy, "more filtering").
- Line shift across-track: −4, −2, 0, +2, +4 m ("if we shift the line a tiny bit").
Grid = 21 × 3 × 5 = **315 configurations**, identical for every target. Not allowed: changing K
(he also went to 3360), mirroring the image (done in the video), moving ovals, or any change after
seeing an image.

## P.4 Targets
- **Real:** position 120, depths 10, 22, 33 m.
- **Fake:** the 200 targets in `runs/test_p_fake_targets.json` (seed 20261112; positions 10–138; three
  depths uniform in 5–40 m, ≥ 6 m apart). SHA-256 begins `2a80c71c7b3f17b0`. Force-added to git with
  this document.

## P.5 Match rule and statistics
- A level is **hit** if any pixel within ±10 positions and ±3 m of it is ≥ the 90th percentile of the
  image's non-zero pixels. (His ovals were about 20 m wide and 6 m tall.)
- Per target and configuration: hits 0–3. **F** = fraction of the 315 configurations with 3/3 hits.
  **T** = 1 if any configuration gives 3/3.
- Null families, all through the same pipeline and grid:
  - **N1 same image:** fake targets on the Osiris-line image, dropping fakes within 15 positions of 120.
    (Other real shafts lie near this line; that can only raise the fake rate, so N1 is lenient to him
    if he is wrong and harsh if he is right. Stated, not corrected.)
  - **N2 bare desert:** fake targets on the desert line.
  - **N3 noise only:** fake targets on complex Gaussian speckle with the scene's spectral support.
- p_N = (1 + number of fakes with F ≥ F_real) / (number of fakes + 1), for N1 and N2. N3 is descriptive.
- **Headline descriptive numbers (reported whatever the verdict):** share of fake targets with T = 1 in
  N1, N2, N3; share of image area above the hit threshold ("busyness").

## P.6 Positive control
On the desert line at position 60: an elliptical displacement (0.5 px, as tests F/G) at the three
frequencies that map to 10, 22, 33 m at s = 1 is applied to the looks before tracking, within ±10
positions. Control passes if its p_N2 ≤ 0.05. If it fails, that scene is **INCONCLUSIVE** (our S-like
tracker could not see a real input; cf. RESULTS_TRACKER_BIAS_2026-11-10).

## P.7 Decision rule and wording
Per scene (control passed): **STANDS OUT** iff p_N1 ≤ 0.05 and p_N2 ≤ 0.05. **NOT DISTINGUISHED** iff
p_N1 > 0.20 and p_N2 > 0.20. Otherwise **MIXED**. Overall from 02-07 and 03-08: STANDS OUT or NOT
DISTINGUISHED iff both agree; else MIXED/INCONCLUSIVE.
- **NOT DISTINGUISHED** means: with our reconstruction and less freedom than the video describes, the
  real shaft matches no better than invented ones. It does not prove his image is an artifact, and it
  does not show that nothing is under Giza.
- **STANDS OUT** means: the real shaft matches better than invented ones beyond tuning. We report it
  publicly, tell Seyfzadeh, and then look for a surface cause (the shaft mouth and causeway are visible
  structures) before any subsurface reading, as in test G.6.
- Either way the full table is published, including the outcome least favourable to our paper.
- Effect of the known open residual (falsification (ii) met on 2/3 scenes, STATE §0) is not addressed
  by this test.

## P.8 Stage-0 record, amendments and result
*To be appended. Deliberately empty at commit time.*
