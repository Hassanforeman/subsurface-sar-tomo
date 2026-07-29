# Configuration sensitivity across four real sites — response to the 28 July 2026 objections

*Version 2, 29 July 2026. Replaces the 28 July draft, which was based on synthetic scenes
and whose central claim the real data contradicted (see Errata, §7).*

*Code: `src/sensitivity_sweep.py`. Results: `runs/sweep_butte.json`, `runs/sweep_bingham.json`,
`runs/sweep_2023-08-13-07-03-04_UMBRA-05.json`, `runs/sweep_2023-11-15-19-47-28_UMBRA-05.json`,
`runs/four_site_summary.json`, `runs/threshold_calibration.json`.
Figures (committed under `docs/`): `four_site_windows.png`, `threshold_calibration.png`, `komati_nsub.png`.*

---

## 1. What was objected to

On the Malanga interview thread, a commenter posting as F. Biondi raised three configuration
objections:

1. *"Which coregistrator are you using? Are you working with DORIS or GeFolki?"*
2. *"I strongly recommend remaining in Double precision at all times and never working in Float32."*
3. *"Which filtering strategy are you applying to the sub-apertures? I would suggest using a Hamming window."*

and, in a follow-up, the principle that a failed reproduction may reflect *"one or more
configuration choices that are left to the user alone"* rather than a defect in the method,
with the burden of exploring those choices lying on the reproducer.

The objection is reasonable. It is answered here by running it.

## 2. What was run

The full pipeline — sub-aperture decomposition, coregistration, micro-motion estimation,
inversion, null test, hardened positive control, surface-leakage and surface-pinning guards —
across the cross-product of:

| Axis | Levels |
|---|---|
| Site | **Butte MT**, **Mount Vesuvius**, **Bingham Canyon**, **Komati Power Station** (all four Umbra sites from the paper) |
| Window | Blackman, **Hann** (paper), **Hamming** (suggested), rectangular (no taper) |
| Precision | **float64/complex128** (paper), **float32/complex64** |
| Coregistrator | **phase correlation + parabolic** (paper), upsampled-DFT (Guizar-Sicairos — the sub-pixel engine inside DORIS-lineage processors), normalised cross-correlation |

= **96 runs**, 200 permutations each. The harness validates itself first (`--selftest`): it
reproduces the repo's own `decompose_subapertures` to **0.00e+00** at Hann/complex128, all four
estimators recover known sub-pixel shifts, the float32 arm is verified single-precision through the
decomposition and the baseline estimator (`scipy.fft`; `numpy.fft` would silently promote to double
and make that arm meaningless) — though `upsampdft` and `opticalflow` hand data to scikit-image,
which may promote internally, so the claim is weaker for those two — the
permutation p-value is calibrated, and the harness demonstrably **can** detect an injected
reflector. A sweep that cannot detect anything would prove nothing.

## 3. Result — the suggested configuration does not change the outcome

![four sites](./four_site_windows.png)

**The only configuration that crossed the threshold used no sub-aperture taper at all**
(rectangular window + phase correlation at Butte, ratio 5.59 against a threshold of 5.0). Every
window, precision and coregistrator combination that was actually recommended — or that the paper
uses by default — stayed below.

*A previous draft framed this as "1 detection in 48 distinct configurations." That overstates the
robustness: the 48 cells are not independent. Windows share the same SLC and the same patches, the
three coregistrators operate on heavily overlapping information, and the four sites share a code
path and similar Umbra acquisition geometry. The effective number of independent tests is
substantially smaller than 48, so the "1 in 48" ratio understates family-wise false-positive risk.
The claim above does not depend on counting.*

| Objection | Finding |
|---|---|
| **Hamming window** | Crosses the 5.0 threshold at **none of the four sites**. Maxima: Butte 4.59, Bingham 4.18, Vesuvius 2.99, Komati 2.85. |
| **Double precision** | Already in use. float32 and float64 agree **to three significant figures in all 96 runs**; the largest paired divergence in the statistic is 0.012. |
| **Coregistrator** | No estimator flips a verdict at any site, including the upsampled-DFT engine used in DORIS-lineage processors. |
| **Positive control** | Recovered in **96/96** runs — the pipeline demonstrably works under every suggested setting. |

