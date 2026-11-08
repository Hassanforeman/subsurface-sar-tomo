# Pre-registration — Test J: the authors' newly disclosed configuration (9 Nov 2026)

*Written and committed BEFORE any Test J run. Design agreed by consensus between Claude and Grok (Grok chat
"SAR Doppler Micro-Motion Tomography Design Review", 9 Nov 2026). Script: `src/test_j_disclosed_config.py`.
Results will be appended below the line, never edited above it.*

## Why
In recorded interviews (docs/BIONDI_TRANSCRIPT_NUGGETS_2026-11-09.md; unverified auto-transcripts) Biondi states:
(1) "normally a spotlight data has 22 or 25 kHz of bandwidth, but we are using half bandwidth in order to scan inside"
(0–10 kHz on average); (2) collects take 10–15 s and "we need five, six, seven seconds … to listen"; (3) "not 15 seconds
of integration but maybe only five seconds … transform a static image into a small video"; (4) "we only use a part of
the orbit to produce a lower azimuth resolution image, the rest of the orbit we use"; (5) the inversion is an FFT;
(6) maximum depth depends on the Doppler bandwidth synthesised; (7) Umbra's "power is a bit insufficient".
This test runs the reproduction under the most defensible reading of those statements, on data already on disk.

## Mapping (consensus)
Each look is formed from a fraction `f` of the azimuth (Doppler) spectrum, slid across the full spectrum; in spotlight
mode a fraction of the band is the same fraction of the collect time. With n_sub looks, band = N·f requires
overlap = (n_sub − 1/f)/(n_sub − 1).
- **Arm A — half-band looks:** f = 1/2 (statement 1; consistent with 4).
- **Arm B — absolute 5–7 s looks:** f = 6 s / T_collect, for scenes with T_collect ≥ 10 s (statements 2–3).
- For reference, the existing default (n_sub 11, overlap 0.8) already uses f = 1/3, i.e. "5 s of 15 s" (statement 3).
- Depth labels are reported at 10 kHz and 22 kHz (v = 6000 m/s, R = 650 km, A = 42 km); they are labels only and
  do not affect any decision.
Alternative readings noted, not run now: a single static half-band filter with no sliding; a one-off split of the band
into an imaging part and a scanning part.

## Scenes (on disk 9 Nov 2026)
| Scene | Sensor | T_collect | Role |
|---|---|---|---|
| Butte MT 2024-03-07 UMBRA-04 | Umbra | 10.7 s | **Primary** (documented workings to 457 m); Arm B f = 0.56 ≈ Arm A |
| Cairo centre 2024-11-23 C13 SP | Capella | 35.0 s | Secondary: tests "Umbra insufficient" on long-dwell Capella data; does **not** cover Giza; Arm B f = 0.17 |
| Bingham 2024-01-12, Komati 2023-08-13 | Umbra | 3.3 s | Context only, if time allows (Arm A) |
Giza ×3 and Vesuvius need re-download and are deferred to a follow-up under this same pre-registration.

## Fixed pipeline (unchanged from v6.3 Table 3)
512×512 centre crop, 64-px patches, 24 patches, phase-correlation adjacent tracking, accumulation, degree-2 detrend,
DFT steering inversion; contrast on the fixed n_sub-11 window; alignment null (200 permutations); guard = 2 resolution
cells; Hann window primary.

## Runs, in priority order
1. Butte, Arm A, n_sub 11, Hann (with positive control). **Primary.**
2. Butte, Arm A, n_sub 21, Hann (stability).
3. Butte, Arm B (f = 0.56), n_sub 11, Hann.
4. Capella Cairo, Arm A n_sub 11 and Arm B (f = 0.17) n_sub 11, Hann.
5. Butte, Arm A, n_sub 11, rectangular window (sensitivity).
6. Noise control: complex white Gaussian noise of the same size through run 1's exact configuration.
7. Bingham and Komati, Arm A, n_sub 11 (context).
Each run also logs: SICD collect duration and azimuth impulse-response bandwidth; mean lag-1 inter-look correlation;
median |adjacent displacement| (px); fraction of the 24 patches whose own peak lies beyond the guard.

## Positive control
Observation-domain damped resonance (`inject_damped_resonance`) at 0.7 of the fixed window, amplitude 4× the
observation standard deviation — the same hardened control as the sensitivity sweep. (The stronger in-image E12 plant
is not repeated here for compute reasons; this is stated as a limitation.)

## Predictions under the artifact account
- P1: no run clears 5× against the alignment null.
- P2: every run is surface-pinned (peak within 2 cells).
- P3: the noise control (run 6) gives a peak within 1 cell of run 1's peak and a ratio of the same order.
- P4: the positive control is recovered beyond the guard in run 1.
Expected change: with f = 1/2 the looks are more correlated (overlap 0.90–0.95), so adjacent displacements shrink
toward the estimator noise floor; the peak may move within the guard.

## Falsification rule (pre-registered)
The artifact account is **contradicted** if, at Butte, all of the following hold: (i) the stacked peak lies beyond the
2-cell guard; (ii) contrast vs the alignment null is ≥ 5×; (iii) the same peak (within 1 cell) appears at n_sub 11 and
n_sub 21 in Arm A; (iv) the positive control is still recovered. The same four conditions on Capella Cairo would also
count. Failure of any one is compatible with the artifact account. Because the metre scale is a free label, agreement
with a documented Butte level is reported but is not part of the rule.

