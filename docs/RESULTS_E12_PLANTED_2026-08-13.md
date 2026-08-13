# E12 — the planted-SLC positive control. Run, and it is decisive.

*13 August 2026. `src/experiment_e12_planted.py`, self-test passing, results in
`runs/e12_planted_synthetic_{tone,damped}.json`.*

**Status: run on synthetic band-limited speckle (bw_frac 0.80, matching the measured occupied
bandwidth of the real scenes). Not yet run on a real SICD.** The real-scene run is one command once
the Giza scene is downloaded, and it converts the headline number from pixels into metres.

---

## 1. What was wrong with the old positive control

The manuscript's "in-data positive control" is `inject_reflector()`:

```python
return obs + amp * np.cos(Kz * z_inject)
```

It adds a tone to `obs` — the trajectory vector — **after** the cumulative sum and **after** the
degree-2 detrend, written **on the steering matrix's own basis**. It shows the inverter can recover a
tone written in its own coordinates. Since E9 established that the SAR front-end is not even
necessary to produce the artifact, a control that bypasses the front-end entirely proves nothing
about whether a physical signal could survive it. Adversarial review called this self-flattering.
It was.

## 2. What E12 does instead

Each sub-aperture look is **physically shifted in the image domain** by a sub-pixel amount, so the
displacement must be *recovered by the pipeline's own magnitude cross-correlation estimator, from
speckle, through the window taper*, before it is accumulated, detrended and inverted. Nothing
downstream is touched. A reflector at relative depth *z* produces, under the method's own forward
model, a per-look trajectory `D_k = A·cos(Kz[k]·z)`; that is exactly what is imposed, coherently
across all 24 patches.

Two waveforms are run: the **matched tone**, and a **damped** variant deliberately off the steering
basis so the test cannot be accused of handing the inverter its own eigenvector.

**Amplitudes are calibrated against the pipeline's own residual RMS**, per adversarial review — *"design
the amplitude against the pipeline's own residual RMS, not against a displacement that would light up
any tracker."* The unplanted trajectory RMS is measured per scene and every amplitude is reported as
a multiple of it. Measured here: **0.01957 px**.

### Self-test, all passing

| | |
|---|---|
| [A] planted displacement recovered by the front-end | corr **0.995** |
| [B] amp = 0 is a bit-exact no-op | PASS |
| [C] the artifact is present in the unplanted control | peak **1.67 cells** |
| [D] the plant is per-look and localised | PASS |
| [E] **front-end recovery scale at 0.5 px** | **0.124 — only 12% of the planted amplitude survives to the trajectory** |

**[E] is a finding, not a bug**, and it is reported rather than asserted away: the front-end
*attenuates* sub-pixel displacement by roughly eightfold before the inversion ever sees it.

---

## 3. Results — matched tone, planted at 3.30 cells

| amp (px) | × walk RMS | peak cells | 5–95 pct | contrast | found target | pinned | P(tgt)/P(pk) |
|---|---|---|---|---|---|---|---|
| 0.0000 | 0.0 | 1.67 | 1.63 – 1.77 | 3.84 | 0% | **100%** | 0.330 |
| 0.0050 | 0.3 | 1.73 | 1.67 – 1.79 | 4.40 | 0% | 100% | 0.274 |
| 0.0100 | 0.5 | 1.77 | 1.64 – 2.28 | 3.52 | 8% | 92% | 0.382 |
| 0.0200 | 1.0 | 1.69 | 1.64 – 1.95 | 3.66 | 0% | 92% | 0.358 |
| 0.0500 | 2.6 | 1.71 | 1.64 – 2.35 | 3.41 | 8% | 92% | 0.529 |
| **0.1000** | **5.1** | **3.13** | 1.71 – 3.17 | 3.18 | **83%** | 17% | 0.936 |
| 0.2000 | 10.2 | 3.15 | 3.13 – 3.20 | 6.72 | 100% | 0% | 0.947 |
| 0.5000 | 25.6 | 3.16 | 3.15 – 3.18 | 13.88 | 100% | 0% | 0.950 |
| 1.0000 | 51.1 | 3.18 | 3.16 – 3.20 | 5.23 | 100% | 0% | 0.973 |
| 2.0000 | 102.2 | 3.15 | 3.14 – 3.16 | 11.22 | 100% | 0% | 0.939 |

**Detection floor: 0.1 px of per-look displacement — 5.1× the pipeline's own trajectory RMS.**

## 4. Results — damped, off the steering basis

