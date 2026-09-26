# §7 shape metric on the real Giza volumes — pre-registered step 1 (C.4) — 26 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_MINES_AND_GRANSASSO.md` Part C (rule fixed 16 Aug 2026,
calibration `runs/shape_metric.json`). Analysis choices the pre-registration left open (crop,
scenes, aggregation, in-data positive control, secondary checks) were fixed in
`src/shape_metric_giza.py` and **committed and pushed as `ec411e3` before any Giza volume was built
or scored.** Script: `src/shape_metric_giza.py`. Output: `runs/shape_metric_giza.json`
(figure `runs/shape_metric_giza.png`, not committed — `runs/*.png` is gitignored).

Stated prediction before the run (assistant, in session): all three scenes "not architecture-like",
controls passing.

## 1. Primary result (pre-registered rule)

Real volume = 768 x 768 centre crop, pipeline identical to the calibration volume (n_sub 11, overlap
0.8, Hann, patch 64, stride 24 -> 30x30 tiles, degree-2 detrend, 300 depth bins, DFT inversion).
Null = the calibration's empty volume (band-limited speckle, bw 0.80, seed 0), identical pipeline.
Rule per treatment: vrun_real > 1.5x vrun_null OR ncomp_real < 0.5x ncomp_null (top 1% of voxels),
over the 8 treatments not excluded in C.3. Scene is architecture-like if >= 5/8 fire. Positive
control: the same real volume with the calibration's 4 planted shafts must fire >= 5/8.

| Scene | Rule fires | Planted-shaft control | Verdict |
|---|---|---|---|
| giza_2023-02-07_UMBRA-05 | 0/8 | 8/8 | NOT architecture-like |
| giza_2023-02-08_UMBRA-04 | **4/8** | 8/8 | NOT architecture-like (near-miss, §3) |
| giza_2023-03-08_UMBRA-04 (pre-registered primary scene) | **0/8** | 8/8 | NOT architecture-like |

**C.4 step 1 outcome: negative.** No real Giza volume is architecture-like under the pre-registered
rule; the rule demonstrably can detect shafts in each real volume (8/8 positive controls).

## 2. Secondary checks (not pre-registered; cannot overturn §1)

| Scene | vs null seeds 0-4 | vs spectrally matched null | 4 off-centre crops (control) |
|---|---|---|---|
| 02-07 U05 | 0,0,0,0,0 | 0/8 (bw 0.80) | 0, 4, 1, 0 (all 8/8) |
| 02-08 U04 | 4,4,4,4,4 | 4/8 (bw 0.78) | 0, 0, 0, 0 (all 8/8) |
| 03-08 U04 | 0,0,0,0,0 | 0/8 (bw 0.80) | 0, 0, 0, 2 (all 8/8) |

Across all 15 real crops, **0 reach the 5/8 threshold**; 2 reach 4/8; 13 are at 0-2. Positive
controls fire 8/8 on all 15. The counts are identical across five independent null seeds, so they
are properties of the real crops, not of null-volume luck. (For reference, an independent empty
volume scored against the seed-0 null fires 0/8 in the script's `--selftest`.)

## 3. The near-miss (02-08 centre crop, 4/8) — reported, not explained

| Treatment | vrun real/null | ratio | ncomp real/null | ratio | fires |
|---|---|---|---|---|---|
| depth gain z^2 | 33/24 | 1.37 | 35/93 | 2.66 | yes (ncomp) |
| z-blur | 50/28 | **1.80** | 10/21 | 2.10 | yes (both) |
| common-mode + gain z^2 | 33/26 | 1.27 | 35/88 | 2.51 | yes (ncomp) |
| gain z^4 + z-blur + gamma | 34/24 | 1.42 | 9/31 | 3.44 | yes (ncomp) |
| raw / log / gamma 0.2 | 36/34 | 1.06 | 38/54 | 1.42 | no |
| common-mode removed | 41/36 | 1.14 | 35/54 | 1.54 | no |

- Three of the four fires are on the **component-count** arm only (fewer, larger bodies); the
  **vertical-extent** arm — what "a shaft" means — clears 1.5x in one treatment only (z-blur, 1.80x).
- Margins are far below the planted-shaft calibration (4-5x vrun, 7-13x ncomp).
- It does not recur in the four off-centre crops of the same scene (all 0/8).
- **Candidate explanation (untested):** real scenes carry spatially coherent SURFACE content that
  band-limited speckle does not; the pipeline is surface-pinned, so surface texture can merge
  above-threshold voxels into fewer, larger bodies without adding vertical extent. The matched null
  controls for the pipeline but not for "a scene exists", so the rule is sensitive to surface content
  as well as to depth structure. A surface-matched null (or a co-location test against surface
  brightness) would test this. Not done; listed as open in STATE.md.

## 4. An observation outside the rule

In the untreated volumes the real crops' top-1% voxels span more of the depth axis than the null's
(span 0.76 / 0.88 / 0.58 vs 0.40). `span` is recorded but is not part of the pre-registered rule, so
this carries no verdict; it is noted because it points the same way as §3 (real scenes are not
exactly an empty scene through the same pipeline), which is expected and is not evidence of depth
structure.

## 5. Consequences

- Paper §7's "the negative claim in this section remains provisional" can be updated: the
  pre-registered step 1 has been run and is negative, with the 02-08 near-miss disclosed.
- C.4 step 2 (scoring published figures) is now permitted by the pre-registration's ordering.
- Prediction record: the stated prediction held, narrowly on one scene.
