# No Reproducible Evidence for Deep Subsurface Structures Beneath the Giza Plateau: A Pre-Registered Reproduction of Single-Pass SAR Doppler Micro-Motion Tomography, and an Audit of Its Published Imagery

**Hassan Foreman** — independent researcher
Preprint v6 — DRAFT, 27 September 2026. Supersedes v5 (August 2026). Under review at PCI Archaeology (#1130). Not yet peer reviewed.
Code, data identifiers, pre-registrations and every result file: https://github.com/Hassanforeman/subsurface-sar-tomo (Zenodo DOI 10.5281/zenodo.21065675).

> *Draft status.* Numbers are final for the analyses listed; wording will change in response to reviewers. Figure slots name the pipeline output that fills them. Every claim points to a script and a result file in the repository (Appendix A).

---

## Abstract

Between 2022 and 2026, F. Biondi and C. Malanga reported that Doppler sub-aperture "micro-motion tomography" of single spaceborne SAR acquisitions reveals structures hundreds of metres to kilometres beneath the Giza plateau: paired shafts to ~648 m, spiral ramps, large chambers and, in 2026, a buried "second Sphinx". The 2022 article was retracted by *Remote Sensing* on 10 August 2026 for unspecified "serious methodological flaws and statistical errors". This paper supplies the specific, reproducible account the retraction notice does not.

Working only from the authors' paper and patent, I rebuilt the method, added the controls it omits, and applied it to free X-band spotlight data from two sensors over six sites, including three acquisitions of Giza. Every Giza test was pre-registered, with its analysis choices committed publicly before the data were processed. There are five results.

1. **The depth is a label, not a measurement.** The patent's steering matrix is a discrete Fourier transform. On real Umbra orbits, the paper's own steering wavenumbers are uniformly spaced to a few parts in 10⁵ (coefficient of variation 2 × 10⁻⁶ to 2 × 10⁻⁵), indistinguishable from a uniform DFT ladder. The metre scale is set entirely by an unmeasured "investigation frequency" or sound wavelength: the same pixels read as 34 m or 1,110 m.
2. **The method returns the same confident, shallow feature everywhere, including from pure noise.** Across 48 runs over six sites and two sensors there were 0 detections, with the peak confined to 1.2–1.9 resolution cells. A sufficient generating mechanism is demonstrated: accumulated registration noise forms a random walk, and a degree-2 detrend followed by a DFT places its expected peak at 1.68 cells, reproduced with no satellite data. Accumulation is sufficient to generate the artifact; it is not shown to be necessary on two of the three Giza scenes (see below).
3. **At tile scale (13–50 m), the output does not respond to voids known to be there.** Fields of hundreds of excavated 5–30 m mastaba shafts in the Giza Western and Eastern Cemeteries are not distinguished from bare plateau in the same acquisitions (standardised differences −0.10 and −0.03, both inside the plateau-versus-plateau spread). A displacement planted before tracking is detected in every scene.
4. **Nothing in the reproduced volumes is shaped like architecture.** A pre-registered shape statistic applied to the three real Giza volumes gives 0/8, 4/8 and 0/8 treatments against a threshold of 5/8, while planted shafts give 8/8.
5. **The recognisable geometry of the published imagery comes from sources other than the radar measurement, several of them named in the authors' own materials.** In all 16 "tags association" figures of the 2022 paper, the geometry belongs to a CAD model. The tomogram panels are unscaled 2-D heat maps (no axes were added in the journal version), and 4 of 16 are overlaid on drawings of the known interior. The 2026 "Second Sphinx" presentation builds its 3-D sphinx from four unscaled 2-D heat maps, and its own pipeline slide lists an image-to-image GAN, face-landmark and face-embedding tools, golden-ratio canon grids and dialogue with Grok and Gemini.

What remains unexplained is stated. On two of three Giza scenes a weak surface-ward lean survives removal of the running total; it is not an ordering effect (pre-registered, not significant) and is reported as open. The surface-vibration measurement itself is real for strongly driven targets, but ambient ground motion at Giza is below its demonstrated sensitivity, and it does not image the subsurface in any case. This is a critique of method and mathematics, not of intent.

**Keywords:** synthetic aperture radar; Doppler tomography; micro-motion; reproducibility; pre-registration; null result; Giza; image provenance.

---

## 1. The claims under examination

I restate the claims as fairly as I can from the 2022 paper [1], the lapsed patent WO2024008365A1 [3] (the fullest public method disclosure), and the 2025–2026 presentations [4, 5]:

- **C1.** Microwaves do not penetrate rock; instead ambient seismic energy makes the ground vibrate, and the subsurface "becomes transparent like a crystal" when observed through surface micro-motion.
- **C2.** Splitting the azimuth (Doppler) spectrum of one SAR image into sub-apertures and tracking sub-pixel shifts between them recovers that vibration field.
- **C3.** A steering matrix A(K_z, z) focuses these observations in depth, giving 3-D tomograms with depth resolution δz = λR/2A, where λ = v/f is a seismic wavelength.
- **C4.** Applied to Giza, the method reveals paired cylindrical shafts to ~648 m, spiral structures and large chambers; applied elsewhere, the Gran Sasso laboratory at ~1.4 km and, in 2026, a buried second Sphinx.
- **C5.** More than 200 acquisitions from four satellite operators return the same structures, which is presented as independent confirmation.

My standard throughout is the one the original work does not meet. A result counts as a detection only if:
- it exceeds a null built from the same pipeline;
- it survives controls fixed in advance;
- it corresponds to independent ground truth.

## 2. Data and reproduction method

**Data.** All scenes are free, openly licensed X-band spotlight products (Umbra and Capella Open Data, CC-BY 4.0). Six sites were analysed:

- **Giza plateau**, three Umbra acquisitions:
  - 2023-02-07 (UMBRA-05);
  - 2023-02-08 (UMBRA-04);
  - 2023-03-08 (UMBRA-04, the pre-registered primary).
- **Butte, Montana:** densely mapped underground mine workings.
- **Bingham Canyon:** an open pit with no subsurface void.
- **Komati.**
- **Cairo (Capella).**
- **Mount Vesuvius:** the authors' own published site [2].

Exact scene identifiers are listed in the repository.

**Pipeline.** I reimplemented the method as disclosed. Table 1 maps each block of the patent's processing diagram to its implementation.
- Doppler sub-aperture decomposition: 11 looks, 80% overlap, Hann taper.
- Adjacent-pair sub-pixel tracking of 64 × 64 patches, accumulated into a trajectory.
- Degree-2 detrend.
- An analytic-signal step.
- A depth focus by DFT, 300 bins.

The controls the original omits were added:
- an alignment null that preserves each patch's depth profile;
- in-data positive controls, planted as displacement in the image before tracking;
- a surface-pinning guard in resolution cells;
- sub-aperture-count stability.

Every stage has a synthetic self-test against known truth.

**Pre-registration.** From August 2026 onward, every test on Giza was specified in a document committed to the public repository before the data were processed:
- the statistic, thresholds and controls;
- the aggregation rule;
- what each outcome would mean.

Deviations found before running, such as a failed placement check, were written into the pre-registration and committed before any result existed. Result sections were appended after the run. Failures are reported as failures. The five non-Giza sites were analysed before the Giza pre-registrations existed; they are reported as context and are not used to confirm any Giza test.

*Table 1 — the patent's disclosed processing chain (blocks 1–11) mapped to this implementation.* [carry over from v5 unchanged]

## 3. The operator: depth is a Fourier bin with a free label

### 3.1 The steering matrix is a DFT
The patent states that the steering matrix "represents the best approximation of a matrix operator performing the Digital Fourier Transform (DFT) of Y" [3]. The depth tomogram is therefore the power spectrum of each patch's detrended trajectory. The reference implementation agrees with direct DTFT evaluation to one part in 10¹⁵.

A DFT returns a structured, peaked spectrum from any input, so a confident tomogram is the expected output whether or not anything lies beneath the surface. Super-resolution inverters do not change this. Capon and MUSIC applied to the same trajectories surface-pin at the same depth as the plain transform (Giza: 1.75, 1.99 and 1.75 cells). The artifact is upstream of the inverter.

### 3.2 The paper's own K_z form is a DFT on real orbits
The 2022 paper writes K_z = 4πB⊥/(λ_s r sin θ), with B⊥ the platform offset at each sub-aperture centre projected perpendicular to the line of sight. I evaluated this with each Umbra product's own orbit polynomial for the 11-look bank.

*Table 2 — the paper's steering wavenumbers on real Umbra geometry.*

| Scene | Processed aperture | B⊥ span | CV of ΔK_z | Depth repeat per metre of λ_s |
|---|---|---|---|---|
| 02-07 | 1.27 s | 6,510 m | 3.8 × 10⁻⁶ | 292 m |
| 02-08 | 1.18 s | 6,059 m | 2.2 × 10⁻⁶ | 240 m |
| 03-08 | 5.04 s | 25,784 m | 2.3 × 10⁻⁵ | 71 m |

Two consequences follow:
- **The ladder is uniform to a few parts in 10⁵ — indistinguishable from a uniform DFT ladder — so orbit curvature does not rescue the operator.** As implemented, depth is a Fourier bin.
- **The depth axis repeats every λ_s·r·sinθ/(2ΔB⊥), and λ_s is not measured.** With λ_s = 0.48 m the repeat is 140 / 115 / 34 m; with λ_s = 3.8 m it is 1,110 / 912 / 270 m. With one fixed λ_s, the three acquisitions put the same ground on different depth scales. The scale follows viewing geometry, not the ground.

I cannot evaluate the authors' own (undisclosed) look centres. Every bank I can form from the published formula and these state vectors has a steering ladder uniform to a few parts in 10⁵, and depth remains proportional to 1/λ_s.

An independent reimplementation reaches the same result on ICEYE dwell data [7]: a uniform ladder, an exactly periodic depth axis (27.4 m, correlation 1.000), and a scale set by a declared sound wavelength.

### 3.3 The 22 kHz "investigation frequency" is not in the data
The patent synthesises depth at f ≈ 22 kHz. This is ultrasonic:
- ambient ground motion is overwhelmingly below ~100 Hz;
- the Nyquist rate of a look sequence spanning one to five seconds is of order hertz.

f enters only as a final axis scale (δz = vR/2Af). It never touches the inversion.

*Figure 1 — one tomogram, three frequencies:* the identical Butte tomogram places its feature at ~5 m, ~100 m or ~2,000 m for f = 22,000, 1,000 or 50 Hz. [runs/compare_…png, from v5]

"648 m" and "1.4 km" are settings of this dial.

## 4. A sufficient generating mechanism

### 4.1 Tracked increments are registration noise
Each tracked increment comes from registering two sub-looks. I measured look-to-look magnitude similarity on the three Giza scenes:
- **Adjacent looks (80% spectral overlap): 0.58–0.71.** This is about what the same filter bank gives for pure synthetic speckle (0.55–0.61).
- **Looks that share no spectrum: 0.06–0.18,** the speckle floor.

Each increment is therefore carried by the filter-bank overlap, not by a coherent scene seen across the aperture. (Magnitude correlation is used here; the complex-coherence version is listed in §11.)

This agrees with a direct coherence measurement on ICEYE dwells [7]: coherence halves after ~1 s of look separation. It also means that a protocol restricted to nearly non-overlapping looks would register speckle.

### 4.2 A running total of noise is a random walk, and the DFT pins it
The trajectory is the running total of the increments (`np.cumsum`). A running total of noise has a random-walk spectrum: smooth and strongly autocorrelated whatever the scene.
- **The peak position is fixed by the detrend.** After a degree-2 detrend, the DFT peak sits at a position set by the polynomial order. The expected tomogram is a parameter-free matrix quadratic form,

  E[P(z)] = f(z)ᴴ · H (I − P_d) C (I − P_d)ᵀ Hᴴ · f(z),

  with C_ij = min(i, j) + 1 (random-walk covariance), P_d the degree-d polynomial projection (the detrend), H the analytic-signal operator as a matrix, and f(z)_k = exp(−i K_k z) the pipeline's DFT steering. Its argmax, evaluated numerically (src/derive_depth_constant.py), is 1.680 cells at degree 2 (0.869 and 2.474 at degrees 0 and 4; converged in series length). Monte-Carlo walks with no image and no SAR processing give 1.69 ± 0.02 for series lengths 11 to 128, consistent with it. The earlier empirical rule 0.856·(d/2 + 1) is only approximate and is not used.
- **Real sites land at 1.2–1.9 cells.**
- **Contrast also scales with the walk, not the ground.** It rises 73× as the series lengthens from 11 to 128 samples, while the increments stay flat (1.1×). At 128 sub-apertures, an input containing no scene returns more contrast than a real one (274.85 against 128.64). The most dramatic contrast in this study (Cairo, 272.52) is reproduced to within 1% by an input with no scene in it.

### 4.3 What the mechanism does not yet explain (pre-registered test H)
Removing the running total, which leaves series length and steering matrix unchanged:
- **At Bingham Canyon and Cairo,** the peak moves off the surface (1.66 → 2.83 and 1.69 → 4.76 cells).
- **At Giza,** it does so on one of three scenes (02-08: 1.67 → 3.83). On the other two it stays within the 2-cell guard (1.75 → 1.88; 1.77 → 1.95).

I tested whether this residual reflects the *order* of the increments. The null was 1,000 look-order shuffles per scene, and the anomaly criterion (below the null's 5th percentile) was fixed in advance.

Result: 0 of 3 scenes were anomalous. The observed peaks fall at the 10th, 56th and 12th percentiles. The increments are not serially correlated (lag-1 +0.10, −0.13, +0.02), so the pinning is not an ordering or smoothing effect.

The residual is not fully resolved:
- the per-scene nulls pin only 13–16% of the time, so two of three pinned scenes has probability ≈ 0.05 under them;
- both pinned scenes lean surface-ward;
- a post-hoc combination of the three percentiles gives p ≈ 0.13, and is not part of the rule.

**Accumulation is therefore demonstrated to be sufficient to generate the artifact, but not shown to be necessary at two Giza scenes.** A weak surface-ward lean in the increment *values* remains open. It is not evidence of structure: all three scenes are detection nulls.

## 5. Results on real data

### 5.1 Six sites, 48 runs, no detections
*Table 3 — 48 runs = 6 sites × 8 sub-aperture counts (11–128). The Giza row is the 2023-02-07 scene; the other two Giza acquisitions are the repeatability test (§5.2). The decision statistic is contrast relative to the alignment null (rule: ≥ 5×); raw peak-to-median contrast (Hann taper, n_sub 11) is shown for reference only. Every run is surface-pinned (1.2–1.9 cells).*

| Site | Sensor | Decision ratio vs alignment null (n_sub 11) | Raw contrast (Hann; reference only) | Detections (of 8) |
|---|---|---|---|---|
| Giza 02-07 | Umbra | **3.67** | 6.06 | 0 |
| Bingham Canyon | Umbra | 2.40 | 3.87 | 0 |
| Butte | Umbra | 1.53 | 3.33 | 0 |
| Komati | Umbra | ≤ 2.41 (range over n_sub 1.01–2.41) | 2.76 | 0 |
| Cairo | Capella | < 2.75 † | 2.75 | 0 |
| Vesuvius | Umbra | < 4.11 † | 4.11 | 0 |

Recorded ratios: Giza, docs/PREREGISTRATION_GIZA_2026-08-13.md; Bingham, RESULTS_2026-07-31_FIVE_SITE §5; Butte (Hann), SENSITIVITY_RESPONSE_BIONDI E4; Komati, ibid. E3 (range across n_sub; the n_sub-11 value is not separately recorded). † Vesuvius and Cairo ratios are not recorded; the alignment-null contrast is ≥ 1 by construction (a peak is never below the median), so each ratio cannot exceed its raw contrast, which is below 5. [TODO before deposit: regenerate all six at n_sub 11 from the scenes — non-Giza scenes are not currently on disk.]

**The one configuration that crosses 5×.** Under a rectangular (untapered) window, Butte gives 5.07 against the alignment null. The excess tracks inter-look leakage almost exactly (lag-1 autocorrelation of the trajectories +0.244 rectangular, −0.010 Hann, −0.103 Blackman; r = +0.977 between lag-1 and the ratio) and is absent under every taper that suppresses leakage; it does not survive multiple-comparison correction across the configurations tried. It is reported, not counted as a detection, and its mechanism is stated (SENSITIVITY_RESPONSE_BIONDI E4).

**Giza returns the highest raw contrast (6.06) and is still not a detection: its decision ratio is 3.67.** Roughly a third of that excess is the undisclosed window taper alone: the same scene gives 6.06 with Hann, 5.03 rectangular, 4.69 Blackman and 4.52 Hamming.

At Butte, at the authors' settings (256 sub-apertures, 22 kHz), the only confident feature is a band pinned at ~4 m. It aligns with none of the documented workings (100-ft levels to 457 m; mine pool at ~160 m).

### 5.2 Giza against predictions published before the data
Eight predictions and four falsification conditions were committed before the first Giza scene finished downloading:
- 5 predictions hit, 2 missed and 1 split;
- the three acquisitions agree on peak depth to 0.10 cells (pre-registered repeatability met);
- in plan view over the whole 5674 × 5351 scene (462 tiles), surface brightness shows the plateau, pyramids and city clearly, while depth slices are salt-and-pepper with no morphology.

(Details in v5 §4; carried over unchanged.)

### 5.3 Known voids are not distinguished from bare rock (pre-registered test G)
The Western and Eastern Cemeteries contain hundreds of excavated mastaba shafts 5–30 m deep, beside bare plateau. The test design:
- **Tiles:** cemetery tiles versus bare-plateau tiles in each acquisition, with regions fixed from published maps before any crop was viewed.
- **Matching:** tiles matched on surface brightness.
- **Statistic:** the standardised difference in depth-profile centroid.
- **Reference:** the difference between two halves of the same empty desert.
- **Positive control:** a displacement planted in a quarter of the cemetery tiles before tracking.

A placement check on SLC amplitude alone, before any tomogram was built, led to two recorded amendments:
- one plateau control was dropped because it contained a built compound;
- one scene (02-08) was demoted to secondary because its product geolocation was ~500 m in error (corrected by amplitude registration and excluded from the verdict).

*Table 4 — cemetery vs bare plateau.*

| Scene | Matched tiles | d, cemetery − plateau | d, plateau − plateau | Planted control | Verdict |
|---|---|---|---|---|---|
| 02-07 | 91 | −0.10 | +0.12 | −1.86 | NULL |
| 03-08 (primary) | 469 | −0.03 | −0.14 | −2.03 | NULL |
| 02-08 (secondary) | 61 | +0.30 | −0.28 | −1.50 | excluded by rule |

**Overall: NULL.** The easiest real target on the plateau, hundreds of shallow, surveyed, excavated voids under flat ground, does not move the output relative to bare rock. The planted control shows the test could see a change in the input.

An independent reimplementation reports the same on ICEYE data (+0.031 brightness-matched) [7].

Limitations:
- 02-07 has low power;
- tiles (13–50 m) are much larger than a shaft (1–2 m), so this tests fields of shafts, not single shafts;
- a shaft-centred test needs metre-level registration and is future work.

### 5.4 Nothing in the volumes is shaped like architecture (pre-registered)
A shape statistic was calibrated on synthetic volumes and fixed before any real Giza volume was built:
- median vertical run and connected-component count of the top 1% of voxels;
- scored against a volume built from pure speckle through the identical pipeline;
- 8 rendering treatments, with 5/8 required for "architecture-like".

The real Giza centre crops give 0/8, 4/8 and 0/8, while the same volumes with planted shafts give 8/8.

The single near-miss (02-08) was examined further in a pre-registered follow-up:
- its bright blobs are no more elongated than those of pure noise (median elongation 26 against 26; planted shafts 74–82);
- they are not correlated with surface brightness or registration quality.

It is reported, not explained.

### 5.5 The streaks are not surface-driven either (pre-registered test F)
The most prominent features in single-pass tomograms are vertical streaks. By construction, a tomogram column's energy equals its tile's detrended-trajectory energy (ρ = 1.00). I hypothesised that streaks sit under tiles with poor registration or distinctive backscatter.

**The hypothesis was rejected:** |ρ| ≤ 0.15 against brightness, texture and registration quality in all three scenes, the same as pure noise. A displacement control was recovered 4/4 in every scene.

Which tiles carry large excursions is not predicted by these surface properties. Whether surface scatterer *spacing* sets apparent depth, as simulations suggest [7], is untested on real data (§11).

### 5.6 How large a real signal would need to be
A reflector planted in the Giza image before processing is detected only above 0.2 px, 8.4× the pipeline's own trajectory noise. Below that, a scene containing a genuine reflector reports lower contrast than an empty one: confidence is anti-correlated with truth.

Separately, measured single-pass velocity floors are ~77 µm/s on ICEYE dwells [7], while ambient ground motion is ~0.1–10 µm/s. The motion the deep claims rely on is below what one pass can see.

## 6. Decision statistics are uninterpretable without the full chain
Both of this paper's criteria can be defeated on an input containing no scene by filters applied to each patch independently:
- the ratio test (contrast > 5× the alignment null);
- the surface guard (peak beyond 2 cells).

Specifically:
- **A low-pass filter** drives 97% of empty blocks past the ratio test.
- **A high-pass filter** moves 100% past the guard.
- **A five-tap kernel found by direct search** does both, reporting all 200 empty blocks as detections (98% even against a 95th-percentile null).

A broad survey of 137 operators found almost nothing; only optimisation exposed the failure. The results in this paper stand because no such filter is applied and the chain is published. The general lesson cuts both ways: a confidence figure attached to a tomogram cannot be evaluated against a pipeline nobody can see. That is why the undisclosed settings of the published work matter:
- sub-aperture count;
- overlap;
- taper;
- λ_s;
- estimator;
- rendering.

(Full detail: v5 §5.5, carried over.)

## 7. Where the published imagery's geometry comes from
This section audits published figures, not data. It documents what the images contain and what the authors' own materials state. It makes no claim about intent.

### 7.1 The 2022 paper: a CAD model, tags and overlays (pre-registered)
All 16 figures captioned "Tags association from tomography to 3D model" pair a 3-D model panel with a tomogram panel.

**Measured.** With a detail statistic fixed and validated before the paper was obtained, the model panel carries more independent spatial detail than the tomogram in 15/16 pairs (median 9.7× on arXiv v1, 10.5× on the journal images). The only exception is a heat map laid over an engraving whose hatching supplies the detail.

**By inspection:**
- every tomogram panel is a 2-D colour-mapped image with no axes or scale;
- the link to the model is hand-placed "Tag N" labels;
- 4/16 tomogram panels are heat maps composited over pre-existing drawings or photographs of the known interior.

A 2022 reviewer noted that "none of the tomograms have meaningful axes" [1, review report]. The journal images are pixel-identical to the preprint (r = 1.00); no axes were added. The only axis-labelled tomograms in the section are in pixels, while the CAD model is dimensioned in metres.

This test was weak by design, since a CAD render will beat a heat map on detail. The descriptive findings carry the weight.

### 7.2 The 2026 "Second Sphinx" presentation (pre-registered descriptive audit)
58 slides were published with the author's permission [5]. The audit found:
- **The measured product is unchanged from 2022:** four unscaled 2-D jet heat maps (left, front ¾, right, top). None states a voxel size or threshold. The only metric depth axis in the set (a Great Sphinx figure, 0 to −1200 m) is the frequency-set relabel of §3.3.
- **The 3-D sphinx is built downstream.** The deck's pipeline slide, titled as a dialogue with an AI (Grok), lists "Multi-View Registration & 3D Reconstruction", "Thermal-to-Visible GAN (Pix2Pix / CycleGAN)", "68+ Landmark Detection (DeepFace + MediaPipe)", "Forensic Facial Approximation", "Golden Ratio & Egyptian Canon Grid Analysis" and "ArcFace / Eigenface Embedding".
  - A Pix2Pix/CycleGAN is an image-to-image generator.
  - Face-landmark tools are built to find faces.
- **Face grids are drawn onto the heat maps.** Proportion lines ("linea occhi / base naso / linea bocca"), golden-ratio spirals and head outlines appear on the heat maps. One heat map is perspective-warped onto a photograph of the Great Sphinx (slide image 38; file hashes in runs/press_image_audit.json).
- **The renders carry the known Great Sphinx's form.** Headdress and forepaws are present. The "estimated total length" of 73.0 m is the Great Sphinx's commonly quoted length.
- **The confidence figures are outputs of those tools, not measurements of the ground.** The 96.1%, 94%, 83% and 78% figures are attributed on the slides to Gemini, Grok and a "FusionResNet+GCN". The "blind test" input and prompts are not public.

Three pre-stated expectations were scored:
- no image states both a voxel size and a threshold: hit;
- a 3-D scene shows modelling-software traits: hit (identical helical columns and cubes, grid floor, navigation control);
- the 2-D lines lack metric axes: partial.

### 7.3 Other published imagery
A 2026 post presenting a Titanic "blind test" [6] states in its caption a "structural correlation" of 91.4% between "HarmonicSAR data of the wreck at 3,800 meters" and existing optical imagery. The posted media carries the on-frame label "In-situ Photo Overlay (tilted for alignment)" (recorded 3 Sep 2026; docs/BIONDI_IMAGERY_ANALYSIS_2026-09-03.md §5). The wreck lies under ~3,800 m of seawater, whose microwave penetration depth at X-band is of order millimetres (good-conductor estimate δ = 1/√(πfμσ) ≈ 2.6 mm at 9.6 GHz with σ ≈ 4 S/m). The detail in the frame is the photograph's.

In a 2026 interview the lead author described discarding experiments that "made no sense" because "very often one was inverting noise", and keeping those that "went well" [8]. Discarding low-quality scenes is ordinary practice. With an operator that returns structured output from any input, however, the criterion matters: whether it was fixed before or after the output was seen. Selecting outputs that look sensible afterwards retains false positives preferentially. This also explains why "200 scans agree" (C5) is consistency, not corroboration. Stacking five same-geometry passes over a known-empty open pit reinforces the same surface-pinned peak (v5 §3.5).

### 7.4 What this section does not show
It does not show:
- intent;
- which tool produced which pixel;
- whether anything lies beneath the mound.

It shows that the recognisable geometry in the published imagery is not derivable from the displayed tomography. It enters through models, drawings, photographs, templates and AI tools, several of them named by the authors.

## 8. Independent work
Three independent efforts reach the same conclusion by different routes, and one supporter-side effort documents the method's missing details:
- **Pomposi (Zenodo, April 2026)** [9]: a geometric argument that single-pass sub-apertures give an elevation resolution of order 285 m, and a Giza-versus-desert sweep finding no target-specific discrimination.
- **ejhong, "SAR Depth, Tested" (GitHub, September 2026)** [7]. A reimplementation via the paper's K_z form on two ICEYE Spotlight Dwell acquisitions (Giza and Sacsayhuamán), not peer reviewed. Its findings:
  - a periodic depth axis;
  - monuments indistinguishable from desert on two continents;
  - no signal at surveyed cemetery shafts;
  - coherence halving at ~1 s;
  - a seismic-array cross-correlation test finding no propagating wavefield (0.004 against 0.49 for an injected wave);
  - an analytic lateral resolution bound of ≥ 27–52 m.

  Its data are not public; ours are.
- **"Biondi Protocol" derivative package (GitHub)** [10]: a supporter-side reconstruction that states that "several pieces of information" needed to reproduce the method were not published. It was revised in September 2026, adding a 5% maximum look-overlap gate and per-pair orbit baselines.

Two independent formulations reach the same result on separate data and sensors: the patent's DFT with adjacent tracking (this work) and the paper's K_z with common-reference tracking [7]. The periodic, freely scaled depth axis and the absence of site discrimination are therefore properties of the method, not of one implementation.

## 9. What is real, and what would change this conclusion
**What is real.** Sub-aperture tracking measures real surface motion where motion is strong and coherent: vessels, bridges, and dams driven by traffic or machinery [11]. That front end stands. It measures the vibrating surface itself; it does not image what lies beneath. Giza is quarried limestone on limestone bedrock with no strong driving source, so its ambient motion lies below the demonstrated single-pass sensitivity.

**What would change this conclusion.** A minimal, public demonstration would need four things:
1. The processing parameters for one published Giza result are disclosed: sub-aperture count, overlap, taper, estimator, λ_s or f, and scene identifier.
2. On a separate public scene containing a surveyed void, the same configuration places a peak at the surveyed depth, and not merely at an alias of the ~1.7-cell surface peak.
3. That peak survives an alignment null and a de-accumulation control.
4. A third party reproduces it from the published configuration.

I would withdraw this paper's conclusion on that evidence. The repository is open for it.

## 10. Revision history
v1–v5 corrections and withdrawals are listed in full in the repository (v5 §10):
- the 1720× and 194× figures;
- the Komati row;
- the claim that the images are the rendered artifact;
- the anti-conservative look-shuffle null;
- two abandoned mechanism accounts;
- three analysis-code verdict messages that stated a preferred answer.

v6 adds:
- **Tests F, G, H** and the shape-metric application (§§4.3, 5.3–5.5).
- **The K_z-ladder and look-similarity measurements** (§§3.2, 4.1).
- **The image audits** (§7).
- **A withdrawn explanation.** The explanation that overlap-correlated increments cause the residual pinning is withdrawn: test H found the increments uncorrelated.
- **A rejected hypothesis.** The hypothesis that streaks are surface-driven was rejected by its own pre-registered test.
- **One superseded open item.** v5's statement that the §7 imagery question could not be tested is superseded by §§5.4 and 7.

## 11. Limitations and open items
- All sites are X-band spotlight; nothing here bears on C- or L-band.
- The residual surface-ward lean after de-accumulation at two Giza scenes (§4.3) is unexplained.
- Look similarity (§4.1) is measured on magnitudes. Complex coherence and the estimator's correlation-peak height on the same pairs remain to be reported.
- Test G tests fields of shafts at tile scale (13–50 m). A shaft-centred, alias-checked version needs metre-level registration.
- Whether surface scatterer spacing sets apparent depth (or alias position) on real data is untested.
- The decision-rule attack (§6) is on synthetic input with linear per-patch filters of length ≤ 5.
- One secondary scene (02-08) had a ~500 m geolocation error, found and corrected before analysis. Earlier tests used scene-centre crops and are unaffected.
- The author's undisclosed settings may differ from any bank tested here (§3.2). The conclusion concerns the method as published.

## 12. Conclusion
Rebuilt from its own paper and patent, single-pass SAR Doppler micro-motion tomography produces the following, on free data anyone can re-run:
- **A depth axis that is a Fourier bin.** Its metre scale is set by an unmeasured frequency, and it changes with viewing geometry.
- **A confident, shallow peak at 1.2–1.9 resolution cells at every site,** for which accumulated noise is a sufficient generator (reproduced without satellite data), though not shown to be the necessary cause on two Giza scenes.
- **No response to voids known to be there.**
- **No architecture-like shape** in the reconstructed volumes.

The recognisable shafts, chambers and faces of the published imagery come from sources other than the displayed tomography: CAD models, drawings, photographs, face templates and AI tools, several of them listed by the authors. One small residual in the mechanism remains open and is reported as such.

The 2022 article was retracted without an itemised reason. This paper offers the specific, testable version: the defects are located, and each can be reproduced from the repository. The surface-motion measurement at the method's front end is real and useful for monitoring. The deep inference built on it is not supported.

---

**Data and code availability.** All scenes are Umbra and Capella Open Data (CC-BY 4.0); identifiers are in the repository. Code (MIT), pre-registrations, result files and figure scripts: github.com/Hassanforeman/subsurface-sar-tomo; Zenodo 10.5281/zenodo.21065675. Third-party figures and slides were analysed under fair use and are not redistributed.

**Conflict of interest.** None, financial or non-financial.
**Funding.** None.
**Use of artificial intelligence.** Large language models assisted with software development, analysis and drafting, and one (Grok) was used adversarially to source leads and attack results. Every lead was checked against primary sources; claims not verified are labelled or omitted. The author directed the research, made all scientific decisions, verified every output and is accountable for the content. No figure is AI-generated.

## References
[1] Biondi, F. & Malanga, C. (2022). Synthetic Aperture Radar Doppler Tomography Reveals Details of Undiscovered High-Resolution Internal Structure of the Great Pyramid of Giza. *Remote Sensing* 14(20):5231; arXiv:2208.00811. **Retracted** 10 Aug 2026, *Remote Sensing* 18:2679 (doi:10.3390/rs18162679). Public peer-review report at mdpi.com/2072-4292/14/20/5231/review_report.
[2] Biondi, F. (2022). Scanning Inside Volcanoes with SAR Echography Tomographic Doppler Imaging. *Remote Sensing* 14(15):3828.
[3] Patent WO2024008365A1 (PCT/EP2023/064345; ceased). Tomographic Doppler imaging.
[4] Khafre Research Project (2025). Press presentations on structures beneath the Khafre pyramid (not peer reviewed).
[5] Biondi, F. & Malanga, C. (2026). "Giza — La città nascosta: Atto finale", presentation slides, 21 June 2026, published with permission at archaeologicalrescue.org/secondsphinx (T. Grassi, 26 Jun 2026).
[6] Biondi, F. (2026). Post on X, 15 Aug 2026, x.com/Filippobiondi_1/status/2088558729146830895.
[7] ejhong (2026). SAR Depth, Tested. ejhong.github.io/sar; github.com/ejhong/sar (not peer reviewed).
[8] Biondi, F. (2026). Podcast interview (Italian), transcript and translation in the repository (docs/BIONDI_PODCAST_2026-07-16.md). [confirm citation form]
[9] Pomposi, S. (2026). Independent Reproduction Attempt of SAR Doppler Tomography for Subsurface Imaging of the Great Pyramid of Giza. Zenodo 10.5281/zenodo.19574701.
[10] BiondiProtocol (2026). Replication-and-Verification-Biondi-Protocol, github.com/BiondiProtocol/Replication-and-Verification-Biondi-Protocol (v1.5, v1.7).
[11] Milillo, P. et al. (2016). Space geodetic monitoring of engineered structures: the Mosul Dam. *Scientific Reports* 6:37408.
[12] Retraction Watch (2026). Journal retracts paper claiming network of corridors inside the Great Pyramid of Giza, 31 Aug 2026.
[13] Umbra Open Data; Capella Open Data — AWS Registry of Open Data (CC-BY 4.0).
[14] Butte district mine maps: Montana Bureau of Mines & Geology; USGS I-2050-C; OSMRE National Mine Map Repository.

## Appendix A — claim-to-evidence map
| Claim | Script | Result file | Pre-registration |
|---|---|---|---|
| K_z ladder is a DFT; depth scale free (§3.2) | src/kz_ladder_umbra.py | runs/kz_ladder_umbra.json | descriptive |
| Look similarity (§4.1), known voids (§5.3) | src/known_voids_umbra.py | runs/known_voids_umbra.json | docs/PREREGISTRATION_KNOWN_VOIDS_2026-09-27.md |
| Increments residual (§4.3) | src/increments_order_null.py | runs/increments_order_null.json | docs/PREREGISTRATION_INCREMENTS_2026-09-27.md |
| Shape metric on Giza (§5.4) | src/shape_metric_giza.py | runs/shape_metric_giza.json | docs/PREREGISTRATION_MINES_AND_GRANSASSO.md §C |
| Streaks vs surface; near-miss (§5.4–5.5) | src/streak_surface.py | runs/streak_surface.json | docs/PREREGISTRATION_STREAKS_2026-09-27.md |
| 2022 figures (§7.1) | src/figure_information*.py, src/figure_layout.py | runs/figure_information*.json | docs/PREREGISTRATION_FIGURES_2026-09-27.md |
| 2026 slides (§7.2) | src/press_image_audit.py | runs/press_image_audit.json | docs/PREREGISTRATION_PRESS_IMAGES_2026-09-27.md |
| Six-site table, mechanism, decision-rule attack (§§4.2, 5.1, 6) | see v5 Appendix / docs/STATE.md §1 | runs/ | docs/PREREGISTRATION_GIZA_2026-08-13.md |