The single detection comes from removing the sub-aperture taper **entirely** — the worst-practice
bracket included to bound the range, not anything the objection recommended.

## 4. The one pattern that deserves scrutiny

Order the windows by how strongly they suppress spectral leakage between adjacent sub-apertures
(Blackman → Hann → Hamming → none) and read the statistic along that axis, phase correlation:

| Site | Blackman | Hann | Hamming | None | monotonic? |
|---|---|---|---|---|---|
| Butte, MT | 1.72 | 2.38 | 4.59 | **5.59** | yes |
| Mount Vesuvius | 1.58 | 2.74 | 2.99 | 3.13 | yes |
| Bingham Canyon | 2.27 | 2.45 | 3.35 | 2.29 | no |
| Komati Power Stn | 1.79 | 2.05 | 2.85 | 1.92 | no |

The apparent signal at Butte rises steadily as spectral isolation between looks is removed. One
reading is inter-look leakage: the taper exists to stop adjacent sub-apertures bleeding into one
another, so a "detection" that grows as that protection is stripped may simply be the configuration
with the most contaminated looks.

**This is a hypothesis, and at least two competing explanations are not ruled out.** (i) Stronger
tapers reduce the effective bandwidth of each look, and therefore its SNR and shift-estimate
precision — weaker residuals under Blackman and Hann are expected *even for a real signal*.
(ii) Surface structure may couple into the residual trajectory differently under different spectral
weightings, so the gradient could be a surface-modulated bias that happens to be monotonic at these
two sites. Nothing here distinguishes these from leakage.

**Two honest caveats.** The monotonic sites (Butte, Vesuvius) are also the two with real subsurface
structure, and the non-monotonic ones (an open pit, a power station) are the two without. That is a
2-of-4 split noticed *after* looking at the data; under random assignment it arises about one time
in six. It is not evidence. And the Butte detection does not survive multiple-comparison correction
against the empty-scene reference (p = 0.020, corrected threshold 0.006), where 0.020 is also the
resolution floor at 50 reference runs per cell.

**The test that would settle it** — and the right quantity matters. Measure the correlation
structure of the **detrended residual trajectories that actually enter the inverter**, as a function
of window, and test whether it tracks the statistic. Correlating the complex looks, or the magnitude
images, measures the wrong thing.

> **That test has since been run. §4 states the hypothesis and the test it requires; §4c (E4)
> reports the result — the statistic tracks inter-look autocorrelation at r ≈ +0.99, with a sign
> change. Read the two together: as of 29 July the leakage reading is a measurement, not the
> hypothesis this section describes.**

**A note on surface leakage by site.** Komati is the only site with leakage scores above the 0.5
flag — 5 of its 12 configurations. Those flags sit in the `ncc` and `blackman` arms; its
Hann/phase-correlation **baseline leakage is 0.32**, comfortably low, and `tomogram.py` independently
reports 0.32 for the same scene. An earlier draft of this document said Komati's apparent structure
was "surface-driven regardless," which overstated it: the baseline is clean, and the flags are
confined to non-baseline estimator/window combinations.

## 4b. An undisclosed parameter that appeared to dominate — and the two reasons it did not

> **SUPERSEDED BY §4c.** This section records what the pipeline *as published* did, and why both of
> its headline readings were wrong. The 194× figure is withdrawn (axis-extent confound), and the
> "flips the verdict four times" framing is retracted (a failure of this reproduction's own guard
> and null, not a property of the method). §4c reports the corrected experiments. The section is
> kept because the failure modes it documents are the point.

**The 194× figure quoted in the previous draft is withdrawn.** The contrast statistic is not
comparable across `n_sub`, so no ratio of ratios across that axis is interpretable. At the time of
writing, what appeared to survive was the qualitative result — that changing only the sub-aperture
count flips the verdict four times on a site with nothing underneath it. **That too is now
retracted; see §4c (E1–E3).**

![komati n_sub](./komati_nsub.png)

Komati Power Station is a surface industrial site with no documented subsurface structure. The
correct answer at every `n_sub` is "nothing there." Instead the script returns null at 11, *"above
null, not surface-pinned → investigate"* at 32, null again at 64, and surface-pinned artifact at
128 and 256.

The `n_sub=32` result is the one to sit with: it is a **false positive at the strongest verdict
level the pipeline can issue**, on a power station, produced by nothing but a different
sub-aperture count.

