# Technical Bible — Subsurface SAR Doppler Tomography

*The complete working reference for this project. Read it before touching data.*
*Version 1.2. Every quantitative claim is traceable to the References at the end.*

---

## 0. The one-paragraph version

Filippo Biondi's method does **not** push radar into the ground. It uses a satellite
radar as a **remote vibrometer**: it measures sub-millimetre micro-motions of the
*surface* (driven by ambient seismic/wind energy), then treats that vibration field
as the imaging wave and runs a tomographic inversion to infer structure at depth.
The measurement front-end is legitimate and well-precedented. The deep 3-D inversion
(hundreds of metres to kilometres, from essentially one acquisition) is unproven,
internally inconsistent in places, and almost certainly overstated. This project
rebuilds the method honestly and **validates the depth axis against known ground
truth before believing — or selling — anything.**

---

## 1. Who, and what exists in the literature

**Filippo Biondi** — Italian aerospace/electronic engineer, PhD (electronic & electrical
engineering) University of Strathclyde; earlier at University of L'Aquila; 2022–24
Strathclyde; now independent via **HarmonicSAR.com**. ~43 publications, h-index ~17.
Real, respected pre-pyramid track record: SAR super-resolution, low-rank+sparse ship/wake
detection, **ship micro-motion from COSMO-SkyMed staring spotlight (2019)**, Mosul Dam
destabilisation monitoring, bridge SHM.

**Corrado Malanga** — retired organic-chemistry lecturer (Pisa), known mainly for
alien-abduction/consciousness work. Not a remote-sensing scientist. Source of most of the
project's dubious framing (Halls of Amenti, "these are photographs, no validation needed,"
depth "by counting pixels"). **Weight his interpretive claims at ~zero.**

**Armando Mei** — Egyptologist/author; supplies the ancient-texts layer.

### Key documents
| Item | What it is | Status |
|---|---|---|
| Biondi & Malanga 2022, *Remote Sensing* 14(20):5231 | Great Pyramid (Khufu) Doppler tomography | **Peer-reviewed**, contested |
| Biondi 2022, *Remote Sensing* 14(15):3828 | Vesuvius volcano Doppler tomography | Peer-reviewed, little pushback |
| arXiv 2208.00811 | Preprint of the Khufu paper (has the resolution derivation) | Open |
| Patent **WO2024008365A1** | "SAR underground, undersea, under-ice… tomographic doppler imaging" | **Published PCT, legal status CEASED (lapsed)** |
| 2025 Khafre "underground city" claims | 648 m–2 km structures | **Not peer-reviewed**, press conference + YouTube |

The patent being *lapsed* matters: there is **no enforceable IP** blocking you, and its
text is the fullest public method disclosure. It explicitly claims the method works on
"any satellite **and airborne**" data, "**any transmission frequency**, and any
chirp-Doppler bandwidths" — i.e. Biondi himself says the radar band is not the
differentiator, and airborne/drone is in scope.

---

## 2. The method, step by step

Input: one focused **Single-Look Complex (SLC)** SAR image (or raw/CPHD).

1. **Doppler sub-aperture decomposition.** Slice the azimuth (Doppler) spectrum of the
   single image into many overlapping sub-bands. Each sub-aperture is the same scene at a
   slightly different squint angle — the only angular diversity in a single pass.
2. **Micro-motion estimation.** Track sub-pixel displacements *between* sub-apertures by
   high-precision coregistration. Recovers a per-pixel vibration history (sub-mm), driven
   by ambient seismic + wind energy.
3. **Multi-chromatic analysis (MCA).** Organise the complex vibration observations along
   the tomographic (depth) view-direction.
4. **Steering-matrix inversion.** Build a steering matrix `A(z)` whose column for each
   candidate depth `z` predicts the phase signature a source at that depth imprints across
   the sub-apertures. Solve `Y = A(z) h(z)` for the depth profile `h(z)`.
