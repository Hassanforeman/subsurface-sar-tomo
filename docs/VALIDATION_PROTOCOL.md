# Validation Protocol — Pre-Registration Template

> Fill this in **before** processing any real scene for a given test. Commit it, then do not
> edit the hypotheses/thresholds afterward. This is the single thing that separates this
> project from "I see a city in the noise."

Copy this file per experiment, e.g. `runs/2026-07_vesuvius/PREREG.md`.

---

## 1. Experiment ID & date
- ID: `__________`   Date pre-registered: `__________`   Analyst: `__________`

## 2. Site & ground truth (define BEFORE looking at any tomogram)
- Site / coordinates: `__________`
- Independent ground truth source (map, survey, seismic tomography, as-builts): `__________`
- Known structures, depths, and their uncertainties: `__________`
- Regions known to be **solid / empty** (for false-positive testing): `__________`

## 2a. Geophysical context (controls the depth axis — see Technical Bible §4.1)
- **Velocity / geology model** source (boreholes, seismic survey, published refs): `__________`
- Assumed seismic velocity vs depth (and its uncertainty): `__________`
- **Water table** depth and known seasonal range: `__________`
- **Ground temperature / freeze–thaw** state at acquisition (frozen? snow? thawed?): `__________`
- Known/expected ambient vibration sources (machinery, traffic, microseisms, wind): `__________`

## 3. Data (frozen before processing)
- Sensor / mode / scene IDs: `__________`
- **Acquisition season / date / time-of-day / weather**: `__________`
- Acquisition geometry (R, incidence, aperture, polarisation): `__________`
- Predicted resolution δz = λR/(2A) with the numbers used: `__________`

## 4. Hypotheses (specific, falsifiable)
- H1 (detection): a known structure at depth z₀ produces an anomaly above the null at `α = ___`.
- H2 (localisation): estimated depth within `± ___ m` (≤ one resolution cell) of truth.
- H3 (specificity): false-positive rate over known-solid regions `< ___`.
- H4 (repeatability): cross-pass / cross-sensor agreement `> ___`.

## 5. Pipeline configuration (frozen)
- Sub-aperture count / overlap: `____`   Investigation freq f (Nyquist-checked): `____`
- Estimator(s): matched-filter / Capon / MUSIC / CS-L1: `____`
- Fixes applied: analytic-signal step [ ]  dimensionally-consistent steering law [ ]
  adjacent-pair + quality-weighted tracking [ ]  detrend geometric ramp [ ]
- Coregistration method & expected precision: `____`

## 6. Null model (define before running)
- Null construction: shuffle sub-aperture pairs [ ]  sign-flip [ ]  phase-randomise [ ]
- N null realisations: `____`   Detection threshold from null: `____`

## 7. Named confounds to control (check each)
- [ ] Diurnal thermal expansion of the surface (can mimic subsurface vibration)
- [ ] Seasonal water-table change shifting the velocity model
- [ ] Freeze–thaw near-surface velocity change
- [ ] Low registration quality / decorrelated look-pairs (weight or exclude)
- [ ] SAR layover / foreshortening; DEM/topography masquerading as depth
- [ ] Atmospheric / ionospheric phase
- [ ] Mirror-symmetry ghost (analytic-signal step applied?)

## 8. Blinding procedure
- [ ] Tomogram produced and saved **before** ground-truth overlay.
- [ ] No parameter tuned after seeing the truth overlay.
- [ ] All produced slices reported (no cherry-picking; show misses too).

## 9. Decision rule (write the kill criterion now)
- **Pass if:** `__________`
- **Fail / pivot if:** `__________`
  (default: "detection not above null AND localisation error > one resolution cell at the
  shallowest rung → passive single-pass not viable → pivot to multi-aperture/active.")

## 10. Results (filled AFTER unblinding)
- Detection AUC vs null: ____   Localisation error: ____   Specificity: ____   Repeatability: ____
- Measured δz vs predicted: ____
- Did residuals track season/groundwater/temperature as expected? ____
- Verdict (pass / fail / inconclusive): ____
- What we changed in the Technical Bible as a result: ____