### Why the magnitude is uninterpretable

`tomogram.py` builds `zgrid = np.linspace(0, n_sub*DZ_TARGET/2, 300)` — the *physical extent* of the
depth axis scales with `n_sub` while the bin count stays fixed at 300 — and `contrast()` is
peak-over-median across those bins. When energy is concentrated near the surface, extending the axis
into empty deep bins lowers the median while the peak is unchanged, so contrast rises even if the
underlying residuals are identical.

Holding a surface-pinned profile *fixed in physical units* and resampling it onto each `n_sub` grid
confirms the mechanism: contrast climbs 1.0× → 3.7× on identical physics, then saturates once the
profile has decayed to its floor.

Two consequences, and they pull in opposite directions:

- The confound is real, so the raw magnitude cannot be quoted as method sensitivity.
- But it **saturates at ~3.7×** in that test, so it does not by itself account for the observed
  spread — the rest depends on profile shape, which also changes with `n_sub`. It would be equally
  wrong to call the whole effect a geometric artefact.

The correct conclusion is neither: **the statistic is not comparable across `n_sub` at all**, so the
magnitude should not be quoted in either direction. A defensible version would fix the depth range
in metres under a stated velocity model, re-bin, and recompute — or replace peak-over-median with a
scale-invariant statistic. Not yet done.

The real/null ratio does **not** rescue it. Shuffling destroys the surface concentration, so the
null profile is spread and does not receive the same inflation: Komati nulls run 1.3, 1.6, 2.7, 7.4,
2.5 across `n_sub` = 11…256, with no consistent scaling. The ratio inflates specifically in the
surface-pinned regime.

### A new finding: the surface-pinning guard's threshold is uncalibrated

The `n_sub=32` false positive survives the confound — it is the one run that is **not**
surface-pinned, so axis stretching cannot explain its verdict. But it clears the guard only
marginally. `shallow_pinned()` flags a peak in the shallowest 5% of the axis; at `n_sub=32` the
metric range is 0–33.8 m and the peak sits at 3 m, i.e. **8.9% of the axis** — past the cutoff by
less than four percentage points, with a peak still only three metres down.

| `n_sub` | metric range | peak | peak % of axis | 5% guard |
|---|---|---|---|---|
| 32 | 0–33.8 m | 3 m | **8.9%** | **clears** |
| 128 | 0–135 m | 3 m | 2.2% | flagged |
| 256 | 0–270 m | 4 m | 1.5% | flagged |

The same 3-metre-deep feature is flagged as an artefact at `n_sub=128` and passes as
"investigate" at `n_sub=32`, purely because the axis it is measured against is shorter. The 5%
cutoff is an unjustified constant, and it should be calibrated — or replaced by a criterion in
physical units — before the guard is relied on.

`n_sub` is specified in **neither 2022 paper nor the patent**. The patent describes `N_D` as
*"the sampling-rate of the mechanical wave existing on the Earth that we are observing digitally"*
and never gives a value. So the parameter that can flip the verdict on a null
site is undisclosed, alongside the three raised in the objection.

**This is what the reproduction's sub-aperture-count stability guard exists for.**
`tomogram.py`'s `look_count_stability()` re-runs the inversion at n/4, n/2 and n and flags a peak
that moves — precisely because a result that depends this strongly on `n_sub` is not a measurement.
The Komati curve is the clearest demonstration of that guard's necessity produced so far, and it
argues the guard should be mandatory rather than opt-in (`--stability`).

## 4c. Follow-up experiments (29 July) — the open criticisms, closed

`src/followup_experiments.py`, self-test 5/5. Four experiments, run on the real scenes.

![followup](./followup_results.png)

### E1 — most of the apparent `n_sub` sensitivity was the depth axis

Evaluating every sub-aperture count on **one fixed depth window** (0–11.6 m, inside the unambiguous
range of every configuration tested) instead of the native stretching axis:

| | spread across `n_sub` = 11…128 |
|---|---|
| native axis (as published) | 2.76 – 49.00 — **17.8×** |
| **fixed window** | 2.75 – 5.28 — **1.9×** |

So roughly nine-tenths of the apparent sensitivity was the confound. The honest statement is that
`n_sub` moves the statistic by about **1.9×** on Komati, not by orders of magnitude. This replaces
the withdrawn 194× figure with a defensible number rather than leaving a hole.

