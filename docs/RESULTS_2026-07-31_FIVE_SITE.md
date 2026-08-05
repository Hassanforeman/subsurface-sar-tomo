# Five sites × eight sub-aperture counts — complete grid, 31 July 2026

*Prepared for the revision of the PCI Archaeo submission (ArticleID #1130). All runs use
`src/followup_experiments.py` with the fixed comparison window, the absolute surface-pinning guard,
and the alignment null. Raw outputs in `runs/followup_nsub_*.json`.*

**40 runs. 5 sites. 2 independent satellite operators. 3 continents.**
**0/40 detections. 40/40 surface-pinned. Peak depth confined to 2.5–3.9 m everywhere.**

---

## 1. The headline result

| site | sensor | native contrast range | ×span | fixed-window range | ×span | peak range | detections >5× | pinned (old → new guard) |
|---|---|---|---|---|---|---|---|---|
| Komati Power Stn, ZA | Umbra | 2.76 – 49.00 | 17.8× | 2.75 – 5.28 | 1.9× | 3.2 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Bingham Canyon, UT | Umbra | 3.87 – 128.64 | 33.2× | 2.88 – 5.40 | 1.9× | 2.5 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Butte, MT | Umbra | 3.33 – 29.49 | 8.9× | 2.33 – 7.52 | 3.2× | 3.2 – 3.9 m | **0/8** | 3/8 → **8/8** |
| Mount Vesuvius, IT | Umbra | 4.11 – 124.19 | 30.2× | 3.74 – 5.36 | 1.4× | 3.2 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Cairo (central), EG | **Capella** | 2.75 – **272.52** | **98.9×** | 2.35 – 6.20 | 2.6× | 3.4 – 3.6 m | **0/8** | 2/8 → **8/8** |

Sites: an open-pit copper mine, a coal-fired power station, a historic hard-rock mining district,
an active volcano, and a dense city centre. Imaged by two unrelated commercial operators with
different constellations, different ground processors and different product chains.

> ### ⚠️ §14 IS THE CURRENT POSITION — READ §12–§14 BEFORE QUOTING ANYTHING ABOVE
>
> **§14 reproduces both signature behaviours of the method — the fixed shallow peak and the
> `n_sub` contrast explosion — from accumulated Gaussian noise with no SAR data of any kind.**
> Walk contrast rises 72.9× over the same length range while the increments of the same series
> stay flat at 1.1×; the walk peak sits at 1.66–1.71 cells at every length, 100% pinned.
>
> ---
>
> ### §12 (retained for the mechanism experiment on real data)
>
> **Empirical findings (§1–§9, §11) stand.** Pure white noise through the identical pipeline
> reproduces the peak position (1.71 vs 1.66 cells) and the contrast (3.60 vs 3.87). The real
> excess over a properly derived null is a few percent, **not** the 2.4× quoted in §1–§5.
>
> **Two mechanism claims are withdrawn:** "the inverter produces this from nothing" (§10) and
> "80% sub-aperture overlap manufactures the peak" (§11.1 — the effect is present at *zero*
> overlap).
>
> **§12 supersedes both**, and unlike them it rests on a direct experimental contrast with a matched
> control: the trajectory is a running total (`np.cumsum`), which is a random walk, and removing
> only that step moves the peak off the surface and collapses the contrast.

## 2. Finding A — the reported depth is a property of the pipeline, not the ground

**Across all forty runs the peak lies between 2.5 m and 3.9 m** — between roughly 1.2 and 1.9
resolution cells. It does not vary with site, with geology, with sensor, or with sub-aperture count.

If the peak depth carried subsurface information, it would move when the subsurface moved. It does
not move at all. A method that returns the same depth over Vesuvius and over central Cairo is not
measuring either of them.

This is the strongest result in the study, and it is a **positive** claim rather than a negative
one: not "nothing was found at five sites," but "**the same thing is found everywhere, and it is the
processing chain.**"

## 3. Finding B — one undisclosed setting moves the headline number by up to 99×

The sub-aperture count is not stated in the 2022 paper, in patent WO2024008365A1, or in any
presentation. On the same scene, with everything else fixed, the native contrast spans:

- Cairo (Capella): **2.75 → 272.52** (98.9×)
- Bingham: **3.87 → 128.64** (33.2×)
- Vesuvius: **4.11 → 124.19** (30.2×)
- Komati: **2.76 → 49.00** (17.8×)

An investigator running Vesuvius at `n_sub = 128` would report a detection **124× above noise**;
at Cairo, **272×**. Both are zero-detection scenes under a correctly specified null. The published
method gives a user no way to know which number they are looking at.

This also confirms the v3 erratum: Komati reaches **49.00** at `n_sub = 128`, reproducing the 50×
published in v2.

## 4. Finding C — the corrected guard changes every row

The old 5%-of-depth-axis rule flags **14/40** runs as surface-pinned. The absolute two-cell rule
flags **40/40**.

The old rule's threshold scales with the depth axis, whose extent grows with `n_sub` while the bin
count stays fixed — so at low `n_sub` a peak 1.5 cells down was passed as "clear subsurface
structure." Every row in the published table sits in that regime.

## 5. Finding D — results are invariant to the depth-calibration constants

Bingham, run twice, changing only the assumed physics:

| | 6000 m/s, 42 km (pipeline default) | 3000 m/s, 75 km (patent's values) |
|---|---|---|
| contrast | 3.87 | **3.87** |
| shuffle null | 1.47 | **1.47** |
| alignment null | 1.62 | **1.62** |
| C / align | 2.40 | **2.40** |
| verdict | surface-pinned | **surface-pinned** |
| `dz_phys` | 2.11 m | 0.59 m |
| peak depth | 3.5 m | 1.0 m |
| **peak in cells** | **1.66** | **1.69** |

Every dimensionless quantity identical; only the metre labels move. All five sites were run at both
parameter sets with the same outcome.

**This is expected, not a discovery** — calibration constants scale an axis and cannot touch the
tomogram. Report it as a check that forecloses the "you used the wrong constants" objection, and as
the cleanest demonstration that **depth here is assigned rather than measured**: change the assumed
physics by 3.6× and the identical feature is reported at 3.5 m or at 1.0 m, with no other
consequence whatsoever.

## 6. Reproduction of published values

| site | published | this study |
|---|---|---|
| Butte | 3.3× | **3.33** |
| Vesuvius | 4.1× | **4.11** |
| Cairo (Capella) | 2.8× / 1.6× | **2.75 / 1.49–1.57** |
| Komati (corrected, v3) | 2.8× / 1.3× | **2.76 / 1.39** |

**The Cairo/Capella row is now verified.** It had not been re-run since submission and is flagged
"Outstanding verification" in the published manuscript. That flag can be removed.

Repeat runs of identical commands produce bit-identical output — the pipeline is deterministic
under a fixed seed. Worth one sentence in the methods.

## 7. Limitations — state these, do not let a referee find them

- **The fixed window reduces the `n_sub` confound but does not eliminate it.** Butte still spans
  **3.2×** across sub-aperture counts (7.52 at `n_sub`=32 against 2.33 at 128), versus 1.4–1.9× at
  the other four. Claiming the fixed window solves the problem would be overstating it. It changes
  no verdict, but it must be reported.
- ~~The peak-depth invariance has been measured at one crop and patch geometry only.~~
  **Tested 31 July — see §9. The invariance holds.**
- **All five scenes are X-band spotlight.** Nothing here speaks to C-band or L-band behaviour.
- **The alignment null is itself a modelling choice.** It is more conservative than the shuffle
  null, but it is not the only defensible null.

## 8. Changes for the revision — REWRITTEN 31 July after §11–§14

*The earlier version of this list predated E7–E9 and proposed the peak invariance as the principal
finding. That ordering is now wrong: the invariance is the observation, and §12–§14 are the
explanation.*

### 8.1 Structure — lead with observation, then mechanism

**Order the results as:**

1. **The empirical invariances** (§1–§5). Peak confined to 1.2–1.9 cells across 5 sites, 2 sensors,
   8 sub-aperture counts, 13 geometries, 2 sets of physical constants. Zero detections in 40 runs.
2. **The depth scale is assigned, not measured** (§5, §6). Depth ∝ 1/f exactly, by construction —
   this is a property of the code path, not a fitted result.
3. **The `n_sub` sensitivity** (§3). Up to 98.9× on one scene from a parameter no published source
   discloses.
4. **The minimal reproduction** (§14). Accumulated Gaussian noise — no image, no sub-apertures, no
   overlap, no coregistration — reproduces *both* the fixed shallow peak (1.66–1.71 cells at every
   length) and the contrast explosion (72.9×), while the increments of the same series stay flat
   at 1.1×.
5. **The mechanism** (§12, §13). Matched-control experiment on real data: `inc` and `cumsum(inc)`
   have identical length, so the steering matrix is unchanged and the only difference is the running
   total. Removing it moves the peak off the surface and collapses the contrast.

### 8.2 Table and text corrections (unchanged from the earlier list)

1. Replace the results table with the grid in §1, under the absolute guard and the alignment null.
2. Upgrade the **Bingham row** from "front-end only / no signal" — it produces a full tomogram and a
   surface-pinned verdict at every sub-aperture count.
3. Fix the Table 2 lead-in, which describes all five sites as indistinguishable from look-shuffled
   nulls while naming Bingham.
4. Remove the **"Outstanding verification"** note on Cairo/Capella — now verified (§6).
5. Recompute the Komati ratio from unrounded values — v3 states **2.15**, derived from rounded
   inputs (2.8 ÷ 1.3); the unrounded figure is **1.99**. No conclusion changes, but this row has
   already required one erratum.
6. State that the analysis was repeated at the patent's own velocity and aperture with identical
   dimensionless results.

### 8.3 New text required

7. **Re-base every ratio.** The manuscript's contrasts are measured against the shuffle null, which
   destroys the very autocorrelation that produces the artifact. Against a properly derived null the
   excess is a few percent, and at `n_sub` = 128 noise *exceeds* real data.
8. **Two sentences on the revision history.** The mechanism account changed twice under
   progressively stronger nulls before settling. Disclosed, that is evidence of process; discovered,
   it is a liability. The relevant distinction is that the current account rests on matched controls
   rather than inference.
9. **A limits paragraph** stating plainly what is *not* shown: that the published imagery is nothing
   but this artifact. Those figures involve stacking, denoising and display choices that have not
   been reproduced and whose inputs are not public. Claiming otherwise would be the one overreach
   capable of discrediting the rest.

### 8.4 Caveats to attach, per external review

10. **PSF-matched null not run.** The synthetic SLC is white; real speckle carries resolution-cell
    correlation. The mechanism claim does not depend on it — E8 is a within-series contrast and E9
    removes the SAR front-end entirely — but **absolute** statements ("noise exceeds real data 2:1")
    should carry a one-clause caveat.
11. **`contrast` is characterised empirically, not analytically**, under strongly autocorrelated
    inputs. §14 measures it across a 12× range of series lengths, which is short of a derivation.
    See §8.5.

### 8.5 One derivation worth attempting — untested

A random walk has a power spectrum falling as 1/f². The steering matrix is described in the patent
as a DFT. If the tomogram of an accumulated series is therefore close to its power spectrum, that
spectrum is monotonically decreasing and its peak lands at the **lowest surviving mode** — and
degree-2 detrending removes exactly the constant, linear and quadratic components. That would
predict a peak at a fixed low bin index regardless of series length, which is what §14 measures.

**This is a hypothesis, not a result.** It makes a sharp, cheap prediction: changing the detrend
degree should move the peak bin by a predictable amount. Testing it would convert §14's empirical
observation into an analytic account and close the last item in external review. It has not been
tested, and the mechanism account in §12–§14 does not depend on it.

---

## 9. E5 — the peak depth does not depend on the patch geometry either

`src/followup_experiments.py --experiment geometry`, Bingham, `n_sub = 11`, one-at-a-time sweep
around the baseline (512 crop, 64-px patches, 24 patches, 0.8 overlap):

| varying | crop | patch | n_patch | overlap | C | C/align | peak | **peak cells** | % axis |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 512 | 64 | 24 | 0.80 | 3.87 | 2.40 | 3.5 m | **1.66** | 30.1% |
| patch | 512 | 32 | 24 | 0.80 | 4.24 | 2.06 | 3.8 m | **1.78** | 32.4% |
| patch | 512 | 48 | 24 | 0.80 | 3.71 | 2.54 | 3.7 m | **1.77** | 32.1% |
| patch | 512 | 96 | 24 | 0.80 | 3.64 | 2.30 | 3.6 m | **1.71** | 31.1% |
| patch | 512 | 128 | 24 | 0.80 | 5.14 | 3.36 | 3.6 m | **1.71** | 31.1% |
| n_patch | 512 | 64 | 12 | 0.80 | 4.42 | 1.90 | 3.5 m | **1.67** | 30.4% |
| n_patch | 512 | 64 | 48 | 0.80 | 4.61 | 3.41 | 3.7 m | **1.77** | 32.1% |
| overlap | 512 | 64 | 24 | 0.00 | 3.59 | 2.05 | 3.5 m | **1.67** | 30.4% |
| overlap | 512 | 64 | 24 | 0.40 | 4.05 | 2.79 | 3.5 m | **1.64** | 29.8% |
| overlap | 512 | 64 | 24 | 0.60 | 2.38 | 1.58 | 3.6 m | **1.73** | 31.4% |
| overlap | 512 | 64 | 24 | 0.90 | 7.47 | 4.58 | 3.6 m | **1.69** | 30.8% |
| crop | 256 | 64 | 24 | 0.80 | 4.87 | 3.40 | 3.7 m | **1.77** | 32.1% |
| crop | 1024 | 64 | 24 | 0.80 | 2.70 | 1.89 | 3.6 m | **1.69** | 30.8% |

**Peak depth: 1.64 – 1.78 cells. Spread 1.09×. Standard deviation 0.05 cells.**
**0/13 detections. 13/13 surface-pinned.**

Patch size varied by 4×, patch count by 4×, overlap from none to 0.9, crop area by 16×. The
contrast itself moved substantially — 2.38 to 7.47, a factor of 3.1 — so the geometry demonstrably
changes what the pipeline computes. **The peak depth moved by 0.14 of a cell.**

No single factor drives it: patch 1.71–1.78, overlap 1.64–1.73, n_patch 1.67–1.77, crop 1.69–1.77.

### What this establishes

The reported depth is not a property of the scene, the geology, the sensor, the sub-aperture count,
the depth-calibration constants, or the patch geometry. It survives every knob we can turn. It is
**a fixed output of the inversion itself.**

**Careful with the `% axis` column.** Within E5 the peak sits at 29.8–32.4% of the axis, but every
E5 run uses `n_sub = 11`, so "fixed fraction of axis" and "fixed number of cells" are
indistinguishable here. The `n_sub` sweeps in §1 break the tie: as `n_sub` rises from 11 to 128 the
axis extent grows eightfold while the peak stays at 3.2–3.9 m. The invariant is therefore **a fixed
number of resolution cells, not a fixed fraction of the axis.**

Combining every experiment — five sites, two sensors, eight sub-aperture counts, thirteen
geometries, two sets of physical constants — the peak lies at

> **peak depth ≈ 1.7 × `dz_phys`**   (observed range 1.2 – 1.9 cells)

and `dz_phys = (v / f) · R / (2A)` depends *only* on the assumed velocity, investigation frequency,
slant range and aperture. **Not on the data.**

### The mechanism test this now points to — cheap, decisive, and not yet run

If the peak is an output of the inversion rather than of the data, then **feeding the inverter pure
synthetic noise should place the peak at the same ~1.7 cells / ~30% of axis.** No satellite data
required.

- Same position → the peak is the steering matrix's response to unstructured input. The patent
  itself describes that matrix as a DFT. This would demonstrate the paper's central thesis
  directly rather than by inference: on the only feature that carries the depth claim, real data
  is indistinguishable from noise.
- Different position → something in the real data *is* influencing the peak, and the invariance
  argument needs qualifying.

This should be run before the revision. It is the natural completion of the argument.

### Cross-sensor confirmation

E5 was repeated on **Capella** (different operator, constellation and ground processor):
peak **1.62 – 1.80 cells, sd 0.05**, 0/13 detections, 13/13 pinned — statistically identical to
Bingham's 1.64 – 1.78. **The geometry invariance is confirmed across sensors.**

---

## 10. E6 — the mechanism: 80% sub-aperture overlap manufactures the peak

**This section has been rewritten twice. Read §10.4 on how much confidence it deserves.**

### 10.1 The first E6 was mis-specified — its conclusion is withdrawn

The first run of E6 (31 July, commit `e5474cd`) compared *detrended* real observations against
*undetrended* synthetic noise, and set the AR coefficient from the post-detrend residuals (0.009)
instead of the raw trajectories (0.431). Both errors made the null far too easy. It concluded that
noise does not reproduce the peak position. **That conclusion is withdrawn.**

### 10.2 The corrected test — Bingham, `n_sub = 11`, 300 trials, seed 0

Synthetic series are now generated at the raw look-to-look correlation and passed through the same
degree-2 detrend as the real data. The AR coefficient is calibrated (a = 0.90) so the synthetic
series reproduces the observed raw sample lag-1 of 0.431 — sample autocorrelation on an 11-point
series is biased low, so setting a = 0.43 would under-correlate the null.

| input | peak median | 5–95 pct | sd | in 1.2–1.9 band | contrast median |
|---|---|---|---|---|---|
| white → detrend | 3.83 | 1.75 – 5.00 | 1.08 | 15% | 1.47 |
| **AR(1) a = 0.90 → detrend** | **1.71** | **1.64 – 1.82** | **0.08** | **99%** | **3.22** |
| **real data** | **1.66** | — | 0.05 (across 66 runs) | 100% | **3.87** |

**Correlated noise containing no scene reproduces the peak position (1.71 vs 1.66), the tightness of
that position (sd 0.08 vs 0.05), and 83% of the contrast (3.22 vs 3.87).**

### 10.3 The mechanism

The correlation is not incidental — it is built in. At **80% sub-aperture overlap**, adjacent looks
share four-fifths of their spectral content, so their trajectories are correlated *by construction*,
independently of anything beneath the surface. Fed through the inverter, that correlation alone
produces a confident, tightly reproducible peak at a fixed shallow depth.

This is a complete mechanistic account of the surface-pinned artifact, and it connects directly to
the inter-look leakage measured in E4.

**It also re-bases the detection margin.** Measured against uncorrelated noise: 3.87 / 1.47 =
**2.63×**. Measured against a correctly correlated null: 3.87 / 3.22 = **1.20×**.

The real excess over a properly specified null is roughly **20%**, not a factor of two and a half.
This quantifies exactly what the erratum told the recommender about the shuffle null being
anti-conservative — the shuffle destroys look-to-look correlation, so it compares real data against
something closer to the 1.47 column than the 3.22 column.

### 10.4 What must NOT be claimed

- **Not** "real data is indistinguishable from noise." Real contrast is 3.87 against 3.22; a
  residual excess exists. The defensible statement is that *the overwhelming majority of the
  apparent signal is accounted for by sub-aperture overlap, and the remainder does not clear any
  sensible threshold.*
- **Not** settled. This finding is one day old and the claim has moved twice — invariance implies
  noise-equivalence, falsified, then revived under a corrected null. Both reversals came from nulls
  built too weakly, which is the same failure the paper criticises. Before it enters the manuscript:
  - reproduce on **Capella** and at least one further site;
  - check the calibration at other `n_sub` values, since the overlap-induced correlation depends on
    `n_sub` and the trajectory length;
  - verify that a = 0.90 is not an artifact of the 11-point series length.

### 10.5 On the autocorrelation question raised against the erratum

`src/check_detrend_autocorr.py`, Bingham:

| series | lag-1 | lag-2 | lag-3 |
|---|---|---|---|
| real, raw trajectory | **0.431** | 0.116 | −0.080 |
| real, deg-1 detrended | 0.191 | −0.166 | −0.287 |
| real, deg-2 detrended (used) | **0.009** | −0.303 | −0.256 |
| white noise, raw | −0.076 | −0.057 | −0.100 |
| white noise, deg-1 detrended | −0.179 | −0.099 | −0.118 |
| white noise, deg-2 detrended | **−0.269** | −0.173 | −0.088 |

The post-detrend 0.009 must be read against the identically-detrended noise reference of −0.269, not
against zero: a degree-2 fit on a short series forces negative correlation. On both readings — raw
0.431 vs −0.076, detrended 0.009 vs −0.269 — **the look-to-look smoothness is real.**

**The erratum's rationale sent to Dr Di Palma on 29 July is correct and needs no retraction.** For
precision, the manuscript should cite the raw-trajectory figure and the noise reference rather than
the bare post-detrend number.

### 10.6 Next

E7: a synthetic-only demonstration — generate a tomogram from correlated noise with no scene at all,
and place the apparent structure at a chosen depth via the investigation frequency (depth ∝ 1/f is
an identity, not a fit). Requires no satellite data and would be the most legible figure in the
paper.

---

## 11. E7 — the principled null. Two corrections and a stronger result.

Complex white noise (no scene) through the identical pipeline, 40 trials per overlap, `n_sub` = 11.
**Nothing fitted.**

| overlap | raw lag-1 | peak median (cells) | 5–95 pct | sd | contrast median | pinned |
|---|---|---|---|---|---|---|
| 0.00 | 0.447 | 1.73 | 1.64 – 1.82 | 0.06 | 2.84 | 100% |
| 0.40 | 0.437 | 1.71 | 1.62 – 1.86 | 0.07 | 2.82 | 100% |
| 0.60 | 0.470 | 1.71 | 1.60 – 1.92 | 0.18 | 3.05 | 98% |
| **0.80** | 0.498 | **1.68** | 1.62 – 1.80 | 0.05 | **3.80** | 100% |
| 0.90 | 0.558 | 1.69 | 1.62 – 1.79 | 0.05 | **5.51** | 100% |
| **REAL** | 0.431 | **1.66** | — | 0.05 (66 runs) | **3.87** | — |

### 11.1 CORRECTION — "80% overlap manufactures the peak" is WITHDRAWN

Stated in commit `fa577ee`, §10 of this document, and §5.1 of the Grok brief. **It is wrong.**

At overlap **0.00** the trajectories still show lag-1 = 0.447 and the peak still lands at 1.73
cells. Overlap is not the source of the correlation.

### 11.2 The actual mechanism — the trajectory is a cumulative sum

`adjacent_trajectory_e` in `src/sensitivity_sweep.py` ends:

```python
    return np.cumsum(inc), coh
```

The trajectory is the **cumulative sum** of adjacent-look displacement estimates. A cumulative sum
of independent increments is a **random walk**, which is strongly autocorrelated by construction —
no overlap required. That fully accounts for lag-1 ≈ 0.45 at zero overlap.

**Hypothesis (not yet tested):** the inverter reads random-walk smoothness as a coherent depth
signal and places its peak at ~1.7 cells. Overlap does not create this; it *amplifies the contrast*
by correlating the increments themselves (2.84 → 3.80 → 5.51 as overlap rises 0.0 → 0.8 → 0.9).

**Decisive test (E8, not yet run):** feed the raw increments `inc` to the inverter instead of
`np.cumsum(inc)`. If the ~1.7-cell peak disappears, the artifact is the cumulative sum. If it
survives, the hypothesis is wrong.

### 11.3 The residual excess has essentially vanished

| null | noise contrast | real / noise |
|---|---|---|
| shuffle (manuscript's original) | ~1.47 | 2.63× |
| AR(1) fitted (E6) | 3.22 | 1.20× |
| **derived, overlap 0.8 (E7)** | **3.80** | **1.02×** |

Real data sits **2%** above what pure noise produces through the same pipeline at the same overlap,
and the peak positions (1.66 vs 1.68) are indistinguishable.

This confirms the prediction from external review that part of the 20% residual was AR(1) misfit
rather than signal. Each time the null has been specified more correctly, the excess has shrunk.

### 11.4 New finding — noise clears the manuscript's own detection threshold

At **overlap 0.90, pure noise yields contrast 5.51**, exceeding the manuscript's `> 5×` decision
rule. At a plausible, undisclosed setting the method returns a formal detection on data containing
nothing whatsoever.

### 11.5 Caveats

- The synthetic SLC is white; real SAR speckle is correlated at the resolution-cell scale by the
  system PSF. A more faithful null would impose that correlation.
- One site, one `n_sub`, 40 trials.
- E8 has not been run. Until it is, §11.2 is a hypothesis supported by the zero-overlap row and the
  presence of `cumsum`, not a demonstrated mechanism.
- **This document's mechanism claim has now been wrong twice.** Treat §11.2 as provisional.

---

## 12. E8 — the mechanism, demonstrated: the trajectory is a running total

Bingham, `n_sub` = 11, overlap 0.8, 40 noise trials. `inc` and `cumsum(inc)` have identical length,
so the steering matrix is unchanged and the **only** difference is the running total.

| input | series | raw lag-1 | peak (cells) | contrast | surface-pinned |
|---|---|---|---|---|---|
| real | **cumsum — as published** | +0.431 | **1.66** | **3.87** | PIN |
| real | increments | −0.113 | **2.83** | **1.36** | clear |
| white noise (median) | **cumsum — as published** | +0.505 | 1.71 | 3.60 | 100% |
| white noise (median) | increments | −0.055 | 2.94 | 1.41 | 18% |

### 12.1 What is established

`adjacent_trajectory_e` returns `np.cumsum(inc)`: the per-patch trajectory is a **running total of
adjacent-look displacement estimates**. A running total of noisy increments is a random walk —
strongly autocorrelated by construction, at any overlap, with or without a scene.

The inverter reads that walk's smoothness as coherent depth structure and places a peak ~1.7
resolution cells down. Removing only the running total:

- peak moves from 1.66 → 2.83 cells (real) and 1.71 → 2.94 (noise);
- contrast collapses 3.87 → 1.36 (real) and 3.60 → 1.41 (noise);
- surface-pinning falls from 100% to 18%.

**Real data and noise are indistinguishable in both arms** — 3.87 vs 3.60 with the cumsum
(ratio 1.07), 1.36 vs 1.41 without it.

This supersedes both earlier mechanism claims: the inverter alone (withdrawn, §10) and spectral
overlap (withdrawn, §11.1). Overlap *amplifies* the contrast (§11, 2.84 → 5.51 across 0.0 → 0.9)
but the running total *creates* the artifact.

### 12.2 What this does NOT establish

**It does not show the method "should" use increments.** Cumulating relative displacements into an
absolute trajectory is a reasonable thing to do; the increments arm is a diagnostic, not a proposed
correction. The finding is narrower and sharper:

> The trajectory construction introduces a strong positive autocorrelation that the inversion
> interprets as coherent subsurface structure. No control in the published method accounts for it,
> and the resulting peak is reproduced by noise containing no scene.

That is a specific, located, testable defect — not a general assertion that the technique fails.

### 12.3 Caveats

- One site, one `n_sub`, one overlap, 40 trials. Repeat on Capella and at other `n_sub`.
- The synthetic SLC is white; real speckle carries resolution-cell correlation from the system PSF.
  A PSF-matched null remains the outstanding methodological gap, flagged in external review.
- This is the **third** mechanism account in this document. The first two were withdrawn. The
  difference is that this one rests on a direct experimental contrast with a matched control rather
  than on inference from invariance. It should still be presented as the leading account, not as
  settled fact, until it is reproduced on a second site.

### 12.4 For the manuscript

State the empirical findings first — peak invariance, noise equivalence, `n_sub` sensitivity, the
1/f identity — and present §12 as the mechanistic account with its caveats attached. Acknowledge in
one or two sentences that the mechanism was revised twice under progressively stronger nulls; that
history is a strength when disclosed and a liability when discovered.

---

## 13. E8 across sensors and sub-aperture counts — the `n_sub` sensitivity IS the random walk

### 13.1 Cross-sensor (Capella, `n_sub` = 11)

| input | series | raw lag-1 | peak (cells) | contrast | pinned |
|---|---|---|---|---|---|
| real | cumsum — as published | +0.488 | 1.69 | **2.75** | PIN |
| real | increments | −0.129 | 4.76 | 1.31 | clear |
| white noise | cumsum | +0.505 | 1.71 | **3.60** | 100% |
| white noise | increments | −0.055 | 2.94 | 1.41 | 18% |

Same pattern on a second operator. Note that Capella's **real** contrast (2.75) is **24% below** the
pure-noise value (3.60).

### 13.2 Across sub-aperture count (Bingham)

| `n_sub` | lag-1 real / noise | real contrast | **noise contrast** | real / noise |
|---|---|---|---|---|
| 11 | 0.43 / 0.51 | 3.87 | 3.60 | 1.07 |
| 32 | 0.82 / 0.81 | 26.42 | 21.04 | 1.26 |
| **128** | **0.88 / 0.95** | **128.64** | **274.85** | **0.47** |

Removing the cumulative sum at `n_sub` = 128: real peak moves 1.50 → **52.66 cells**, contrast
128.64 → 2.49; noise peak 1.71 → 13.70, contrast 274.85 → 1.72; surface-pinning 100% → **0%**.

### 13.3 The two headline findings are one finding

The look-to-look autocorrelation rises with `n_sub` — 0.43 → 0.82 → 0.88 on real data, 0.51 → 0.81
→ 0.95 on noise — because **a longer random walk is smoother**. Smoother walk → higher contrast.

Therefore the `n_sub` sensitivity documented in §3 (3.87 → 128.64 on Bingham, 2.75 → 272.52 on
Cairo) is **not a separate quirk**. It is the cumulative sum: raising `n_sub` lengthens the walk,
which raises its autocorrelation, which inflates the contrast. The undisclosed parameter and the
artifact mechanism are the same phenomenon.

### 13.4 The decisive numbers

- **At `n_sub` = 128, pure noise yields contrast 274.85 against real data's 128.64.** Data
  containing nothing produces **more than twice** the apparent structure of a real scene.
- **Cairo/Capella's real value at `n_sub` = 128 was 272.52. Pure noise gives 274.85** — agreement
  to within 1%. The most dramatic number in the five-site grid is reproduced, to the percent, by
  an image with no scene in it.
- Across `n_sub` = 11, 32, 128 the real/noise contrast ratio is **1.07, 1.26, 0.47** — scattered
  around unity with no systematic excess in either direction.

### 13.5 Status

The mechanism is now confirmed on **two sensors** and **three sub-aperture counts**, always with the
matched-length control. §12 is no longer provisional on those axes.

Still outstanding: the **PSF-matched null**. The synthetic SLC is white, whereas real speckle carries
resolution-cell correlation from the system point-spread function. This is the last identified way
the null could differ systematically from the data, and it was raised in external review.

---

## 14. E9 — the mechanism reproduced with no SAR data whatsoever

External review accepted §13's unification as strong circumstantial evidence but noted it was one
step short of proof: other `n_sub`-dependent factors (sub-aperture spectral weighting, estimator
variance, per-look SNR) co-vary with trajectory length and had not been excluded.

E9 excludes all of them by construction. **No image, no sub-apertures, no overlap, no window, no
coregistration.** Only iid Gaussian increments, optionally accumulated, degree-2 detrended, and
inverted on the axis the real pipeline uses at that `n_sub`. Length is the sole variable.
60 trials per row, 24 series per trial.

| length | series | lag-1 | contrast median | 5–95 pct | peak (cells) | pinned |
|---|---|---|---|---|---|---|
| 11 | **walk** | 0.471 | **3.29** | 2.26 – 4.84 | 1.70 | 100% |
| 11 | increments | −0.107 | 1.48 | 1.30 – 1.84 | 3.77 | 8% |
| 16 | **walk** | 0.610 | **5.18** | 3.36 – 7.81 | 1.71 | 100% |
| 16 | increments | −0.066 | 1.55 | 1.33 – 1.89 | 4.64 | 7% |
| 22 | **walk** | 0.711 | **9.26** | 7.04 – 13.61 | 1.69 | 100% |
| 22 | increments | −0.056 | 1.49 | 1.29 – 1.77 | 5.94 | 2% |
| 32 | **walk** | 0.790 | **17.12** | 11.66 – 24.24 | 1.69 | 100% |
| 32 | increments | −0.033 | 1.53 | 1.32 – 1.73 | 9.12 | 5% |
| 45 | **walk** | 0.847 | **32.15** | 22.01 – 42.49 | 1.66 | 100% |
| 45 | increments | −0.025 | 1.58 | 1.40 – 1.74 | 12.45 | 0% |
| 64 | **walk** | 0.889 | **65.61** | 44.11 – 86.30 | 1.71 | 100% |
| 64 | increments | −0.015 | 1.62 | 1.43 – 1.85 | 17.18 | 2% |
| 90 | **walk** | 0.920 | **122.01** | 86.84 – 156.29 | 1.66 | 100% |
| 90 | increments | −0.011 | 1.60 | 1.45 – 1.93 | 18.59 | 0% |
| 128 | **walk** | 0.942 | **239.77** | 167.83 – 316.03 | 1.71 | 100% |
| 128 | increments | −0.007 | 1.68 | 1.49 – 1.99 | 33.39 | 0% |

**Walk contrast rises 72.9× across the range. Increment contrast rises 1.1× — flat.**

### 14.1 What this establishes

Both signature behaviours of the method are reproduced by accumulated Gaussian noise alone:

1. **The fixed shallow peak.** The walk peak sits at **1.66 – 1.71 cells at every length**, 100%
   surface-pinned, matching the 1.2–1.9 band measured across five real sites, two sensors, eight
   sub-aperture counts and thirteen geometries. The increments of the same series peak at 3.8 – 33.4
   cells and pin in 0–8% of trials.
2. **The `n_sub` sensitivity.** Contrast scales with length *only* for accumulated series. Since
   every other `n_sub`-dependent factor has been removed, **walk length alone drives it.**

The real-pipeline curve sits inside the synthetic one: Bingham reads 3.87 → 26.42 → 128.64 at
`n_sub` 11/32/128, against 3.29 → 17.12 → 239.77 for pure walks at the same lengths, and 274.85 for
noise pushed through the full SAR pipeline at 128.

**The unification in §13.3 can now be stated causally rather than as a correlation.** The two
headline behaviours of this method are properties of taking a running total of noise.

### 14.2 The plainest statement available

The characteristic outputs of the published method — a confident peak a metre or two beneath the
surface, and a contrast that grows without limit as the sub-aperture count is raised — can be
generated with a few lines of `numpy`: accumulate Gaussian noise, remove a quadratic, invert. No
satellite, no scene, no ground.

### 14.3 What it still does not establish

- It does not show that accumulating displacements is the *wrong* operation. It shows that doing so
  produces these outputs from noise, and that the published method has no control distinguishing
  that case from a real detection.
- The **PSF-matched null** remains open. Per external review, the E8 within-input contrast
  (cumsum vs increments on the *same* series) is insulated from it, so the *mechanism* claim does
  not depend on it. What it would firm up is the *absolute* comparison — the "noise exceeds real
  data at `n_sub` = 128" figure. State quantitative noise-equivalence with that caveat attached.
- `contrast` has still not been characterised analytically under strongly autocorrelated inputs.
  E9 measures its behaviour empirically across a 12× range of series lengths, which is weaker than
  a derivation but is no longer merely anecdotal.

---

## 15. E10 and E11 — the last two objections closed

### 15.1 E10 — the PSF-matched null

External review's remaining methodological objection: the synthetic image in E7/E8 was white, whereas
real SAR speckle is band-limited by the system and therefore correlated at the resolution-cell scale.

E10 builds the synthetic image the physically correct way — complex white noise placed in a centred
sub-block of the **spectrum**, then inverse transformed. `bw_frac = 1.0` reproduces the white image;
lower values give longer resolution-cell correlation. The real scene's occupied bandwidth is
measured rather than assumed.

Bingham, `n_sub` = 11, 25 trials. **Measured real bandwidth (95% energy): azimuth 0.750,
range 0.744.**

| `bw_frac` | raw lag-1 | peak (cells) | contrast | pinned |
|---|---|---|---|---|
| 1.00 (white, = E7) | 0.501 | 1.69 | 3.81 | 100% |
| **0.80 (nearest real)** | 0.514 | **1.73** | **4.14** | 100% |
| 0.60 | 0.553 | 1.75 | 4.68 | 100% |
| 0.40 | 0.536 | 1.73 | 4.97 | 100% |
| 0.25 | −0.010 | 1.49 | 2.57 | 100% |
| 0.15 | 0.477 | 1.60 | 2.52 | 100% |
| **REAL** | 0.431 | **1.66** | **3.87** | — |

**With correctly correlated speckle the peak still matches (1.73 vs 1.66) and the synthetic produces
7% MORE contrast than the real scene** (4.14 vs 3.87; real/synthetic = 0.93). The white-noise null
was not flattering the conclusion — if anything it was slightly conservative.

Across `bw_frac` 1.00 → 0.40 the peak holds at 1.69–1.75 with 100% pinning throughout.

**Report honestly:** the 0.25 and 0.15 rows break the monotone pattern (lag-1 falls to −0.01 at
0.25). Those bandwidths are far below anything a real SAR system produces and are not relevant to
the comparison at 0.75, but the non-monotonicity should be stated rather than left for a referee to
notice. Cause not investigated; likely the coregistration estimator behaving differently on very
smooth images.

### 15.2 E11 — the depth is derived, not merely observed

**The automatic verdict printed by this experiment is imprecise and should not be quoted.** It says
the peak bin is "largely independent of series length." It is not — bins span 4 to 48 at degree 0.
The invariant is not the bin index; it is the **depth in resolution cells.**

Pure random walks, no SAR pipeline, 60 trials, 300-bin axis:

| detrend degree | peak (cells) across 8 lengths (11 → 128) | mean bin × length |
|---|---|---|
| 0 | 0.86 – 0.90 | 525 |
| 1 | 1.05 – 1.14 | 659 |
| **2 — what the pipeline uses** | **1.66 – 1.71** | **1008** |
| 3 | 1.96 – 2.05 | 1204 |
| 4 | 2.41 – 2.59 | 1495 |

Two exact regularities:

1. **Peak depth in cells is fixed by the detrend degree alone**, constant to ±0.05 cells across a
   **12× range** of series lengths.
2. **bin × length is constant** for a given degree (sd 11–34 on means of 525–1495). Since
   `peak_cells = bin × L / 598` for a 300-bin axis spanning `L·DZ/2`, that constant *is* the peak
   depth: 1008 / 598 = **1.685 cells** at degree 2.

**1.685 cells is exactly what every real site, both sensors, all sub-aperture counts, all thirteen
geometries and every noise run returned** (observed range 1.2–1.9, central value ~1.7).

### 15.3 What this means

The characteristic depth reported by this method is not approximately explained by the artifact. It
is **arithmetically determined** by two implementation choices:

- taking a **cumulative sum**, which makes the series a random walk with a 1/f² spectrum, and
- removing a **degree-2 polynomial**, which deletes the constant, linear and quadratic components
  and leaves the maximum at the lowest surviving mode.

Change the detrend to degree 4 and the reported "structure" moves from 1.7 to 2.5 cells. Change it
to degree 0 and it moves to 0.88. Nothing about the subsurface enters at any point.

Combined with the exact 1/f proportionality of the metre labelling (§5), the reported depth of a
feature in this method is a function of: the polynomial order of a detrending step, the number of
bins on the display axis, and an investigation frequency chosen by the analyst. None of these are
measurements of the ground.

### 15.4 Status of external review's open items

| Item | Status |
|---|---|
| PSF-matched null | **closed** — §15.1; conclusion unchanged and slightly strengthened |
| Analytic account of `contrast` under random-walk inputs | **closed** — §15.2 gives an exact law for the peak position; the contrast magnitude remains empirical |
| Acknowledge revision history in the manuscript | outstanding — see §8.3 item 8 |
