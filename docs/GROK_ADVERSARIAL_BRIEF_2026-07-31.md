# Adversarial review request — SAR Doppler tomography artifact mechanism

**Date:** 31 July 2026
**Requester:** Hassan Foreman (independent researcher)
**Context:** preprint under evaluation at PCI Archaeology, ArticleID #1130,
`10.5281/zenodo.21668674`. Repository: `github.com/Hassanforeman/subsurface-sar-tomo`
(commit `fa577ee`).

---

## 0. What I want from you

**Try to destroy the central claim in §5.** I am not looking for encouragement. Specifically:

1. Is the AR(1) null in §5 **fitted to the data it is meant to test**? This is my own strongest
   worry and I want it pressed hard.
2. Is the residual 20% excess (§5.3) actually the signal, with the rest being a fitted artifact?
3. Is the "depth ∝ 1/f is an identity" argument in §6 correct, or is there a data dependence I have
   missed?
4. Check the arithmetic. All of it.
5. The claim reversed twice in one day (§4). Is the current version stable, or is it the third
   unstable position in a sequence that should not yet be published?

Where you agree, say so briefly and move on. Where you disagree, be specific about which number or
which inference fails.

---

## 1. The method under test

Biondi & Malanga (Remote Sensing 14(20):5231, 2022; patent WO2024008365A1) claim single-pass SAR
Doppler tomography can image structures kilometres below the surface. The pipeline, as reproduced
from their published description:

1. Take one single-look-complex SAR image.
2. Split its Doppler bandwidth into `n_sub` overlapping sub-apertures ("looks"). **Default overlap
   0.8** — adjacent looks share 80% of their spectral content.
3. For each of `n_patch` image patches, estimate a per-look displacement trajectory by
   coregistering adjacent looks (phase correlation).
4. **Detrend each trajectory with a degree-2 polynomial** (`detrend(traj, deg=2)`).
5. Invert the stack of trajectories against a steering matrix to produce a depth profile
   ("tomogram"). The patent describes this matrix as a DFT.
6. Convert bin index to metres via `dz_phys = (v / f) · R / (2A)` with v ≈ 3000 m/s,
   f ≈ 22 000 Hz, R = 650 km, A = 75 km.

Trajectory length equals `n_sub` (11 at default). So step 4 removes 3 degrees of freedom from an
11-point series.

**Contrast** is the statistic used to decide detection: the tomogram's peak relative to its own
spread. The manuscript's decision rule is contrast > 5× the null.

---

## 2. The empirical grid — 40 runs, 5 sites, 2 sensors

All at Hann window, phase-correlation coregistration, float64, 512×512 centre crop, 64-px patches,
24 patches, 0.8 overlap. Sub-aperture counts 11, 16, 22, 32, 45, 64, 90, 128.

| site | sensor | native contrast range | ×span | fixed-window range | ×span | peak range | detections >5× |
|---|---|---|---|---|---|---|---|
| Komati Power Stn, ZA | Umbra | 2.76 – 49.00 | 17.8× | 2.75 – 5.28 | 1.9× | 3.2 – 3.7 m | 0/8 |
| Bingham Canyon, UT | Umbra | 3.87 – 128.64 | 33.2× | 2.88 – 5.40 | 1.9× | 2.5 – 3.7 m | 0/8 |
| Butte, MT | Umbra | 3.33 – 29.49 | 8.9× | 2.33 – 7.52 | 3.2× | 3.2 – 3.9 m | 0/8 |
| Mount Vesuvius, IT | Umbra | 4.11 – 124.19 | 30.2× | 3.74 – 5.36 | 1.4× | 3.2 – 3.7 m | 0/8 |
| Cairo (central), EG | Capella | 2.75 – 272.52 | 98.9× | 2.35 – 6.20 | 2.6× | 3.4 – 3.6 m | 0/8 |

Sites are an open-pit copper mine, a coal power station, a hard-rock mining district, an active
volcano and a dense city centre, on three continents, from two unrelated commercial operators.