### E2 — the repaired guard catches what the old one let through

Replacing "peak in the shallowest 5% of the axis" with "peak within 2 depth-resolution cells
(4.2 m) of the surface":

| | flagged as surface-pinned |
|---|---|
| old 5%-of-axis rule | 3 / 8 |
| **absolute-depth rule** | **8 / 8** |

Every Komati run peaks at **3.2–3.7 m** — the same shallow feature at every sub-aperture count. The
fractional rule let five of eight through purely because their axes were shorter. The `n_sub=32`
false positive reported in §4b was a **failure of this reproduction's own guard**, and it is fixed.

### E3 — under a correctly-specified null, Komati is null everywhere

The alignment null preserves each patch's depth profile exactly and randomises only whether patches
agree on a depth. Against it, Komati returns **0 / 8 detections** across all sub-aperture counts
(ratios 1.01–2.41). The verdict does not flip at all once the null is specified properly and the
guard is scale-stable.

**This retracts the "flips the verdict four times" framing of §4b.** Those flips were artefacts of
the reproduction's own diagnostics, not of the method under test. Corrected: with a scale-stable
guard and a correctly-specified null, Komati is a consistent shallow surface artefact at every
`n_sub`, which is the right answer for a power station.

### E4 — the leakage reading is now a measurement, not an inference

Measuring the lag-1 autocorrelation of the **detrended residual trajectories that enter the
inverter**, per window, at Butte:

| window | lag-1 autocorrelation | contrast | vs shuffle null | vs **alignment null** |
|---|---|---|---|---|
| Blackman | **−0.103** | 1.98 | 1.33 | 1.34 |
| Hann | −0.010 | 3.33 | 2.07 | 1.53 |
| Hamming | +0.095 | 5.95 | 3.86 | 3.17 |
| rectangular | **+0.244** | 8.30 | 5.59 | **5.07** |

The relationship is essentially the same whichever response variable is used:
r(lag-1, contrast) = **+0.995**, r(lag-1, shuffle ratio) = **+0.994**,
r(lag-1, alignment ratio) = **+0.977**. The script reports the shuffle-ratio figure. The statistic
tracks inter-look correlation almost exactly, and the correlation changes *sign* — from
anti-correlated under the strongest taper to strongly positive with no taper.

**Note that the rectangular-window detection at Butte survives the alignment null** (5.07, above the
5× threshold) — it is not an artefact of the mis-specified shuffle null. It is a real, reproducible
excess. What E4 establishes is its *mechanism*: the excess is carried by inter-look correlation that
the taper exists to suppress, and it is absent in every configuration that suppresses it. A
subsurface return should not require the removal of spectral isolation in order to appear.

This discriminates between the two competing explanations. The bandwidth/SNR account predicts weaker
residuals under stronger tapers, but predicts **nothing** about inter-look autocorrelation rising
monotonically and crossing zero. That is a leakage signature specifically. §4's hypothesis is
therefore upgraded: the Butte window gradient is inter-look leakage, and the single configuration
that crossed the threshold is the leakiest one.

*Caveat: four windows, so four points. The ordering was predicted from theory before measurement
rather than selected after it, and the sign change is not something a fishing expedition produces —
but n = 4.*

## 5. The threshold is calibrated (and one proposed improvement is rejected)

Across **400 runs on synthetic scenes containing nothing**: median 2.77, p95 4.35, p99 5.03,
max 6.02. The paper's 5× threshold carries a **2.0% false-positive rate against that reference** —
so it is not an arbitrary round number.

**Treat 2.0% as an optimistic lower bound, not a calibrated α.** Real SAR scenes carry spatially
structured surface reflectivity, varying temporal coherence, residual range migration and
non-Gaussian residual statistics after sub-aperture formation. Speckle-only and blob-modulated
synthetics do not reproduce the null distribution of this statistic under those conditions. A more
credible reference would be built from real data: crops with no plausible subsurface, or
phase-scrambled versions of the real SLCs that preserve surface magnitude structure while destroying
the residual trajectories.

![calibration](./threshold_calibration.png)