5. **Stack tomographic slices** from multiple view-directions (2025 work: multiple
   satellites) into a 3-D volume.

**Crucial point:** this is **CT-like in form** (many angular projections → 3-D), but unlike
medical CT the projection geometry is *modelled, not measured*. In CT the operator is
ground-truth-correct because the source angles are known exactly. Here `A(z)` encodes an
*assumed* seismic propagation model. Measured operator → assumed operator is the difference
between tomography you can trust and tomography people fight about.

---

## 3. The resolution math (this is the crux)

### 3.1 Radar image resolution (sets measurement quality, NOT depth)
- **Range (slant):** δ_range ≈ c / (2·B), B = chirp bandwidth. Independent of band.
  (Pinned Bingham scene: B ≈ 466 MHz → ~0.30 m slant-range resolution.)
- **Azimuth:** stripmap ≈ D/2; spotlight finer via integration angle. Band-independent.
- **Implication:** "switch X→Ku for higher resolution" is **wrong**. Resolution comes from
  **bandwidth and aperture**, not wavelength. Shorter radar wavelength only helps
  *displacement sensitivity* at the cost of faster decorrelation.

### 3.2 Tomographic (depth) resolution — Biondi's actual formula
> **δz = λ·R / (2·A)**

where **λ is the SEISMIC/acoustic wavelength**, R = slant range, A = synthetic aperture in
the tomographic (Doppler) synthesis. Biondi's own numbers:
- λ = v/f = 6000 m/s ÷ 12 500 Hz ≈ **0.48 m**
- R ≈ 650 000 m, A ≈ 42 000 m → δz = 0.48·650000 / (2·42000) ≈ **3.71 m**

The classical TomoSAR elevation formula with the **radar wavelength swapped for the
acoustic one** — depth resolution is governed by the *seismic* wavelength and the synthetic
aperture in the vibrational domain, **not** the radar chirp.

### 3.3 Where "better resolution" actually comes from (the optimisation levers)
1. **Shrink R / grow angular aperture (A/R).** Dominant lever; where the **drone idea is
   genuinely right** (low R, wide arc → large angular aperture). Right call, wrong original
   reason (geometry, not wavelength).
2. **Raise investigation frequency f** → shorter seismic λ → finer δz. Caveat: high-f
   seismic attenuates fast; the published 12 500 Hz appears to *violate Nyquist* (§5).
3. **More coherent data → larger A + more independent looks.** The legitimate version of
   "more data = better": more *coherent aperture*, not just more scenes.
4. **Super-resolution inversion** (Capon/MVDR, MUSIC, compressed sensing) — beats the
   Rayleigh limit when scatterers are sparse. Highest-leverage algorithmic upgrade.

---

## 4. Honest physics framing — the depth ladder

| Rung | What | Status |
|---|---|---|
| Measurement | remote surface vibrometry | **Solid**, well-precedented |
| Shallow inversion | metres → tens of m | Plausible, partly validated, **commercially useful** |
| Deep inversion | hundreds of m → km | **Contested, probably wrong as claimed**; all the glamour |

**Analogy discipline.** Medical imaging (X-ray/MRI/ultrasound, and Midjourney's ultrasonic
CT) succeeded with *active, multi-angle, penetrating, surrounding* physics **and** rigorous
ground-truth validation. Biondi's method is passive, single-surface, narrow-aperture. The
reconstruction math (full-waveform inversion + AI priors) is real and portable from
medicine/seismology — but **compute amplifies a physically adequate measurement; it cannot
manufacture information the geometry never captured.** Garbage aperture in, confident
artifact out.

## 4.1 Geophysical factors that control the signal AND the depth axis

The method has two physical dependencies the source papers gloss over, both modulated by
environment, season, and site geology. Getting them wrong is a primary way the depth axis
becomes fiction.

