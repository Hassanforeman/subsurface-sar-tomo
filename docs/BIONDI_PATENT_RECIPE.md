# Biondi's Disclosed Recipe — from the Patent (WO2024008365A1 / PCT EP2023/064345)

*Mined from the patent text — the fullest public method disclosure (more authoritative than the
1.5-hour talk, which we could not transcribe; the patent supersedes it for the actual recipe).
Verbatim quotes in quotation marks.*

---

## The headline: the "steering matrix" is just a DFT

The single most important disclosure, in his own patent:

> "the steering matrix A(K_Z, z) represents the best approximation of a matrix operator performing
> the Digital Fourier Transform (DFT) of Y."

and the depth-focusing step:

> "The focus of the raw tomographic signal is made by computational block 9, representing the DFT
> mathematical operator."

**There is no sophisticated hidden inversion.** Depth is obtained by taking a **DFT of the
pixel-tracking vibration vectors** along the tomographic direction. That is *exactly* what our
`tomogram.py` already does (`steering()` is a DFT basis; `invert_patch` is its power spectrum). So
our pipeline is a faithful reproduction of his disclosed core — we are not missing a magic operator.

This also answers "he's not pulling the tomograms out of nowhere": correct — he's pulling them out
of a **DFT**, which is mathematically guaranteed to produce a structured-looking spectrum from *any*
input vector, real subsurface signal or not. That is precisely the confident-artifact failure mode
we demonstrated in `steering_stress_test.py`.

## The full processing chain (patent Fig. 0.5, blocks 1–11)

1. SLC SAR image →
2. 2-D DFT (DFT2) →
3–4. generate two **Doppler sub-apertures** (a "master"/black and "slave"/blue sub-band of the
   spectrum) →
5–6. inverse DFT2 back to two lower-azimuth-resolution SLCs →
7. **pixel-tracking** between them ("for all those pixels for which tomography needs to be
   trained") →
8. complex vectors = "raw tomographic complex data" →
9. **DFT** → focus in depth/elevation →
10. tomogram →
11. geocode to 3-D coordinates.

This is our exact chain (sub-aperture → pixel-track → DFT-in-depth), plus an explicit **master/slave
range-Doppler sub-band** structure.

## What he does that we don't (the real gaps)

1. **Multichromatic / range (chirp) sub-banding.** The patent builds "range-Doppler sub-apertures
   large-matrix" for a master and a slave — i.e. it splits **both** the chirp (range) **and** the
   Doppler (azimuth) bands. We currently use Doppler sub-apertures only. This is the one genuine
   processing piece we're missing (the MCA axis).
2. **N_D as the vibration sampling rate.** "N_D represents the sampling-rate of the mechanical wave
   existing on the Earth that we are observing digitally" — the number of sub-apertures sets the
   temporal sampling of the vibration. (Matches our interpretation; ties directly to our
   sub-aperture-count stability guard.)
3. **Single OR multiple images.** "estimates the micro-motion … processing a single **or multiple**
   SAR images" — multi-image (the 200+ stack) is within scope and used for diversity/confirmation,
   but the core depth step works per-image.

## The weak link he discloses himself: 22 kHz

> "synthesized at 22 kHz … the maximum observable frequency of investigation (approximately
> 22000 Hz)."

The depth resolution δz = λR/2A uses λ = v_seismic / f with **f ≈ 22,000 Hz**. That is an
**ultrasonic** frequency. Ambient/seismic ground motion is overwhelmingly **sub-100 Hz**; there is
no mechanism for a satellite imaging a ~3 s dwell to observe a coherent 22 kHz elastic wave in rock
(it would attenuate within metres, and it is orders of magnitude above the sub-aperture pair-axis
Nyquist — the violation the independent reproductions flagged). **This single assumption is what
manufactures the fine depth resolution and the kilometre-deep features.** Drop f to a physical
seismic value and the resolution/penetration claims collapse.

## Band independence (confirms our physics)

> "any satellite and airborne … any transmission frequency, and any chirp-Doppler bandwidths."

His own patent says the radar band is not the differentiator and that airborne is in scope — exactly
our position ("Ku for resolution is wrong"; the drone win is geometric aperture, not band).

---

## Implications for our project

1. **We already reproduce his core** (sub-aperture pixel-track + DFT). Our nulls are therefore a
   reproduction of *his disclosed method*, not a strawman — strengthens the paper.
2. **Decisive experiment now available:** add the **master/slave range sub-banding (MCA)** and run
   the inversion **with his own parameters (f ≈ 22 kHz)**. Prediction: we will reproduce his kind of
   dramatic deep "structure," and our controls (sub-aperture-count stability, ground truth at Butte,
   leakage) will expose it as a DFT artifact. That is a clean, publishable demonstration of *how* the
   confident-but-unreal tomograms arise.
3. **The honest one-liner:** the secret sauce is not a clever inversion — it's a DFT relabelled as a
   steering matrix, fed a physically impossible 22 kHz investigation frequency, run over a big image
   stack for apparent consistency. Real math; unphysical assumption; guaranteed to look like structure.

### Sources
- [Patent WO2024008365A1 (Google Patents)](https://patents.google.com/patent/WO2024008365A1/en) — PCT/EP2023/064345, filed 29 May 2023 (legal status: ceased/lapsed).
- Corroborating: Biondi & Malanga 2022 (arXiv:2208.00811); Joe Rogan #2443 ("more than 200" scans); Pilicy appraisal (Graham Hancock, 2025).