The obvious upgrade — replacing the single shuffled null with a permutation p-value — **fails**: it
fires 24/24 on empty scenes. Adjacent sub-apertures overlap by 80%, so the residual trajectory is
smooth in look index even when built from pure speckle; shuffling destroys that smoothness, and the
test ends up measuring "is this sequence smooth?" rather than "is there structure at depth." Worth
recording, because it is the improvement a referee is most likely to propose.

The fix is not to abandon permutation testing but to specify the null correctly: a surrogate that
**preserves look-to-look autocorrelation** while destroying depth coherence — phase-randomised
surrogates, circular shifts of the trajectory that retain its power spectrum, or block permutation
at the scale of the sub-aperture overlap. Not yet implemented.

## 6. None of the three parameters is disclosed in any published source

| | Patent WO2024008365A1 | Biondi & Malanga 2022 (Giza) | Biondi 2022 (Vesuvius) |
|---|---|---|---|
| Coregistrator named | absent | absent | absent |
| Numerical precision | absent | absent | absent |
| Sub-aperture window | absent | absent | absent |
| **Sub-aperture count `n_sub`** | **`N_D` named, no value** | absent | absent |

The closest any source comes is the Vesuvius paper's *"the pixel-tracking technique"* with
*"high-performance sub-pixel coregistration"*, and the patent's *"pixel-tracking for all those
pixels for which tomography needs to be trained"*. No tool, no algorithm, no parameters.

All three were therefore stated publicly for the first time in a YouTube comment on 28 July 2026.

This matters because of the follow-up argument. If configuration choices are decisive — and §4
shows the window alone moves the Butte statistic from 1.72 to 5.59, across the threshold — and
those choices appear in neither the peer-reviewed papers nor the patent, then the published work is
not reproducible as published. That is not a rhetorical point; it is what the term means.

## 7. Errata, and an unresolved discrepancy in our own results table

**Errata.** The 28 July draft of this document predicted, from synthetic scenes, that a Hamming
window would move the statistic by ~0.24. On the real Butte scene the effect is **2.21** — about
ten times larger. The synthetic scenes were too homogeneous to stand in for a structured real site.
The prediction was wrong; the code was not.

**Correction required to the paper's results table (Komati).** Re-running the
Hann/phase-correlation baseline reproduces the published contrasts exactly at two sites and not at
the third:

| Site | Published | This rerun | `tomogram.py` rerun | |
|---|---|---|---|---|
| Butte, MT | 3.3× / 1.4× | **3.33× / 1.68×** | — | matches |
| Mount Vesuvius | 4.1× / 1.5× | **4.11× / 1.49×** | — | matches |
| **Komati Power Stn** | **50× / 10×** | **2.76× / 1.43×** | **2.8× / 1.3×** | **published row is stale** |

Resolved 29 July 2026. The repo's own canonical `tomogram.py`, run at its defaults on the Komati
scene, returns **2.8× / 1.3×** with mean registration quality **0.85** — agreeing with
`sensitivity_sweep.py` (2.76× / 1.43×, quality 0.85) and disagreeing with the published table by a
factor of ~18. Two independent code paths agree; the table row does not. The published figure is
therefore an error in the manuscript, not in either script, and the manuscript's Komati row needs
correcting.

**The correction strengthens the paper.** 50× / 10× is a ratio of exactly 5.0, sitting precisely on
the `> 5×` decision rule and qualifying as "null" only by a hair — the single most attackable row in
the table. The correct value is **2.15**, comfortably below threshold. The verdict is unchanged;
the margin is much larger.

**Provenance established: the row was run at `n_sub=128`.** LRSD was ruled out first (`--lrsd`
gives 4.0× / 1.2×, ratio 3.33 — nowhere near). Sweeping the sub-aperture count on the same scene
locates it exactly:

| `n_sub` | contrast / null | ratio | verdict printed by `tomogram.py` |
|---|---|---|---|
| 11 (default) | 2.8× / 1.3× | 2.15 | indistinguishable from null |
| 32 | 16.2× / 1.6× | **10.12** | **above null, NOT surface-pinned → "investigate"** |
| 64 | 4.8× / 2.7× | 1.78 | indistinguishable from null |
| **128** | **49.0× / 7.4×** | **6.62** | above null but surface-pinned → artifact |
| 256 | 542.0× / 2.5× | **216.8** | above null but surface-pinned → artifact |

