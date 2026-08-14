# Giza plateau — complete results, 13 August 2026

**The first time this reproduction has been run on the site the original claim is
about.** Predictions were pre-registered and pushed at `e4476d7` before the scene
had finished downloading. Scored in `PREREGISTRATION_GIZA_2026-08-13.md`.

## 1. The scene

Umbra Open Data, CC-BY 4.0, task `sar-data/tasks/ad hoc/Pyramids of Giza/`.
The task is filed under the catch-all collection, not as a named location, which is
why place-name searches of the bucket return nothing. `fetch_giza.sh` records the
correct path.

| | |
|---|---|
| Collect | `7e7cd796-3842-4923-8b48-4c0950ece945` |
| Acquisition | `2023-02-07-07-58-27_UMBRA-05`, SICD, 240 MB |
| Array | 5674 x 5351 |
| Azimuth / range sample spacing | **0.827 m / 0.472 m** |
| Centre frequency | 9.475 – 9.725 GHz (X-band) |
| **Collect duration** | **1.27 s** |
| Scene centre | 29.97930 N, 31.13399 E, 79.8 m |
| `dz_phys` at v=6000, f=22000 | 2.11 m |

Two further Giza acquisitions were downloaded and are not yet analysed:
`2023-02-08-07-54-55_UMBRA-04` (256 MB) and `2023-03-08-07-57-53_UMBRA-04`
(1.70 GB — the scene Pomposi used).

## 2. Sub-aperture ladder — the headline result

**8/8 surface-pinned. 0/8 detections above 5x. Peak 1.52 – 1.75 resolution cells.**

| `n_sub` | native C | fixed-window C | shuffle | alignment | C/align | peak m | peak cells | guard |
|---|---|---|---|---|---|---|---|---|
| 11 | 6.06 | 6.06 | 1.48 | 1.65 | 3.67 | 3.7 | 1.75 | PIN |
| 16 | 4.69 | 3.27 | 1.42 | 1.52 | 2.15 | 3.6 | 1.71 | PIN |
| 22 | 8.56 | 4.16 | 1.47 | 1.72 | 2.42 | 3.5 | 1.66 | PIN |
| 32 | 23.65 | 6.26 | 1.47 | 1.82 | 3.43 | 3.5 | 1.66 | PIN |
| 45 | 37.95 | 4.37 | 1.45 | 1.72 | 2.54 | 3.5 | 1.66 | PIN |
| 64 | 6.99 | 3.82 | 2.24 | 2.77 | 1.38 | 3.2 | 1.52 | PIN |
| 90 | 17.19 | 4.27 | 2.41 | 2.84 | 1.51 | 3.2 | 1.52 | PIN |
| 128 | 108.90 | 3.29 | 1.57 | 1.80 | 1.82 | 3.6 | 1.71 | PIN |

Native spread 23.2x; fixed-window spread 1.9x — identical to Komati and Bingham.

Giza returns the same peak, at the same depth in resolution cells, as an open-pit
copper mine in Utah, a coal-fired power station in South Africa, a hard-rock mining
district in Montana, an active volcano in Italy and central Cairo.

## 3. E8 — the cumulative sum, with a correction to the printed verdict

| input | series | raw lag-1 | peak cells | contrast | pinned |
|---|---|---|---|---|---|
| real | cumsum (as published) | 0.547 | 1.75 | 6.06 | PIN |
| real | increments | 0.087 | 1.88 | 1.86 | **PIN** |
| noise | cumsum | 0.507 | 1.71 | 3.75 | 100% |
| noise | increments | -0.041 | 2.80 | 1.49 | 31% |

Contrast collapses 6.06 -> 1.86 and lag-1 collapses 0.547 -> 0.087, both as at every
other site.

**The peak does NOT move off the surface on Giza** — 1.75 -> 1.88 cells, still
pinned. At Bingham it went 1.66 -> 2.83 and cleared; at Capella 1.69 -> 4.76 and
cleared.