| amp (px) | × walk RMS | peak cells | 5–95 pct | contrast | found target | pinned |
|---|---|---|---|---|---|---|
| 0.0000 | 0.0 | 1.67 | 1.63 – 1.77 | 3.84 | 0% | 100% |
| 0.0200 | 1.0 | 1.73 | 1.67 – 1.79 | 4.31 | 0% | 100% |
| 0.0500 | 2.6 | 1.75 | 1.64 – 2.28 | 3.22 | 8% | 92% |
| 0.1000 | 5.1 | 1.73 | 1.66 – 3.14 | 3.32 | 25% | 75% |
| **0.2000** | **10.2** | **3.05** | 1.61 – 3.13 | 3.01 | **67%** | 33% |
| 0.5000 | 25.6 | 3.13 | 3.10 – 3.15 | 6.11 | 100% | 0% |
| 1.0000 | 51.1 | 3.13 | 3.09 – 3.15 | 7.88 | 100% | 0% |
| 2.0000 | 102.2 | 2.92 | 2.92 – 2.96 | 2.13 | 100% | 0% |

**Off-basis floor: 0.2 px — 10.2× the walk RMS**, twice the matched-tone floor, exactly as expected.

---

## 5. What this establishes — and it is not what I predicted

**The method DOES have a real detection channel.** Plant a large enough displacement and the
inversion finds it at the right depth, cleanly and repeatably (3.13–3.18 cells against a planted
3.30). **That is a point in the method's favour and it must be reported as such.** The dossier's
prediction that a planted signal might never survive was wrong.

**But the failure mode is worse than "it cannot see."** Look at the contrast column across the
sub-floor rows:

| condition | peak | contrast | pinned |
|---|---|---|---|
| no signal at all | 1.67 | **3.84** | 100% |
| real reflector present at 2.6× the noise floor | 1.71 | **3.41** | 92% |

**A scene with a genuine reflector below the floor is indistinguishable from a scene with nothing in
it — and both return a confident, surface-pinned peak at ~1.7 cells.** The method does not fail
silently. It fails by reporting a detection at the wrong depth with the same confidence either way.
Nothing in the published pipeline separates these two cases.

That is a sharper statement than "noise reproduces the output," because it now covers the case the
method's defenders care about: *a scene that really does contain something.*

**Third point, from self-test [E]:** the front-end passes only ~12% of a sub-pixel displacement
through to the trajectory. Any real signal is attenuated eightfold *before* it has to compete with
an artifact that the pipeline generates at full strength.

---

## 6. The number this becomes on a real scene — run this next

The floor is currently in **pixels**, because synthetic speckle has no pixel spacing. A real SICD's
metadata carries the azimuth pixel spacing, so:

> **required ground displacement = detection floor (px) × azimuth pixel spacing (m)**

For X-band spotlight at typical spacings this lands in the **centimetre** range. Ambient seismic
micro-motion — the mechanism the method claims to exploit — is **micrometres to millimetres**.

If that holds on the real Giza scene, the conclusion is a physical one that needs no null model, no
contrast statistic and none of E6–E11:

> *The displacement required to beat the artifact is orders of magnitude larger than the ambient
> seismic motion the method claims to be measuring.*

**Do not write that sentence until it has been run on a real SICD with real pixel spacing.** Write
the threshold down first, as with the Giza predictions.

---

## 7. Caveats, stated plainly

1. **Synthetic scene only.** Band-limited to the measured 0.80 occupied bandwidth, but not a real scene.
2. **The plant is coherent across all 24 patches** — the most favourable case for detection. A real
   reflector illuminating only part of the scene would have a *higher* floor, so this is conservative.
3. **One depth (3.30 cells), one `n_sub` (11), 12 trials per amplitude.** Sweep depth and `n_sub`
   before the number goes in the manuscript.
4. **Contrast is non-monotone in amplitude** (13.88 at 0.5 px, 5.23 at 1.0 px, 11.22 at 2.0 px).
   Not investigated. Likely aliasing of the planted tone against the sub-aperture spacing at large
   shifts. State it; do not quote a contrast-vs-amplitude trend.
5. **The recovered depth is biased low** — 3.13–3.18 cells against a planted 3.30, about 4%. Not
   investigated.
6. The estimator is magnitude-based; see the Table 1 disclosure note.

## 8. Commands

```
python3 src/experiment_e12_planted.py --selftest
python3 src/experiment_e12_planted.py --amps 0 0.005 0.01 0.02 0.05 0.1 0.2 0.5 1.0 2.0 --n-trials 12
python3 src/experiment_e12_planted.py --waveform damped --amps 0 0.02 0.05 0.1 0.2 0.5 1.0 2.0 --n-trials 12
python3 src/experiment_e12_planted.py --sicd data/<giza>_SICD.nitf --amps 0 0.01 0.02 0.05 0.1 0.2 0.5 --n-trials 8
```
