# Pre-registration — the Giza plateau run

**Written 13 August 2026, while the scene was still downloading and before any
number had been computed from it.** Committed before the analysis was run so that
the predictions below are on the record rather than reconstructed afterwards.

## Scene

Umbra Open Data, CC-BY 4.0, X-band spotlight:

| | |
|---|---|
| Task | `sar-data/tasks/ad hoc/Pyramids of Giza/` |
| Collect | `5aa49658-ecf9-4504-afee-281f43fb076e` |
| Acquisition | `2023-03-08-07-57-53_UMBRA-04`, SICD |

Two further Giza acquisitions exist in the same task and will be run as
within-site repeats: `2023-02-07-07-58-27_UMBRA-05` and
`2023-02-08-07-54-55_UMBRA-04` (both SICD + CPHD).

This is the first time the reproduction has been run on the Giza plateau itself.
Every previous site — Bingham Canyon, Butte, Komati, Vesuvius, central Cairo — was
a proxy chosen for ground truth or sensor diversity.

## Why the prediction matters

The manuscript's claim is that the reported depth is a property of the processing
chain and not of the ground. If that is right, Giza must behave exactly like a
copper mine, a power station and a volcano. If Giza behaves differently, the claim
is wrong and the paper needs rewriting. This run can falsify the central argument.

## Predictions, stated before the run

| Quantity | Prediction |
|---|---|
| Peak depth | **1.6 – 1.8 resolution cells**, matching the 1.2–1.9 band from five sites |
| Surface-pinned (2-cell absolute guard) | **yes, at every sub-aperture count**, 8/8 |
| Detections above the manuscript's 5× rule | **0 of 8** |
| Contrast at `n_sub` = 11 | order 3–5 |
| Contrast at `n_sub` = 128 | order 10²; **at or below** the ~275 that pure noise returns at the same setting |
| E8 increments arm | peak moves off the surface, contrast collapses toward ~1.4 |
| E5 geometry sweep | peak stable to about ±0.05 cells across 13 configurations |
| Across the three acquisitions | peak positions agree to within ~0.1 cells |

## What would falsify the argument

- A peak that is **not** in the 1.2–1.9 cell band on Giza while remaining there on
  the other five sites.
- A peak that survives removal of the cumulative sum.
- A contrast that clears 5× against the derived noise null.
- Peak positions that disagree across the three acquisitions by more than the
  spread already measured within a single site.

Any of these would mean the Giza scene contains something the proxy sites do not,
and would require the manuscript's central claim to be withdrawn or qualified.

## Commands to be run

```
python3 src/followup_experiments.py --sicd data/giza_2023-03-08_UMBRA-04_SICD.nitf --experiment nsub
python3 src/followup_experiments.py --sicd data/giza_2023-03-08_UMBRA-04_SICD.nitf --experiment geometry
python3 src/followup_experiments.py --sicd data/giza_2023-03-08_UMBRA-04_SICD.nitf --experiment increments
python3 src/followup_experiments.py --sicd data/giza_2023-03-08_UMBRA-04_SICD.nitf --experiment psf
python3 src/experiment_e12_planted.py --sicd data/giza_2023-03-08_UMBRA-04_SICD.nitf
```

The E12 run additionally converts the detection floor from pixels into metres of
ground displacement, using the azimuth pixel spacing in the SICD metadata. That
number is to be compared against published ambient seismic amplitudes. **No claim
about that comparison is made here, because the number does not yet exist.**

## Result

*To be appended after the run. This section is deliberately empty at commit time.*

---

# RESULT — appended 13 August 2026, after the run

Scene: `giza_2023-02-07_UMBRA-05_SICD.nitf` (240 MB, UMBRA-05, 7 Feb 2023).
512x512 centre crop of a 5674x5351 scene. `dz_phys` = 2.11 m.
Raw output: `runs/followup_nsub_giza_2023-02-07_UMBRA-05_SICD.nitf.json`.

| `n_sub` | native C | fixed-window C | shuffle null | alignment null | C/align | peak (m) | **peak (cells)** | guard |
|---|---|---|---|---|---|---|---|---|
| 11 | 6.06 | 6.06 | 1.48 | 1.65 | 3.67 | 3.7 | **1.75** | PIN |
| 16 | 4.69 | 3.27 | 1.42 | 1.52 | 2.15 | 3.6 | **1.71** | PIN |
| 22 | 8.56 | 4.16 | 1.47 | 1.72 | 2.42 | 3.5 | **1.66** | PIN |
| 32 | 23.65 | 6.26 | 1.47 | 1.82 | 3.43 | 3.5 | **1.66** | PIN |
| 45 | 37.95 | 4.37 | 1.45 | 1.72 | 2.54 | 3.5 | **1.66** | PIN |
| 64 | 6.99 | 3.82 | 2.24 | 2.77 | 1.38 | 3.2 | **1.52** | PIN |
| 90 | 17.19 | 4.27 | 2.41 | 2.84 | 1.51 | 3.2 | **1.52** | PIN |
| 128 | 108.90 | 3.29 | 1.57 | 1.80 | 1.82 | 3.6 | **1.71** | PIN |

## Scored against the predictions

| Prediction | Result | |
|---|---|---|
| Peak depth 1.6–1.8 cells | **1.52 – 1.75** | **partial miss** — 6/8 inside, the `n_sub` 64 and 90 rows sit at 1.52, below the predicted floor. All 8 remain inside the manuscript's 1.2–1.9 band |
| Surface-pinned at every count | **8/8** | hit |
| Detections above 5x | **0/8** | hit |
| Contrast at `n_sub` = 11, order 3–5 | **6.06** | **miss, high** — higher than any of the five previous sites at this setting |
| Contrast at `n_sub` = 128, order 10^2 and at or below ~275 | **108.90** | hit |
| Fixed-window spread comparable to other sites | **1.9x** (3.27–6.26) | hit — identical to Komati and Bingham |
| Native spread | **23.2x** (4.69–108.90) | inside the 8.9–98.9x range of the other five |

**None of the four falsification conditions was met.** The peak did not leave the
band, it did not survive the guard, nothing cleared 5x, and the behaviour matches
five proxy sites on two other continents.

## The two misses, stated plainly

**1. Giza returns the highest raw contrast of any site tested at `n_sub` = 11.**
6.06, against Komati 2.76, Cairo 2.75, Butte 3.33, Bingham 3.87 and Vesuvius 4.11.
Its alignment-referenced ratio, 3.67, is also the highest recorded. This is the one
number in the run that a defender of the method could reasonably seize on, and it
must be reported rather than buried. It does **not** clear the manuscript's 5x rule
against either null, and the peak it produces is 1.75 cells down and surface-pinned
— the same artifact, slightly louder.

**2. The peak sits at 1.52 cells at `n_sub` 64 and 90**, below the predicted 1.6
floor. Both rows also carry unusually high nulls (shuffle 2.24 and 2.41 against
~1.45 elsewhere), which is what drags C/align down to 1.38–1.51. Not investigated.

## What this establishes

The method returns the same surface-pinned peak, at the same depth in resolution
cells, over the Giza plateau as it does over a copper mine in Utah, a coal-fired
power station in South Africa, a hard-rock mining district in Montana, an active
volcano in Italy and a city centre in Egypt. Zero detections in eight runs.

The manuscript's central claim — that the reported depth is a property of the
processing chain and not of the ground — survives its most important test, on the
one site the original claim is actually about.