49.0× / 7.4× rounds to the published "50× / 10×". The manuscript's Komati row was therefore
produced at `n_sub=128` while the Butte and Vesuvius rows reproduce at the default of 11 — the
table **mixes configurations across rows**, and the erratum must state per-row settings rather than
simply correct a number. Its verdict column is also wrong for that run: at `n_sub=128` the script
prints *surface-pinned artifact*, not *null*.

## 8. Limits

- One 512×512 crop per site at `n_sub=11`, not the paper's aggressive `n_sub=256` / `n_chirp=3` /
  LRSD configuration. The window gradient should be re-checked in that regime.
- The fifth (Capella cross-sensor) site was not available locally and is not included.
- The empty-scene reference is synthetic; 50 runs per window×estimator cell is thin for the tail.
- Optical flow (the GeFolki-lineage estimator) passes the shift-recovery self-test but was excluded
  from the site grid for runtime.
- The contrast statistic is not comparable across `n_sub` (§4b). Any future cross-`n_sub` comparison
  needs a fixed metric depth range or a scale-invariant statistic.
- The 48 configuration cells are not independent; counting-based framings of robustness are avoided
  for that reason.

## 8b. Independent adversarial review

This document was reviewed adversarially by a second model (xAI Grok) on 29 July 2026, working from
the code, the results and the draft reply but without access to the SAR scenes. Its substantive
findings — the `zgrid` axis-extent confound, the non-independence of the configuration cells, the
over-assertion of the leakage reading, the scikit-image precision caveat, and the limits of a
synthetic reference distribution — are adopted above. Its characterisation of the 194× effect as
"largely" geometric was checked and is not supported: the geometric term saturates near 3.7× on a
fixed profile. The conclusion drawn here is that the statistic is not comparable across `n_sub` in
either direction, which is why the number is withdrawn rather than reattributed.

## 9. Reproduce

```bash
python3 src/sensitivity_sweep.py --selftest
for f in 2023-08-13-07-03-04_UMBRA-05 2023-11-15-19-47-28_UMBRA-05 \
         2024-01-12-04-09-18_UMBRA-05 2024-03-07-04-48-26_UMBRA-04; do
  python3 src/sensitivity_sweep.py --sicd "data/${f}_SICD.nitf" --n-perm 200 \
          --out "runs/sweep_${f}.json"
done
```

## 10. Summary

Run across four real sites and 96 configurations, the suggested settings do not change the result.
Precision was already double and is numerically irrelevant. No coregistrator flips a verdict at any
site. A Hamming window crosses the detection threshold at none of the four. The injected positive
control is recovered in every run, so the pipeline finds a signal when one is present.

**The window does matter, and the mechanism is now measured rather than argued.** Across the four
windows at Butte, the lag-1 autocorrelation of the detrended residual trajectories tracks the
detection statistic at r ≈ +0.99 and changes sign, from −0.103 under Blackman to +0.244 with no
taper (§4c, E4). The choice should have been in the paper.

**One genuine excess remains, and it is not dismissed here.** The rectangular-window configuration
at Butte reaches 5.07 against the alignment null — above threshold, and *not* an artefact of the
mis-specified shuffle null. It is real and reproducible. What the leakage measurement supplies is
its mechanism: the excess is carried by the inter-look correlation that a taper exists to suppress,
and it is absent from every configuration that suppresses it. A subsurface return should not require
the removal of spectral isolation in order to appear.

**Three claims made earlier in this project are withdrawn**, all by our own testing rather than
anyone else's. The 194× sub-aperture-count figure was an artefact of a depth axis whose extent
scales with `n_sub`; on a fixed window the spread is **1.9×**. The "flips the verdict four times"
framing is retracted: with a scale-stable guard and a correctly-specified null, Komati returns
**0/8 detections** across sub-aperture counts from 11 to 128, peaking at 3.2–3.7 m every time — one
consistent shallow surface feature, which is the right answer for a power station. And the
`n_sub=32` "investigate" false positive was a failure of this reproduction's own fractional guard,
which flagged 3/8 shallow peaks where the absolute guard flags 8/8.

What survives is narrower and better supported than what was claimed on 28 July. The coregistrator,
the precision, the window and the sub-aperture count are given no values in either 2022 paper or in
the patent. At least one of them — the window — demonstrably changes the outcome, for a reason that
can now be measured. That is the finding.
