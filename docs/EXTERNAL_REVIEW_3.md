# External Review #3 — Updated with the Butte Result

*Third independent review (post-Butte). Verbatim review below, followed by our notes —
including one point of technical pushback we are adopting in the preprint.*

---

## Verdict (reviewer)

**Strong, honest, and now decisive.** The Butte null on a **known shallow void** (with highest
registration quality, passing positive control, and low leakage) is the strongest evidence yet
that single-pass X-band spotlight SAR Doppler tomography does **not** recover subsurface
structure, even where it should be easiest. The pipeline is validated, the controls are
rigorous, and the negative result is credible. Publishable as a preprint now and a solid journal
paper after Vesuvius velocity sensitivity. The surface-deformation monitoring product is
realistic; deep claims remain unsupported.

### 1. Most likely way the negative is wrong / over-stated
**Velocity model calibration.** Butte's dense workings + known level maps are excellent, but
without a site-specific v(z) (borehole/seismic), the relative depth axis could systematically
shift real signals. The uncalibrated axis + uniform-v assumption is the main vulnerability.
Re-run Butte/Vesuvius with published velocity models (sensitivity ±20%) and report the shift; if
the null persists it is robust. Surface leakage is controlled (low at Butte); multi-crop would
strengthen it. Illumination variability (3 s snapshot) is minor given the positive control
passing. No evidence of cherry-picking or code issues.

### 2. Penetration-vs-aperture physics
Decomposition is correct and well-supported. Deep energy attenuates; single-pass aperture is
tiny → poor conditioning. More passes help shallow resolution/conditioning but don't restore
lost deep signal. Drone/multi-angle is the logical next step. The resonant-coupling/waveguide
counter-argument is speculative and requires evidence.

### 3. Decisive next experiment
**Vesuvius with a velocity model** (or a second shallow true-positive such as
Derinkuyu/Cappadocia). Butte already gives a strong negative on a known shallow void; Vesuvius
(Biondi's own site + published seismic models) is the cleanest head-to-head. If the null persists
after v(z) correction, the method's practical limit is very shallow.

### 4. Commercial direction
Surface-deformation / micro-motion monitoring is the right immediate product (existing market,
lower liability, leverages the validated front-end). Sequence: build/sell this first, fund
subsurface R&D with revenue. Shallow void detection (tens of m) is plausible upside *after*
true-positive validation; liability is real — pilot with known sites only. Deep is not
commercializable yet. Cheapest demand test: a free/pilot on a mining/infrastructure contact.

### 5. Overall verdict
Continue to a shallow-subsurface product with surface-deformation as immediate revenue. Publish
the preprint (add Butte details + velocity sensitivity). Run Vesuvius as the capstone experiment.
Positions you as the rigorous actor in a noisy field. "Stop at deep claims; pivot to validated
shallow use."

---

## Our notes / response

**Adopted:** fold Butte in as the 4th site; add the velocity / depth-grid robustness analysis;
keep surface-deformation-first commercial sequencing; line up Vesuvius-with-velocity (or
Derinkuyu) as the capstone.

**Pushback on caveat #1 (and the sharper version we are actually adopting):** a site velocity
model v(z) only maps the *relative* depth index to metres — a monotonic re-labeling/stretch of
the z-axis. It **cannot manufacture above-null contrast** where none exists. Our real tomograms
are indistinguishable from their *look-shuffled* nulls across the **entire** depth axis, so
rescaling that axis leaves contrast-vs-null unchanged: a wrong velocity model does **not**
threaten the null verdict the way "it could shift a real signal into view" implies. There is no
signal at any depth to shift.

The *legitimate* form of the concern is **search-grid coverage**, not axis calibration: if the
inversion's depth grid does not span the depths where a true reflector would sit (because the
assumed velocity is off), a real signal outside the searched range could be missed. This is
cheap to rule out and is the version we will run and report: **vary assumed velocity ±20–50% and
widen the depth grid; confirm the null persists across all of them.** This is both more rigorous
than axis calibration and exactly the referee objection it preempts.

**Convergence:** rounds #1, #2, and #3 independently reach the same conclusions — honest credible
negative; penetration limited by aperture/conditioning, not band; surface-deformation is the
proven near-term product; deep imaging unsupported; a shallow true-positive (or velocity-robust
Vesuvius) is the decisive next test.