Three of these reproduce the manuscript's published figures to two decimals (Butte 3.33 vs 3.3,
Vesuvius 4.11 vs 4.1, Cairo 2.75 vs 2.8), so the pipeline is a faithful reimplementation of what
produced the original table.

**Observation A.** `n_sub` — a parameter disclosed nowhere in the paper, patent or presentations —
moves the headline contrast by up to 98.9× on a single scene.

**Observation B.** The peak depth is confined to 2.5–3.9 m (≈1.2–1.9 resolution cells) in every run.

---

## 3. E5 — the peak does not move with processing geometry

One-at-a-time sweep around the baseline, `n_sub` = 11, on two sensors.

Bingham: patch size 32/48/64/96/128, patch count 12/24/48, overlap 0.0/0.4/0.6/0.8/0.9,
crop 256/512/1024 — **peak 1.64 – 1.78 cells, sd 0.05**, 0/13 detections.

Capella, same sweep — **peak 1.62 – 1.80 cells, sd 0.05**, 0/13 detections.

Contrast itself moved substantially over these geometries (2.38 – 8.52), so the geometry
demonstrably changes what the pipeline computes. The peak depth moved by <0.2 cells.

**Also invariant to the depth constants.** Running Bingham at (v=6000, A=42 km) and at the patent's
(v=3000, A=75 km) gives bit-identical contrast, nulls and verdict; only the metre labels change
(3.5 m vs 1.0 m), and the peak stays at 1.66 vs 1.69 **cells**.

---

## 4. Reversals — full disclosure

This claim has changed three times in one day. You should weigh that.

**Position 1 (morning).** "The peak is invariant, therefore the inverter produces its output with no
input — real data is indistinguishable from noise."
*Basis:* §2 and §3 invariance. *Status:* asserted before being tested. **Wrong to assert.**

**Position 2 (E6 v1).** "Falsified. Noise does not reproduce the peak." White noise peaked at 3.11
cells (sd 1.37), only 7% inside the 1.2–1.9 band, contrast 1.39 vs real 3.87.
*Status:* **withdrawn** — the test was mis-specified two ways:
 - real observations were detrended, synthetic noise was **not**, so the comparison was not
   like-for-like;
 - the AR(1) coefficient was taken from the **post-detrend** residuals (lag-1 = 0.009) rather than
   the raw trajectories (0.431), collapsing the "correlated" null into the white-noise null.

**Position 3 (E6 v2, current).** See §5.

The two errors share a form: **comparing against a null that was too weak**, which is precisely the
criticism this paper makes of the original method. That is either a sign the process is working, or
a sign the author keeps constructing nulls that flatter his conclusion. I would like your view on
which.

---

## 5. E6 v2 — the current claim

**Correction applied:** synthetic series are generated at the *raw* look-to-look correlation, then
passed through the **same** degree-2 detrend as the real data.

**Calibration:** sample autocorrelation on an 11-point series is biased low. Setting a = 0.431
produces a synthetic sample lag-1 of only ≈0.25. The generator therefore searches for the
coefficient whose synthetic series reproduces the *observed* sample lag-1 of 0.431; it selects
**a = 0.90**.

Bingham, `n_sub` = 11, 300 trials, seed 0:

| input | peak median (cells) | 5–95 pct | sd | in 1.2–1.9 band | contrast median |
|---|---|---|---|---|---|
| white → detrend | 3.83 | 1.75 – 5.00 | 1.08 | 15% | 1.47 |
| **AR(1) a=0.90 → detrend** | **1.71** | **1.64 – 1.82** | **0.08** | **99%** | **3.22** |
| **real data** | **1.66** | — | 0.05 (over 66 runs) | 100% | **3.87** |

### 5.1 The claimed mechanism

At 80% overlap, adjacent sub-apertures share four-fifths of their spectral content, so their
trajectories are correlated **by construction**, independent of subsurface structure. That
correlation alone, run through the inverter, produces a tightly reproducible peak at ~1.7 cells.

### 5.2 Consequence for the detection margin

Against uncorrelated noise: 3.87 / 1.47 = **2.63×**.
Against the correlated null: 3.87 / 3.22 = **1.20×**.

