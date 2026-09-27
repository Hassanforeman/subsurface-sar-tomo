# Pre-registration F — "vertical streaks are surface-driven" + the 02-08 near-miss split — 27 Sep 2026

*Committed BEFORE `src/streak_surface.py` is run on any SICD. Only the synthetic selftest (speckle, no
scene) has been run; it was used to fix the control amplitude and nothing else.*

## F.1 Why
The 2026 press audit (RESULTS_PRESS_IMAGES_2026-09-27.md) showed the measured product is still a 2-D
range x depth heat-map whose most prominent features are vertical streaks — the "shafts". A column of
the tomogram is the power spectrum of one tile's detrended trajectory, so a bright column is, by
construction, a tile whose trajectory has high variance (identity check E below). The open question is
**what makes a tile's trajectory large**: surface/measurement properties (registration quality,
backscatter brightness) or something not visible at the surface. The same question is the open
02-08 near-miss item (STATE §3), so both are tested here, once.

## F.2 Data and pipeline (unchanged, nothing re-tuned)
Three Umbra Giza SICDs; the same 768 x 768 centre crops as C.4 step 1; the identical volume build
(n_sub 11, overlap 0.8, Hann, complex128, patch 64, stride 24 → 30 x 30 tiles, degree-2 detrend, 300
depth bins, DFT/Bartlett). Null: the same seed-0, bw 0.80 empty volume.

## F.3 Primary statistics and rule
Per tile i: S_i = mean of the tile's 300-bin column (streak strength); Q_i = mean look-pair match score
(registration quality, `match_score`); M_i = mean |SLC| over the tile's patch (surface brightness).
Reported, not in the rule: K_i = std/mean |SLC| (texture); E_i = variance of the detrended trajectory
(identity check; expected rho(S,E) ≈ 1).
- A scene is **SURFACE-LINKED** iff |Spearman(S,Q)| ≥ 0.3 or |Spearman(S,M)| ≥ 0.3. The threshold is an
  effect size, not a p-value (tiles overlap, so p-values would be inflated).
- **H-surface SUPPORTED** if 03-08 (the pre-registered primary scene) and ≥ 2 of 3 scenes are linked;
  **REJECTED** if 03-08 and ≥ 2 of 3 are not linked; otherwise **MIXED**.
- The null volume's rho values are reported as the no-scene reference. (Selftest, already run:
  rho(S,Q) +0.01, rho(S,M) −0.02 — in pure speckle, streak strength is NOT linked to Q or M.)
- A REJECTED outcome means the streaks are not explained by these surface/measurement properties.
  It is **not** evidence of buried structure; it would leave the streaks unexplained.

## F.4 Positive control (in displacement, before tracking — answers the "painted into the volume" gap)
Four tiles (seed 11, away from edges) get a sinusoidal azimuth shift applied to their look patches
before tracking: 2 cycles over the 11 looks, amplitude 0.5 px. Passes if ≥ 3 of 4 planted tiles rank in
the top 10% of S. A failed control makes that scene INCONCLUSIVE.
Amplitude fixed from the synthetic selftest only: planted tiles in top 10% = 2/4 at 0.05 px, 4/4 at
0.1, 0.2 and 0.5 px. 0.5 px chosen (above the ~0.2 px planted-signal floor already on record).

## F.5 Near-miss split (02-08)
- N1 = max(|Spearman(F,M)|, |Spearman(F,Q)|), F_i = fraction of tile i's column above the raw volume's
  99th percentile (the shape metric's mask).
- N2 = median over the 8 included treatments of the shape metric's `elong` (vertical extent / horizontal
  extent of components), for 02-08, the two other scenes, and 02-08 with painted shafts (reference).
- **CLOSED-AS-SURFACE** if N1 ≥ 0.3 and N2(02-08) ≤ 1.5 x max(N2 of the other two scenes).
  **NEGATIVE WEAKENED** if N1 < 0.3 and N2(02-08) > 1.5 x max(others). Otherwise **MIXED** — reported
  as mixed, with no explanatory story added.

## F.6 Cannot change
The C.4 step-1 verdict (0/8, 4/8, 0/8) stands whatever happens here. No threshold in this document is
changed after the run; failures are reported as failures.

## F.7 Result
*To be appended after the run. Deliberately empty at commit time.*