**Illumination — where the vibration energy comes from.** The subsurface is "lit" by
ambient seismic energy whose strength/spectrum vary with: ocean microseisms (~0.05–0.5 Hz,
the dominant global background, strongest in winter storm season); wind loading
(weather/seasonal); cultural/traffic/industrial noise (daytime/weekday). A single ~3 s
acquisition captures whatever ambient field existed at that instant — two scans of the same
place can be illuminated very differently unless this is controlled.

**Propagation — what sets the depth axis.** Depth = seismic velocity ÷ investigation
frequency, so the *velocity model* is everything, controlled by:
- **Groundwater / water table** — saturated vs dry ground differ strongly in seismic
  velocity, impedance and attenuation; the water table is itself a reflector and moves
  seasonally. The same phase maps to different depths in wet vs dry season.
- **Ground temperature / freeze–thaw** — frozen near-surface is much stiffer/faster;
  seasonal frost swings near-surface velocity by large factors. Diurnal thermal expansion
  of the surface is also a real micro-motion that can mimic subsurface vibration.
- **Local geology** — rock type, layering, faults, cavities set the velocity structure and
  the resonances used to call a feature a "void."

**Consequence.** A site-specific velocity model (ideally boreholes or existing seismic
surveys) is a *required input*, not optional. Biondi's 2022 paper used a single uniform
velocity (~6000 m/s) and the public depth claims were "counting pixels" — no rigorous,
groundwater/layering-aware velocity modelling is evidenced. This is at once the method's
necessary input and its largest hiding place for error.