> **The verdict this experiment prints — "Removing the cumulative sum MOVES the peak
> away from the surface" — is FALSE for this run.** It is hard-coded and does not
> read the row. This is the THIRD verdict-printer in this repository to state a
> conclusion its own data does not support (E7's overlap message, E11's bin message,
> now E8's). All three must be disclosed in the revision history.

Giza's increments retain positive autocorrelation (0.087) where noise gives -0.041.
**Unexplained.** Two candidate accounts were tested and both failed: see section 6.

## 4. Window taper — an undisclosed parameter worth 34%

| window | lag-1 | contrast | C/align |
|---|---|---|---|
| blackman | 0.076 | **4.69** | 2.87 |
| hann (default) | 0.083 | **6.06** | 3.67 |
| hamming | 0.092 | 4.52 | 3.08 |
| rect | 0.108 | 5.03 | 3.32 |

Correlation between inter-look lag-1 and the statistic: **-0.059** — no relationship.

Giza's contrast of 6.06, the highest of any site tested, is **largely a window
choice**. Under Blackman the same scene gives 4.69, alongside Vesuvius at 4.11.
The taper is not stated in the 2022 paper, the patent, or any presentation, and it
moves the headline number by 34% on this scene.

## 5. Full pipeline, and the figure

```
mean registration quality: 0.68
REAL tomogram contrast 6.1x; shuffle null 1.8x; ALIGNMENT null 1.6x -> 3.73x
VERDICT: INDISTINGUISHABLE FROM NULL
NEAR-SURFACE GUARD (absolute): peak at 3.7 m; threshold 4.2 m -> ARTIFACT-SUSPECT
  legacy 5%-of-axis rule: peak at 32% of axis -> ok   [DISAGREES]
HARDENED POSITIVE CONTROL (damped): PASS
SURFACE-LEAKAGE: corr = 0.07
```

Registration quality 0.68 is middling for this study (Cairo 0.62, Bingham 0.67,
Vesuvius 0.72, Butte 0.82, Komati 0.85). Giza is not an unusually good radar scene.

**`runs/tomogram_giza_2023-02-07_UMBRA-05_SICD.nitf.png` is the clearest figure in
the project.** Real and shuffled-null panels are visually indistinguishable — same
blobs, no structure. The injected positive control produces a *continuous horizontal
band across every patch at one depth*, which is what a coherent reflector looks
like. Giza has nothing resembling it.

The legacy guard disagreeing with the absolute guard on this scene is a concrete
illustration of why the guard was replaced.

## 6. Plan-view map — the surface is visible, the depth is not

`planview_map.py`, whole scene, 22 x 21 tiles, patch 64, stride 256.

| | |
|---|---|
| corr(surface brightness, power at 1.7 cells) | **-0.180** |
| corr(surface brightness, power at 5.5 cells) | **-0.162** |
| peak depth across 462 tiles | median 2.08 cells, 5–95 pct 1.51 – 4.38 |

The surface-brightness panel resolves the scene plainly — plateau and desert west,
city east, linear features. **Both depth panels are salt-and-pepper with no
morphology at all.** Correlation is slightly negative, not merely absent.

**Consequence.** A faithful reproduction of the published method produces depth
products containing *zero* surface morphology. If the published depth products do
show pyramid morphology, then either the pipeline used differs from the one
described, or the recognisable structure enters through the CAD-model panel rather
than the tomogram panel. The figures at issue (34–50) carry the caption "Tags
association from tomography to 3D model. (a): 3D model of Khnum-Khufu. (b):
Tomographic reconstruction (magnitude)." This cannot be settled without the original
figures or code, and no claim beyond that is made here.

## 7. E12 — the detection floor on real data, and a statistic that runs backwards

Baseline trajectory RMS on this scene: **0.02372 px**.

| planted amplitude | x noise floor | peak cells | contrast | target found |
|---|---|---|---|---|
| none | 0 | 1.75 | **6.06** | 0% |
| 0.01 px | 0.4 | 1.75 | 6.12 | 0% |
| 0.02 px | 0.8 | 1.75 | 6.06 | 0% |
| 0.05 px | 2.1 | 1.75 | 4.69 | 0% |
| 0.10 px | 4.2 | 1.73 | **3.39** | 0% |
| **0.20 px** | **8.4** | **3.16** | 5.40 | **100%** |
| 0.50 px | 21.1 | 3.18 | 13.69 | 100% |

**Detection floor: 0.2 px of per-look displacement, 8.4x the pipeline's own noise
floor.** Harder than the synthetic scene, which needed 0.1 px at 5.1x.

**A scene containing a genuine reflector at 4.2x the noise floor reports a LOWER
contrast (3.39) than a scene containing nothing at all (6.06).** Over the range where
a real archaeological feature would sit, the statistic moves in the wrong direction.
That is worse than failing to detect: it is anti-correlated with truth.

### Converting the floor to ground motion — NOT YET DONE

0.2 px x 0.827 m = **0.165 m of apparent azimuth shift**. Converting that to physical
ground displacement is **not** a multiplication. In SAR, a target moving during the
collect is displaced in azimuth by approximately `(R/V) * v_LOS` — the image shift
maps to a line-of-sight *velocity*, not a displacement. Done properly with `ARPVel`
and the true slant range this is likely to come out around a few mm/s, i.e. tens of
microns of displacement at seismic frequencies — one to two orders of magnitude above
ambient microseism, not the four or five a naive conversion suggests.

**Do not publish a metres-of-ground-motion figure until that geometry is worked
through.** The naive version is wrong and a referee would demolish it.

## 8. An observation from the header that needs checking

Collect duration is **1.27 s** and the method takes **11 sub-apertures** — eleven
temporal samples of the scene across the collect, a rate of about 8.7 Hz, Nyquist
about 4.3 Hz. The claimed investigation frequency is **22,000 Hz**.

On its face the measurement cannot observe a 22 kHz process, by a factor of several
thousand. This would sit alongside the existing finding that `f` never enters the
inverter. **Flagged for verification, not asserted** — an earlier Nyquist argument in
this project was wrong and was withdrawn.

## 9. Attempted recreation of the published imagery — NEGATIVE RESULT

Three renderings were built from a volume containing no data at all
(`volume_render.py --source noise`):

1. `n_sub` = 11, voxel scatter — vertical needles at a single depth.
2. `n_sub` = 11, isosurface — discrete solid bodies in a shallow slab, 1–4 cells.
3. `n_sub` = 128, isosurface — a continuous planar sheet spanning the whole site.

**None resembles the published figures.** No shafts, no vertical extent, no spirals,
no architecture. **The appearance of the published imagery was not reproduced.**

This supports rather than weakens the manuscript's existing limits paragraph. It is
also a finding in its own right: the 2022 paper documents no part of its 3-D
visualisation pipeline — no rendering method, no isosurface, no threshold, no dynamic
range, no colour scale, no denoising — so those figures are not reproducible even in
principle. That belongs with the undisclosed sub-aperture count, window taper and
overlap.

**Consequence for public statements.** "The same result from random numbers" is
established for the peak, the depth and the contrast. It is **not** established for
the images. Never say "the same images".

## 10. Open items

- **Giza's increments arm stays surface-pinned** (1.88 cells, lag-1 0.087). Both
  proposed explanations failed: registration quality is ordinary at 0.68, and surface
  leakage is 0.07 in the crop and -0.18 across the scene.
- The `n_sub` 64 and 90 rows carry elevated nulls (2.24, 2.41 against ~1.45
  elsewhere). Not investigated.
- Two further Giza acquisitions downloaded and unanalysed — the within-site
  repeatability prediction is untested.
- The azimuth-shift-to-ground-motion geometry (section 7).
- The sampling-rate observation (section 8).
- Three verdict printers to correct: E7, E11, E8.
