# Analysis of the output data released with "The Biondi Validation" — 12 Nov 2026

**Status: descriptive analysis of their own published numbers plus a noise simulation. Not pre-registered.**
**Sources:** archaeologicalrescue.org/biondi-validation (linked from Grassi's X post 2120689847652196377):
`Yoshimura_Y27_Y34_P8_Interactive_3D.html` (plotly; adjusted R^2 per cell for eight Western Cemetery lines) and
the scan images `MAnu-OS-1` and `Manu-OS-3`. Numbers: `runs/arf_western_cemetery_stats.json` (read in the
browser; the file itself could not be downloaded to the sandbox), `runs/noise_floor_adjr2.json`
(`src/noise_floor_adjr2.py`).

## 1. What the released numbers are
Western Cemetery model header: "ICEYE X13 · K=3208 · W=1900 · b/a>0.1 · unrestricted modes · uniform
lambda = 0.0807481657 m · 0.1-50 m", P=8. Cell value = adjusted R^2 of the best of 1,309 windows.
- **Largest value in the whole model: 0.0041** (the best fit explains 0.4% of the variance). Per line
  0.0012-0.0041; median of the non-zero cells about 0.0009.
- Non-zero cells: 4.7%, 7.5%, 2.7%, 3.5% of lines Y27-Y30; 1.2% of Y32; **Y31, Y33 and Y34 are empty**
  (the page says so: "Y31 and Y33 have no retained P=8 cells").
- 0-5 m, where the published GPR/ERT anomalies are: 0%, 20%, 7%, 12% of cells non-zero (Y27-Y30).
- Osiris "scan 3" (K=3360, W=1990, the "more filtering" image): colour scale tops out near 0.009.
  Osiris "scan 1" (K=295, W=175): scale to 0.30.

## 2. What pure noise gives under the same settings (simulation, no radar data)
Random two-component series, every window, same elliptical least-squares fit, best window kept:

| Setting | Noise | median | 99th pct | max (cells) | His values |
|---|---|---|---|---|---|
| K=3208, W=1900 | white | 0.0006 | 0.0037 | 0.0059 (2,400) | max 0.0041, median 0.0009 |
| K=3208, W=1900 | AR(1) 0.9 | -0.0003 | 0.048 | 0.088 (2,400) | |
| K=3360, W=1990 | white | 0.0006 | 0.0034 | 0.0054 (2,400) | scale to ~0.009 |
| K=3360, W=1990 | AR(1) 0.9 | 0.0000 | 0.042 | 0.074 (2,400) | |
| K=295, W=175 | white | 0.0056 | 0.039 | 0.073 (60,000) | scale to 0.30; patches 0.05-0.15 |
| K=295, W=175 | AR(1) 0.9 | -0.0055 | 0.16 | 0.45 (60,000) | |

**Reading:** the Western Cemetery values are at the level white noise produces by itself (white-noise
99th percentile 0.003, his maximum 0.004), and far below what autocorrelated noise produces. The scan-1
values are above white noise but inside the range of autocorrelated noise. Displacement series built from
heavily overlapping Doppler bands are autocorrelated (measured on our data, Test P).

**Limits:** we do not know the noise properties of his series, and his ellipse gate and run filter are not
simulated. A small adjusted R^2 does not prove there is no signal. It does mean these values cannot be
called detections without a noise control run through his own pipeline, which has not been shown.

## 3. Do neighbouring lines agree?
Lines are 2 m apart. Overlap (Jaccard) of non-zero cells: Y27-Y28 0.12, Y28-Y29 0.19, Y29-Y30 0.38; nulls
from shifting one line by 8-50 positions average 0.02-0.09 (maxima 0.14-0.31). So neighbouring lines do
agree more than shifted ones. **This is expected whether or not anything is underground:** lines 2 m apart
are built from overlapping image patches (24x32 pixels plus reference fields), so they share most of their
input. It cannot be used as confirmation, and it is not evidence against him either.

## 4. Other facts on the page
- Scan 3's own caption: silhouettes "not fitted to this heat map"; the shaft silhouette is drawn at
  positions ~134-143, where the map is nearly empty.
- No code, no scene identifiers. Sensor/product named: ICEYE ("X13", "X33").
