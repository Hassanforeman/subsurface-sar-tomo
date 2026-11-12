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
**Stage-0 record (12 Nov 2026, ~12:30 Brisbane; committed before any Test P code touched a SICD; no
S-like image of any scene exists yet).**

*Sources read.* Seyfzadeh's public Facebook page (facebook.com/manu.seyfzadeh.2025), 21 posts, read in
Hassan's browser. Relevant facts, in his words where quoted:
- Data are **not public**: ICEYE Spotlight Dwell Fine, 27 Aug 2025 (24.763 s; 0.7 s used) "courtesy of
  Athanatos Foundation"; earlier work on an April 2021 Capella scene (0.7 s excerpt). Code by "OpenAI Pro
  ChatGPT, my trained agent Sage". Helpers named: Dr Edward Biegert, Rob Neyland.
- Pipeline (his "Khafre west base" post): 295 overlapping **Reference/Offset pairs** of Doppler-filtered
  images ("B-shift of ~88 Hz", "leap of 11 Hz"); co-registration 128x128 then 24x32 patch "100 x
  over-sampled"; "nearby reference patches help remove shifts shared with the surrounding scene"; convert
  to metres; depth model fitted; "we examine every possible window of 175 consecutive displacement
  vectors ... the best qualifying fit supplies the score"; ellipse-shape requirement; "With P=7, a
  positive result must belong to a run of at least seven consecutive line positions at that depth".
- Depth focus (his "Equations" and "Great Pyramid Part III" posts): a **steering matrix** of phase
  histories per depth, compared to the data "using a discrete Fourier Transform", Hermitian adjoint;
  "least-squares ... maximum adjusted R^2"; lambda re-estimated from two shafts of known depth
  (Campbell's Tomb and the shaft in Khufu's temple). This is the operator analysed in our paper s3.1-3.2.
- **His own earlier Osiris result** ("Osiris Shaft Candidate" post, Capella data, earlier version):
  "The result is partial ... Level 1 and 2 are not lighting up ... Level 3 ... possibly recognizable as a
  faint structure at about 35 meters". That post gives Tier 2 as **24 m**; the video says 22 m. Protocol
  versions named in his posts/video: 1.4 -> 1.9. The target for Test P stays 10/22/33 (the match claimed
  in the video); 10/24/33 is reported as a secondary row.
- Osiris Shaft coordinates: **29.975406 N, 31.135597 E** (German Wikipedia, "Osiris-Grab", geosearch API,
  read 12 Nov 2026). No coordinate found in OSM, Wikidata or English Wikipedia.
- Line heading 102.45 deg (the ruler shown in the video at ~56 min), position 0 at the WNW end, shaft
  at position 120.

*Amendments to P.2 (replace steps 2-6; made to follow his public description more closely, before any
image exists).* A 1024x1024 crop centred on each line. Azimuth = image columns.
- **A1 pairs.** Reference and Offset bands each half of the crop's azimuth spectrum (Hann), offset by
  2.26% of the spectrum (his 88.4 Hz of ~3.9 kHz), swept rigidly in K = 295 equal steps across the
  available spectrum. (He uses a 0.7 s excerpt; we use each Umbra scene's full aperture, 1.3-5 s.)
- **A2 displacement.** Per pair, shift of Offset relative to Reference on a 24 (az) x 32 (rg) complex
  patch, unnormalised cross-correlation, parabolic sub-pixel peak. Deviations: parabolic instead of 100x
  over-sampling (compute); the 128x128 regional step is omitted because A3 removes regional shifts.
- **A3 common mode.** Six flank patches on a 48-pixel ring (three per side, at 0 and +-45 deg from the
  azimuth axis); median per side, mean of the two sides, subtracted from the target shift.
- **A4** Pixels to metres with the SICD row/column spacing.
- **A5 windows.** Every window of 175 consecutive vectors (121 windows).
- **A6 fit.** q_n = c + u cos(theta_n) + v sin(theta_n), both components, least squares; adjusted R^2
  (6 parameters, 350 data). theta_n = 2 pi f n with f = s * z * (12/50)/175 cycles per sample: at s = 1,
  50 m is 12 cycles per window. **This constant is ours and arbitrary** (his K_z ladder is unpublished);
  the s knob spans 6-24 cycles at 50 m. Depth bins 0.5-50 m, step 0.5 m. Gate: singular-value ratio of
  [u v] > 0.1. Score = best gated window, floored at 0.
- **A7 support.** Keep only pixels with score > 0 that lie in a run of >= 8 consecutive positions at that
  depth (P = 8, the label on his Osiris plot). Order: score -> run filter -> smoothing knob -> hit rule.
- P.3 line-shift knob: each shifted line is processed as its own line (own run filter).
- **P.6 control:** the displacement is applied to the Offset image inside a 64x64-pixel tile centred on
  desert position 60: azimuth 0.5 px x cos(theta), range 0.25 px x sin(theta), summed over the three
  depths at s = 1. Flank patches that overlap the tile are a known weakness of this control.
- **N3 noise:** white complex Gaussian noise shaped by the scene crop's mean azimuth and range amplitude
  spectra, processed on the Osiris-line geometry.
- **Data handling:** 03-08 (1.7 GB) and 02-08 are cropped on the Mac to 1024x1024 complex arrays plus
  line pixel coordinates; the crop step computes no statistic. 02-07 is read directly.
P.3-P.7 otherwise unchanged. Placement check (amplitude only) is recorded below before the main run.

**Amendment A8 (12 Nov, after the synthetic selftest, before any real-scene image).** The selftest
(`--selftest`, generated speckle, no SICD) showed that the P.5 hit rule fails its own positive control:
the planted 10/22/33 m signal was plainly recovered in the image (runs/test_p_selftest.png) but scored
F = 0, because the 90th-percentile threshold is set by the bright 0-2 m band (slow drift fits) that every
image has. Options were compared **on the synthetic selftest only** (control F, p against 200 fakes on
unplanted speckle): rows >= 4 m with percentile 90: F 0.000, p 1.0; percentile 75: F 0.206, p 0.005;
percentile 50: F 0.848, p 0.005. Adopted: **threshold = 75th percentile of non-zero pixels deeper than
4 m** (the strictest option tested under which a real planted signal passes). Same rule for every
target. Busyness is reported on the same rows. Side observation from the selftest (not a result): on
pure speckle 30% of fake targets reach 3/3 under some configuration with this rule.

**Placement record (12 Nov, amplitude only: runs/test_p_placement_02-07.png, _03-08.png).**
- 02-07 and 03-08: the Osiris line lies along the dark causeway strip between the mastaba fields, shaft
  mark (position 120) on the strip: PASS. Desert line on open ground with dunes/tracks, no structures:
  PASS. No line was moved.
- 02-08 (secondary): with the test-G pixel correction the desert line falls outside the image (column
  about -180), so N2 cannot be computed. **02-08 is not run**; it was never in the verdict.
- Mac note: 03-08 was cropped on the Mac with a copy of the script (runs/_test_p_extract.py) and staged.

**Result:** *to be appended.*