Every ratio in the published manuscript is measured against a null with the overlap correlation
removed (the original "shuffle null" permutes look order, destroying exactly this correlation).

### 5.3 What is explicitly NOT claimed

Real contrast is 3.87 against 3.22 — a residual ~20% excess exists. Real data is **not** identical
to noise. The claim is that the majority of the apparent signal is accounted for by sub-aperture
overlap, and the remainder clears no sensible threshold.

### 5.4 Supporting autocorrelation measurements

| series | lag-1 | lag-2 | lag-3 |
|---|---|---|---|
| real, raw trajectory | 0.431 | 0.116 | −0.080 |
| real, deg-2 detrended (used by pipeline) | 0.009 | −0.303 | −0.256 |
| white noise, raw | −0.076 | −0.057 | −0.100 |
| white noise, deg-2 detrended | −0.269 | −0.173 | −0.088 |

Post-detrend values must be read against the noise reference (−0.269), not against zero: a degree-2
fit on a short series forces negative correlation.

---

## 6. The analytic claim — depth is proportional to 1/f by construction

In the implementation, the tomogram is computed on a bin grid that does not involve `f`. `f` enters
only through `dz_phys`, applied at the end to convert bins to metres:

```python
z_native = np.linspace(0, n_sub * DZ_TARGET / 2, 300)   # no f
T = tomogram_from_observations(obs, z_native)           # no f
z_m = z_native * (dz_phys / DZ_TARGET)                  # dz_phys = (v/f)·R/(2A)
peak_m = z_m[argmax(T.sum(0))]
```

`argmax` is independent of `dz_phys`. Therefore **peak_m ∝ dz_phys ∝ 1/f exactly**, with no data
dependence. Empirically: `dz_phys` 2.11 → 0.59 m (ratio 3.57) gives peak 3.5 → 1.0 m (ratio 3.5).

Combined with §5, the reported depth = (a bin fixed by the method) × (a scale chosen by the analyst).
Any depth is reachable by choosing `f`, and nothing in the data constrains that choice.

**Is this reasoning sound, or does `f` enter somewhere I have not traced?**

---

## 7. Known weaknesses — attack these first

1. **The AR(1) null is fitted to the data.** Its coefficient is chosen so the synthetic series
   matches the real series' measured correlation. Is this legitimate null construction, or is it
   tuning a null until it reproduces the observation? My defence: the correlation being matched is
   a *known consequence of the overlap parameter*, not a free parameter. My worry: I did not derive
   a = 0.90 from the overlap; I searched for it.
   **A more principled null would synthesise sub-apertures from white noise with the actual 80%
   spectral overlap and run the identical decomposition — deriving the correlation rather than
   fitting it.** That has not been done. How much does its absence weaken §5?
2. **One site, one `n_sub`.** E6 v2 has been run only on Bingham at `n_sub` = 11.
3. **AR(1) may be the wrong correlation model.** Overlap-induced correlation has a specific
   structure set by the overlap fraction and window; AR(1) is a one-parameter stand-in.
4. **The 2-cell surface-pinning guard is a choice.** It flags 40/40 runs; the previous
   5%-of-axis rule flagged 14/40. Is 2 cells defensible, or convenient?
5. **The contrast statistic itself** may be sensitive to the tomogram's shape in ways not examined.
6. **All scenes are X-band spotlight.** No C-band or L-band evidence.
7. **`dz_phys` uses the patent's constants**, which are themselves undefended.

---

## 8. What I believe I can defend, and want checked

1. `n_sub` alone swings the headline contrast up to 98.9× on one scene, and is disclosed nowhere.
2. Peak depth is confined to 1.2–1.9 cells across 5 sites, 2 sensors, 8 sub-aperture counts,
   13 geometries and 2 constant sets.
3. Reported depth ∝ 1/f exactly, by construction.
4. Correlated noise with no scene reproduces the peak position, its tightness, and 83% of contrast.
5. Against a correctly correlated null, the real excess is ~1.20×, not 2.63×.
6. Therefore: the method's depth output is not evidence of subsurface structure.

**Which of 1–6 survives your scrutiny, and which does not?**