**Legitimate cousin.** Ambient-noise seismic interferometry / coda-wave monitoring
deliberately exploits these temporal changes to monitor groundwater, temperature and stress
(aquifers, volcanoes, faults). Reporting *relative temporal change* ("velocity changed 0.3%
summer→winter, consistent with a 4 m water-table drop, checkable against a well") is far
more defensible than absolute deep static imaging.

**Rules this imposes on the project.**
1. Pick validation sites with a known velocity/geology model so the depth axis is calibrated, not assumed.
2. Treat acquisition season / time-of-day as a controlled variable; use multi-date stacks to test whether residuals track groundwater / freeze–thaw.
3. List diurnal thermal expansion as a named confound in every pre-registration.

---

## 5. Known failure modes & critiques (what to fix / watch)

From the two independent reproductions (the only competent technical engagements):

**`not-JASH/sar-doppler-tomography`** (CUDA, synthetic ground truth, null tests, MUSIC/Capon):
- The **published steering law is dimensionally inconsistent** as written.
- **Depth mirror-symmetry:** real-valued observables → tomograms symmetric in ±z unless an
  **analytic-signal step** is added → ghost twins. *(Reproduced & fixed in our tomo_demo.py.)*
- **Nyquist violation:** quoted investigation frequencies exceed the pair-axis Nyquist by
  orders of magnitude → claimed fine resolution may be aliased.
- Effective depth aperture is carried by **lag families**, not individual sub-aperture pairs.

**`mfwarren/Pyramid`** (Python, open Sentinel-1, feasibility):
- Could **not** get robust subsurface imagery from open Sentinel-1 IW TOPS.
- Limit is **geometry/conditioning, not tuning or "too few datasets."** Sentinel-1 Giza
  geometry: aperture ≈ 11.86 km; EM-TomoSAR vertical res ≈ **4.62 km**; acoustic-style ≈
  108–215 m. No metre-scale structure recoverable there.
- **Sentinel-1 IW TOPS is hostile** to this method. Use **staring spotlight**.

**Our own real-data findings (Bingham):**
- Naive global-reference inter-look shift is dominated by decorrelation + azimuth-Doppler
  geometry → use **adjacent-pair, coherence/quality-weighted, detrended** estimation.
- **Coherence-vs-diversity trade-off:** more sub-aperture looks = more angular diversity but
  lower per-pair registration quality. Higher overlap (~0.8) keeps quality usable.

**Demonstrated inversion blind spots (`src/steering_stress_test.py`, June 2026).** Pure-numpy
stress test of our own `tomogram.py` inversion against signature model-mismatch and grid coverage:
- **Robust to signature shape (good, strengthens our nulls):** the matched-filter/spectral inversion
  recovers moderately damped, chirped, and quadratic-phase reflectors above null (contrast falls
  53× → 12–17× but survives). So the positive control, although it injects exactly the tone the
  filter seeks, generalises — a real signal of a *different shape* would mostly still be seen.
- **Blind spot 1 — heavy sub-cycle damping** (a lossy cavity that rings down in <1 oscillation):
  contrast collapses to ~4.6× → **missed**.
- **Blind spot 2 — shallow / sub-resolution** signals pile up at the near-surface edge → mislocated.
- **Blind spot 3 (a real hole) — off-grid reflectors alias to a CONFIDENT FALSE PEAK.** A reflector
  beyond the searched depth range folds back to a wrong, shallow depth at high contrast (~87×), and
  **the look-shuffle null does NOT catch it** (shuffling destroys the tone, so null stays ~1.5×).
  Our pipeline would currently flag this as a detection. This is also a plausible mechanism for how
  an undisciplined inversion (e.g. Biondi's) could yield *confident* deep features that are artifacts.
- **Guard that works:** vary the **number of sub-apertures**; a real in-range reflector holds its
  depth (spread ~0.2), an out-of-range/aliased peak jumps (spread ~23). Widening the depth *grid*
  does **not** work (the matched filter is periodic in z → argmax hops between replicas).
- **Action items:** (a) add a sub-aperture-count stability gate to `tomogram.py`; (b) add a
  *hardened* positive control that injects a heavily-damped resonance (not a pure tone) to measure
  the true detection floor; (c) keep a velocity/steering-form note — velocity only re-labels the
  axis and cannot create contrast, so it is NOT the cause of a null (the steering *form* and grid
  coverage are the real risks).

**Mandatory engineering:** analytic-signal step; Nyquist-safe f; dimensionally-consistent
steering law; spotlight data; adjacent-pair + quality-weighted tracking; null tests;
sub-aperture-count stability check; hardened (damped) positive control.

**Epistemics to reject:** "these are photographs, no validation needed"; depth "by counting
pixels"; "we asked an AI to confirm → 99.9%." None are validation.

---

## 6. Data sources

| Source | Band/mode | Free? | Use |
|---|---|---|---|
| **Umbra Open Data** (`s3://umbra-open-data-catalog`) | X, spotlight 16–50 cm; **CPHD + SICD** | **Yes**, CC-BY 4.0 | **Primary.** Small scenes, phase-level data |
| **Capella Open Data** (`s3://capella-open-data`) | X, spotlight; SLC/SICD/CPHD | **Yes** | Secondary / cross-sensor |
| Sentinel-1 | C, **IW TOPS** | Yes | Fallback only — wrong mode |
| COSMO-SkyMed | X, staring spotlight | **No** (ASI) | What Biondi used 2022; paid |

**Biondi's exact sites in free archives:** Gran Sasso & Giza are **not** in the curated open
sets (Umbra's 80 curated locations are mines/ports/power stations). **Vesuvius is very likely
in Umbra's free "Volcanoes" collection (214 captures, UUID-named)** — his own peer-reviewed
site with known magma-chamber depth. Gran Sasso/Giza would require **paid tasking**.

**Pinned first scene (free):** Umbra, Bingham Copper Mine, UMBRA-05, 2024-01-12. X-band,
λ≈3.12 cm, slant range 738 km, 4×4 km, 0.5 m, ~100 MP SICD, plus CPHD. Multiple dated passes
exist (repeat-pass + multi-angle for free). Read with **`sarpy`** (needs Python ≥3.10).

---

## 7. Validation methodology (the part that makes this science)

1. **Pre-registration** — write ground truth, hypotheses, metrics, thresholds *before*
   processing (`docs/VALIDATION_PROTOCOL.md`).
2. **Blinding** — produce the tomogram, *then* overlay truth. Never tune toward the answer.
3. **Null tests** — shuffle/sign-flip to measure chance structure; report above-null only.
4. **Metrics** — detection (AUC vs null), localisation error (m), measured-vs-predicted δz,
   specificity (false positives over known-solid), repeatability (cross-pass/sensor).
5. **Written kill criteria** — a rigorous negative result is publishable and valuable.

Validation order: **synthetic ground truth → Bingham (measurement sanity) → Vesuvius
(subsurface, Biondi's own site) → paid sites.**

---

## 8. Build status (this project)
- `tomo_demo.py` — inversion core (Bartlett/Capon/MUSIC) validated vs known depths;
  mirror-symmetry failure reproduced + analytic-signal fix; null test. **PASS.**
- `subaperture.py` — Doppler sub-aperture decomposition + sub-pixel shift estimator
  (0.02 px). **PASS.**
- `micromotion.py` — adjacent-pair, quality-weighted, detrended residual-motion estimator.
  **PASS.** Real Bingham residual ~0.008 px (correctly tiny for stable rock).
- `tomogram.py` — **end-to-end integration COMPLETE.** Grid of patches → observations →
  steering-matrix inversion → depth cross-section, with three controls (look-shuffle NULL,
  in-data POSITIVE CONTROL, SURFACE-LEAKAGE correlation). Self-test recovers an injected layer
  at ~27× null with positive control and leakage both passing. **PASS.**

## 8.1 Real-data results (the actual experiment)

All free Umbra X-band single-pass spotlight. Depth axis relative/uncalibrated.

| Site | Collect | Reg. quality | Real / Null contrast | Verdict | Pos. ctrl | Leakage |
|---|---|---|---|---|---|---|
| Bingham Canyon | 2024-01-12-04-09-18_UMBRA-05 | 0.67 | front-end only | no signal | n/a | n/a |
| Komati Power Stn | 2023-08-13-07-03-04_UMBRA-05 | 0.85 | 50× / 10× | null | n/a | n/a |
| Mount Vesuvius | 2023-11-15-19-47-28_UMBRA-05 | 0.72 | 4.1× / 1.5× | **NULL** | **PASS** | 0.03 |
| Butte, MT | 2024-03-07-04-48-26_UMBRA-04 | **0.82** | 3.3× / 1.4× | **NULL** | **PASS** (z=19/19) | 0.28 |

**Reading.** Four real sites, four nulls — every real tomogram is statistically
indistinguishable from its look-shuffled null, while each in-data positive control recovers an
injected reflector, proving the pipeline *would* surface a real signal. The method, as publicly
reproducible on free single-pass X-band, does **not** recover subsurface structure, and it does
**not** hallucinate one.

**Butte is the decisive bounding case.** It was run specifically as a *true-positive* test
against a **known shallow void**: the Butte district is the most densely mapped underground
mining area on Earth (~10,000 mi of workings in ~7 sq mi; level maps at 100-ft intervals from
the surface down to ~5,100 ft — see `docs/BUTTE_GROUND_TRUTH.md`). It was acquired in winter
(frozen, coherent ground) and returned the **highest registration quality of any site (0.82)**,
so the null cannot be blamed on poor data, and the positive control passed. Result: still
indistinguishable from null. Leakage was 0.28 (flagged "low," driven by a single outlier point,
not a trend) and, because the verdict is null, does not affect the conclusion. This converts the
project's claim from "null at three sites" to "null even against a documented shallow void where
success was most expected" — the strongest publishable negative the free-data regime allows.

*A true positive, if it exists, now requires either a larger angular aperture (airborne/drone or
multi-pass) or the cleanest possible shallow target under paid tasking (Cappadocia / Derinkuyu).*

## 8.2 Reproduction of the patent recipe (22 kHz) — a confident artifact, unmasked

We recreated Biondi's disclosed recipe on the Butte SICD: `tomogram.py --n-sub 256 --n-chirp 3
--lrsd --f-investigation 22000 --ground-truth --stability` (256 Doppler sub-apertures, MCA range
sub-bands, LRSD, the patent's 22 kHz investigation frequency). Result:

- **REAL contrast 1720× vs null 2.6×** → it *passes* a naive contrast-vs-null test as a "detection."
  (Stripping MCA+LRSD still gives 884× vs 9.9× — so the high-sub-aperture DFT is the engine; MCA/LRSD
  only sharpen it.)
- **It is an artifact.** The peak is pinned at the **surface (~4 m, 1% of the depth axis; 87% of all
  energy in the shallowest 5%)**, aligns with **none** of the documented West Camp workings (100-ft
  levels to ~457 m) or the **~160 m water table**, and is a low-frequency / weakly-detrended residual
  concentrated by the DFT. The depth axis only *relabels* with f (δz = vR/2Af); 22 kHz makes the same
  artifact read as fine, deep structure.
- **What catches it (the null test does NOT):** the near-surface guard (peak in shallowest 5% →
  ARTIFACT-SUSPECT) and ground-truth mismatch. Note the **sub-aperture-count stability guard alone is
  insufficient** here: a surface-pinned DC artifact is *stable* across n_sub, so "stable" must be
  qualified — STABLE **and** not-surface-pinned = real-like; STABLE **but** surface-pinned = artifact.

**Significance.** This is the most likely mechanism behind Biondi's confident deep tomograms: crank
the sub-apertures, let the DFT concentrate surface/trend energy into a sharp high-contrast band, and
label it deep via an unphysical 22 kHz. It demonstrates that **contrast-above-null is necessary but
not sufficient** — depth-of-peak, ground truth, and (qualified) stability are required. Figures:
`runs/repro_2024-03-07-04-48-26_UMBRA-04_SICD.nitf.png`. This is a centerpiece result for the preprint.

---

## 9. Glossary
- **SLC / SICD** — Single-Look Complex image (amplitude + phase), slant-plane.
- **CPHD** — Compensated Phase History Data (pre-image; ideal for sub-aperture work).
- **Sub-aperture** — slice of the azimuth/Doppler spectrum = one squint look.
- **Steering matrix `A(z)`** — operator mapping candidate depth → expected phase signature.
- **TOPS / spotlight / stripmap** — SAR modes; spotlight good, TOPS bad for this method.
- **Coherence / registration quality** — how reliably two looks image the same structure.
- **MUSIC / Capon (MVDR) / CS-L1** — super-resolution spectral estimators.
- **δz = λR/2A** — tomographic depth resolution (λ = *seismic* wavelength).
- **Velocity model** — site-specific seismic-velocity-vs-depth; converts phase → real depth.
- **Ambient-noise interferometry** — legitimate field exploiting temporal noise changes.

---

## 10. References
- Biondi & Malanga (2022), *Remote Sensing* 14(20):5231. https://www.mdpi.com/2072-4292/14/20/5231 · arXiv:2208.00811
- Biondi (2022), Vesuvius, *Remote Sensing* 14(15):3828. https://doi.org/10.3390/rs14153828
- Patent WO2024008365A1 (Ceased). https://patents.google.com/patent/WO2024008365A1/en
- Reproductions: https://github.com/not-JASH/sar-doppler-tomography · https://github.com/mfwarren/Pyramid
- Umbra Open Data: https://registry.opendata.aws/umbra-open-data/ · Capella: https://registry.opendata.aws/capella_opendata/
- Critiques: Snopes; Graham Hancock (Pilicy appraisal, sympathetic); Decrypt (Parcak et al.).
- ICEYE docs — range resolution depends on bandwidth, not band.

*Maintained as the project evolves. When a result contradicts this document, update it.*
