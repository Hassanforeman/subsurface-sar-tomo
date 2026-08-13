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
