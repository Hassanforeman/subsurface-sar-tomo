# The other two 3-D models released with "The Biondi Validation" — 13 Nov 2026

**Status: descriptive analysis of their own published files plus a noise simulation. Not pre-registered.**
Companion to `ANALYSIS_ARF_RELEASED_DATA_2026-11-12.md` (the Western Cemetery model). With this, all three
models on archaeologicalrescue.org/biondi-validation have been read.
**Numbers:** `runs/arf_khufu_osiris_models_stats.json` (read in Hassan's browser; the files cannot be
downloaded to the sandbox), `runs/noise_floor_khufu.json` (`src/noise_floor_khufu.py`).

## 1. Osiris Shaft model (`Osiris_Shaft_Interactive_3D.html`)
A drawing of the KNOWN shaft only: levels, passages, survey vertices. It contains no radar values and no
images. There is nothing in it to test. It is the reference shape he compares his scans against.

## 2. Great Pyramid model (`Khufu_X33_W1300_P2_Heights_3D2.html`)
Two "curtains" running up the east face (centre line, and 11 m south), 73 positions x 1,999 depth rows
(0.1-100 m), drawn inward along the face normal. Settings printed in the file: K=3360, W=1300, **P=2**,
b/a>0.1, colour scale adjusted R^2 0 to 0.05.

**The file's own caveat (verbatim):** "Face-normal depth is a visualization hypothesis. It does not validate
the physical depth direction or identify chambers." The ARF article says the same model shows the King's and
Queen's chambers "in their accurate locations".

Values (recovered from the embedded colour images, resolution 0.0002):

| Curtain | cells non-zero | median (non-zero) | 99th pct | max |
|---|---|---|---|---|
| Centre | 37% | 0.0018 | 0.016 | 0.041 |
| 11 m south | 37% | 0.0020 | 0.016 | 0.025 |

The largest value explains 4% of the variance; the typical retained cell 0.2%.

**Noise under the same K and W** (his ellipse gate and run filter not simulated):

| Noise | median | 99th pct | max (2,400 cells) |
|---|---|---|---|
| white | 0.0015 | 0.006 | 0.010 |
| mildly autocorrelated, AR(1) 0.5 | 0.0036 | 0.016 | 0.034 |
| strongly autocorrelated, AR(1) 0.9 | 0.000 | 0.075 | 0.120 |

**Reading:** his values sit above white noise and match mildly autocorrelated noise almost exactly (99th
percentile 0.016 in both). Series built from overlapping Doppler bands are autocorrelated, so this is the
relevant comparison. As with the Western Cemetery model, these values cannot be called detections without
a noise run through his own pipeline.

P=2 (a "structure" needs only two neighbouring cells) is a much looser filter than the P=8 used for the
other scans. That is why 37% of this model is filled, against 1-8% in the Western Cemetery model.

## 3. Are the chambers special in the model?
Using the file's own geometry, cells falling inside a box at each chamber were compared with same-size boxes
placed on a 4 m grid everywhere else inside the pyramid that the curtain covers (about 450 boxes).

| Chamber, on its own curtain | mean in box | share of other boxes with an equal or higher mean |
|---|---|---|
| Queen's, centre curtain | 0.0032 | 17% |
| King's, 11 m-south curtain | 0.0018 | 41% |

Neither chamber stands out: one box in six beats the Queen's chamber box and four in ten beat the King's.
The brightest cell in each curtain is about 60 m above the pavement, not at either chamber.

**Limits (must travel with section 3):** the chamber boxes are approximate coordinates written from memory of
the published surveys (Queen x 2.0-7.7 m east, z 21.2-27.4 m; King x -2.8-7.7 m, z 43.0-48.9 m), not checked
against Petrie; the depth direction is their display hypothesis, not ours; boxes on a 4 m grid overlap, so
the percentages are descriptive, not p-values. Section 2 does not depend on any of this.

## 4. All three released models, together
| Model | has radar values? | settings | max adjusted R^2 | noise comparison |
|---|---|---|---|---|
| Western Cemetery | yes | K=3208, W=1900, P=8 | 0.0041 | white-noise level |
| Great Pyramid | yes | K=3360, W=1300, P=2 | 0.041 | mild autocorrelated-noise level |
| Osiris Shaft | no (geometry only) | - | - | - |
