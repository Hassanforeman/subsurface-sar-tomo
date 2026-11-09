# Tool check: what the adjacent-look tracker returns for a true 2 px shift (10 Nov 2026)

*Not a pre-registered test of the world; a check of our own instrument.* Script: `src/check_tracker_bias.py`.
Run files: `runs/tracker_bias_synthetic_speckle.json`, `runs/tracker_bias_giza_2023-02-07_UMBRA-05_SICD.json`.
Looks from the pipeline's own `decompose_subapertures_w` (overlap 0.8, Hann), one mid-aperture adjacent pair, 64-px
patches, 512 centre crop. The second look is shifted by a known amount in two ways: **real** = the whole crop is
shifted, so content crosses each patch edge (what a physical displacement does); **circular** = each 64-px patch is
Fourier-shifted on its own (how tests F, G and I plant their controls).

Median recovered shift for a true 2.00 px:

| Looks | Phase corr., synthetic | Phase corr., Giza 02-07 | NCC, synthetic | NCC, Giza 02-07 | Circular patch plant (either) |
|---|---|---|---|---|---|
| 11 | 0.17 | 0.18 | 1.86 | 1.91 | 2.00 |
| 16 | 0.09 | 0.08 | 1.76 | 1.77 | 2.00 |
| 21 | 0.06 | 0.05 | 1.68 | 1.60 | 2.00 |
| 32 | 0.02 | 0.02 | 1.41 | 1.13 | 2.00 |
| 48 | 0.01 | 0.02 | 0.93 | 0.47 | 2.00 |
| 64 | 0.01 | 0.01 | 0.32 | 0.28 | 2.00 |
| 96 | 0.00 | 0.00 | 0.20 | 0.12 | 2.00 |
| 128 | 0.00 | 0.00 | 0.16 | 0.09 | 2.00 |

Other shifts (0.25, 0.5, 1.0 px) are in the run files; 0.5 px real reads 0.05 (phase corr.) and 0.39 (NCC) at 11 looks.

## What is and is not new
- **Already known (E12, 13 Aug):** at 11 looks the front end passes about 12% of a planted sub-pixel shift
  ("attenuates … roughly eightfold", RESULTS_E12 §2 [E]); the 0.2 px floor in paper §5.6 is that attenuation. Today's
  9% at 11 looks is the same fact. I logged it this morning as a new finding before checking E12; it was not.
- **New 1, cause.** The baseline estimator is whitened phase correlation on un-windowed patches. On band-limited look
  amplitudes it has a spurious peak at zero lag that outweighs the true peak: two unrelated speckle fields return
  0 ± 0.04 px instead of a random shift. NCC does not have this peak and recovers 1.86–1.91 of 2.00 px at 11 looks.
- **New 2, look count.** The attenuation becomes total as looks narrow: phase correlation passes 4% at 16 looks, 1% at
  32, about 0 from 64. NCC falls to 60–70% at 32 looks and 4–8% at 128.
- **New 3, controls.** A circular patch-level plant is a pure linear phase in every FFT bin, so the estimator reads it
  exactly at any look count (2.00 in every row). The "planted control detected" lines of tests F, G and I therefore
  show the back end works given a displacement; they do not show the front end would have registered a physical
  one. E12's whole-crop plant is the control that does test the front end.

## What this changes
- **Not changed:** the main result (the output is reproduced from noise, peak pinned near 1.7 cells, depth scale
  chosen) and every n_sub = 11 number.
- **Wording to fix at the PCI revision (HOLD stands):** (a) §5.6 should state the ~8–11× attenuation and its cause,
  not only the 0.2 px floor; (b) the 4/4 planted-control statements in §5.3–5.5 should say the plant is a circular
  patch shift that tests the inversion, not the tracker; (c) "run at 8 sub-aperture counts (11–128)" should add that
  with this estimator the tracker cannot register real displacement from about 32 looks upward, so those runs show
  the artifact persists, not that a signal was looked for and absent.
- **Fair objection this opens:** "your tracker is deaf, so your null says nothing about my method." Answer available
  now: the method's own estimator is undisclosed; ours is stated, its sensitivity is measured and published; and the
  artifact does not need a sensitive tracker. Answer that would close it: re-run the three Giza scenes at 11 looks
  with NCC (which does register real shifts) under a new pre-registration. Candidate, not started. Caution from
  SENSITIVITY_RESPONSE: the NCC arm raised false flags on empty scenes, so it needs its own noise-matched threshold.