## Interpretation limits stated in advance
- Biondi's actual settings remain undisclosed; this is the most defensible reading of his own words, not his code.
- Umbra short collects (3.3 s) cannot host a literal 5–7 s look; Butte (10.7 s) and Capella (35 s) can.
- The Capella scene is central Cairo, about 13 km from the Giza plateau; it addresses the sensor objection, not the site.
- A null here does not test the residual on two Giza scenes or the 02-08 shape positive; those remain open.

---
## Results (run 9 Nov 2026, 09:20–09:25 AEST, on Hassan's Mac VM; pre-registration committed first at 982586b)
Run files: `runs/test_j_*.json` (8 files). All scenes 512×512 centre crop, 24 patches, alignment null 200 permutations.

| Scene | Arm | Look time | n_sub | Overlap | Window | Ratio vs alignment null | Peak (cells) | Pinned | Pos. ctrl ratio | Pos. ctrl at injected depth |
|---|---|---|---|---|---|---|---|---|---|---|
| Butte (primary) | A | 5.36 s of 10.7 | 11 | 0.900 | Hann | **5.59** | 1.78 | yes | 4.2 | yes |
| Butte | A | 5.36 s | 21 | 0.950 | Hann | 4.85 | 1.76 | yes | 4.0 | yes |
| Butte | B | 6.00 s | 11 | 0.921 | Hann | **5.09** | 1.73 | yes | 4.6 | yes |
| Butte | A | 5.36 s | 11 | 0.900 | rect | 4.88 | 1.69 | yes | 5.0 | yes |
| Capella Cairo | A | 17.5 s of 35.0 | 11 | 0.900 | Hann | 4.99 | 1.73 | yes | 4.0 | yes |
| Capella Cairo | A | 17.5 s | 21 | 0.950 | Hann | 4.77 | 1.65 | yes | 5.0 | yes |
| Capella Cairo | B | 6.00 s | 11 | 0.516 | Hann | 1.88 | 1.73 | yes | 4.4 | yes |
| Capella Cairo | B | 6.00 s | 21 | 0.758 | Hann | 2.54 | 1.72 | yes | 5.1 | yes |
| **Noise** (Butte-sized) | A | — | 11 | 0.900 | Hann | 4.14 | 1.66 | yes | 4.4 | yes |
| **Noise** | A | — | 21 | 0.950 | Hann | 4.18 | 1.62 | yes | 4.5 | yes |
| Bingham | A | 1.65 s of 3.3 | 11 | 0.900 | Hann | 4.58 | 1.69 | yes | 4.5 | yes |
| Komati | A | 1.66 s of 3.3 | 11 | 0.900 | Hann | 2.95 | 1.67 | yes | 3.8 | yes |

**Scoring against the pre-registered predictions**
- **P1 (no run clears 5×): NOT MET.** Two Butte runs exceed 5× (Arm A n_sub 11: 5.59; Arm B: 5.09). Reported as a failed prediction.
- **P2 (every run surface-pinned): MET.** 12/12 runs peak at 1.62–1.78 cells, inside the 2-cell guard, on every scene, both arms, both windows and the noise control.
- **P3 (noise control within 1 cell of run 1, ratio of the same order): MET.** Noise 1.66 vs Butte 1.78 cells; ratio 4.14 vs 5.59.
- **P4 (positive control recovered beyond the guard in run 1): MET** on location in every run (peak within 1 cell of the injected 3.85 cells). Its ratio, however, is 3.8–5.1, mostly below 5×.

**Falsification rule: NOT triggered.** Condition (i) fails in every run (no peak beyond the guard); (iii) also fails (Butte Arm A drops from 5.59 at n_sub 11 to 4.85 at n_sub 21).

**What the numbers say (interpretation, not part of the rule)**
1. Under Biondi's own stated settings, nothing appears below the surface on any scene, including 35-second Capella data.
2. The two threshold crossings are surface-pinned, not stable across n_sub, and largely reproduced by noise alone (4.14–4.18 at the same settings).
3. The ratio tracks look overlap, not the scene: high-overlap half-band looks (0.90–0.95) give 2.95–5.59 on real scenes and 4.1–4.2 on noise, while the same Capella scene with low-overlap 6 s looks (0.52) gives 1.88. This is the confound flagged in the design review: near-identical adjacent looks push displacements toward the estimator floor (median |disp| 0.002–0.005 px) and inflate the alignment-null ratio.
4. At these settings the ≥5× rule is not a reliable detector on its own: the surface-pinned artifact at Butte (5.59) scores higher than a genuine planted reflector in the same data (4.2). The 2-cell guard and n_sub stability, both pre-registered, are what correctly reject it. This repeats the E12 finding that below a floor the statistic can rank an empty scene above a real reflector.
5. Capella (the sensor Biondi prefers, with a 35 s dwell) behaves like Umbra: surface-pinned, below 5× at every setting.

**Disclosure for the paper:** v6.3's statement that no Hann run clears the rule refers to the v6.3 configuration. Under the half-band configuration two surface-pinned Butte runs exceed 5×; this must be reported if Test J is added.
