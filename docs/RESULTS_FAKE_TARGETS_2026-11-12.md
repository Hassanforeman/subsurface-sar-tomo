# Test P result — the real shaft is not distinguished from invented ones — 12 Nov 2026

**Pre-registration:** `docs/PREREGISTRATION_FAKE_TARGETS_2026-11-12.md` (rules `e55bbc5`; Stage-0 amendments
`048a2fe`; A8 + code `0693399`; placement `f3036d6`; all pushed before the main run finished).
**Script:** `src/test_p_fake_targets.py`. **Outputs:** `runs/test_p_02-07.json`, `runs/test_p_03-08.json`,
`runs/test_p_*.png`, `runs/test_p_posthoc_maxhits.json`. Fake targets: `runs/test_p_fake_targets.json`.

**Scope, first:** the pipeline is our reconstruction ("S-like") of M. Seyfzadeh's publicly described steps,
run on our free Umbra scenes. His code (v1.9) and his ICEYE scene are not public. This is a test of the
procedure, not of his software or his data.

## 1. Result (pre-registered)

| Scene | Control (planted 10/22/33 m) | Real shaft: configs with 3/3 (of 315) | Fakes reaching 3/3 in some config: same image / desert / noise | p_N1 | p_N2 | Verdict |
|---|---|---|---|---|---|---|
| 02-07 U05 | F 0.181, p 0.005 — PASS | **0** | 12% / 15% / 24% | 1.0 | 1.0 | NOT DISTINGUISHED |
| 03-08 U04 | F 0.260, p 0.005 — PASS | **0** | 6% / 6% / 4.5% | 1.0 | 1.0 | NOT DISTINGUISHED |

**Overall: NOT DISTINGUISHED.** 02-08 was not run (desert line outside its footprint; never in the verdict).
The secondary target 10/24/33 m (the depths in his own earlier post) also scored 0 in both scenes.

- The planted signal was recovered in both scenes, so the pipeline could see a real three-level signal.
- The real Osiris Shaft never produced a three-level match in any of the 315 allowed configurations.
- Invented shafts did: 6-15% of them on real images, 4.5-24% on pure noise.
- Busyness (share of image above threshold, rows deeper than 4 m): Osiris line 6.2% / 8.0%, desert 6.9% /
  7.7%, noise 5.8% / 8.1%. The three kinds of image are equally busy.
- The Osiris line, bare desert and pure noise images look alike (runs/test_p_02-07.png, _03-08.png): a
  bright 0-6 m band and scattered patches to about 15 m.

## 2. Post hoc, descriptive only (not in the rule)
Best number of levels hit under tuning: real shaft 2 of 3 in both scenes. Fakes with >= 2 of 3: 83% / 75%
(same image), 82% / 74% (desert), 90% / 67% (noise). A two-level "partial match" is the typical outcome
for an invented target.

## 3. What this does and does not show
- With less analyst freedom than the video describes, a three-level "match" can be produced for a
  meaningful minority of invented shafts, on empty desert and on noise. Tuning plus matching by eye is
  therefore not evidence by itself.
- In our hands the real shaft does **not** appear. We did not reproduce his image. That is a failure to
  replicate with different data and code, not a demonstration that his image is an artifact.
- It does not show that nothing is under Giza, and it does not address the open residual in our own
  paper (falsification (ii) met on 2/3 scenes).

## 4. Limits
- Our depth constant (12 cycles per window at 50 m) is arbitrary; the s knob covers 0.5-2x.
- Umbra (1.3 s and 5 s apertures, 0.2-0.8 m pixels) vs his ICEYE dwell scene (0.7 s of 24.8 s).
- Parabolic sub-pixel registration instead of 100x over-sampling; our own common-mode scheme.
- Hit threshold (A8) was set on a synthetic selftest after the original rule failed its control.
- N1 is contaminated by other real shafts near the causeway line (stated in P.5).
- The fake-target list is public: the stronger test is for him to run it on his own pipeline and data.

## 5. Post hoc: do the patches repeat between two passes over the same ground? (12 Nov, descriptive)
> ⚠️ WEAKENED 12 Nov 14:00 by Test Q (PREREGISTRATION_REPEAT_PASS_2026-11-12.md): the same comparison statistic
> failed to detect a planted repeating signal, twice. The near-zero correlations below therefore do NOT
> show that the patches fail to repeat; the statistic may simply be blind. Do not cite this section.
`runs/test_p_posthoc_repeat_pass.json`. Test P score maps (untuned pipeline), rows deeper than 4 m, 3-pixel
smoothing, per-depth mean removed, at depth scales 0.5 / 1 / 2. Correlation of the shaft-line image from the
7 Feb pass with the same line from the 8 Mar pass: **0.10 / -0.03 / -0.05**. For comparison, pairs that
share no ground: shaft (Feb) vs desert (Mar) 0.13 / 0.17 / 0.30; shaft (Feb) vs noise 0.41 / 0.50 / 0.24;
desert Feb vs Mar 0.31 / 0.32 / 0.38. Same pass with the line moved 2 m: -0.12 / -0.19 / -0.11. The patch
pattern over the shaft does not repeat from one pass to the next; unrelated pairs correlate as much or
more (residual shared depth structure sets a baseline of roughly 0.1-0.5). Limits: two passes only,
different satellites and resolutions (0.47x0.83 m vs 0.23x0.21 m), not pre-registered.
