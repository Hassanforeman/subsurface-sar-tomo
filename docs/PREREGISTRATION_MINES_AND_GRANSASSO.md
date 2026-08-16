# Pre-registration — mine-site extension, Gran Sasso, and the §7 shape metric

**Committed 16 August 2026, before any of the new scenes has been downloaded or
processed.** The results sections below are deliberately empty and will be appended
in a later commit. The predictions above them will not be edited; if any of them is
wrong, the wrongness is the result.

This follows the protocol used for the Giza run (`docs/PREREGISTRATION_GIZA_2026-08-13.md`,
predictions at `e4476d7`, results appended at `f6c1a90`).

---

## PART A — Mine-site extension

### A.1 Why

The paper's ground-truth argument currently rests on **one** mine: Bingham Canyon,
plus Butte, Montana as a documented underground district. A public proposal has been
made to settle the method by excavating at a specific archaeological site. That is
not the cheapest available test. **Working mines publish surveyed workings, and free
X-band data exists over several of them, so the test needs no permission from anyone.**

Umbra's open-data catalogue contains 80 tasks. Five are mines:

| Task name (verbatim from the catalogue) | Type | Why it is in the set |
|---|---|---|
| `Bingham Copper Mine` | open pit + underground | already in the paper |
| `Butte, MT` (via existing scenes) | documented underground district | already in the paper |
| `Diavik Diamond Mine, Canada` | open pit **+ underground** | the strongest new positive-truth case |
| `Greenbushes Mine, Australia` | open pit, hard-rock lithium | large excavated void, little underground |
| `Silver Peak Mine, Nevada` | **brine ponds, no underground workings** | **negative control** |
| `Thacker Pass Lithium Mine, Nevada` | shallow open pit | shallow-void case |

Silver Peak matters most methodologically: it is a lithium **brine** operation —
evaporation ponds, no deep excavated void. A method that reports subsurface structure
there is reporting it where there is none to report.

### A.2 Predictions — fixed now

For every new site, at the default setting (11 sub-apertures, 512×512 centre crop,
64-pixel patches, 24 patches, 0.8 overlap, Hann taper, float64):

1. The peak will sit at **1.2–1.9 resolution cells** at every sub-aperture count.
2. **0 detections**: contrast will not exceed 5× the alignment null at any setting.
3. Every run will be **surface-pinned** under the absolute two-cell guard.
4. Peak depth in metres will scale as **1/f** exactly, as at every other site.
5. **Diavik will not differ from Silver Peak** in any of the above, despite one having
   documented underground workings and the other having none.

Prediction 5 is the point of the exercise. If the method worked, those two sites
should not look the same.

### A.3 What would falsify this

- Any site clearing 5× the alignment null **and** escaping the two-cell guard.
- Diavik separating from Silver Peak on any decision statistic.
- A peak aligning with a documented working level to within the depth resolution.

Any of these is a positive result for the method and will be reported as one.

### A.4 Result

*To be appended after the run. Deliberately empty at commit time.*

---

## PART B — Gran Sasso / LNGS

### B.1 Why

A public claim reports a tomographic reconstruction of the Laboratori Nazionali del
Gran Sasso at a stated 1.4 km depth. LNGS is the best ground truth available for a
deep-void claim anywhere: three excavated halls, each roughly 100 × 20 × 18 m, under
about 1,400 m of rock, with the layout published by INFN.

### B.2 Predictions — fixed now, conditional on coverage existing

1. Peak at **1.2–1.9 resolution cells**, as at all six existing sites.
2. Reported depth in metres will move as **1/f** and is therefore not a measurement.
3. Contrast will not exceed **5×** the alignment null.
4. **No feature will appear at the position, orientation or dimensions of the three
   halls.**

Prediction 4 is the one most likely to fail, and is the reason to run it.

### B.3 Coverage

A coordinate search over the Umbra and Capella open catalogues
(`find_gran_sasso.sh`, box 42.30–42.60 N, 13.30–13.75 E) is running. Task names in
the catalogue contain nothing Italian, but names are arbitrary — the Giza scene was
filed under `ad hoc/Pyramids of Giza/`.

**If there is no free coverage, that is itself the finding**: the published LNGS
reconstruction cannot be independently checked by anyone, which makes "which sensor,
which scene, which acquisition date" the only remaining question.

### B.4 Result

*To be appended after the run. Deliberately empty at commit time.*

---

## PART C — The §7 shape metric

### C.1 Why, and a failure worth recording

§7 says three renderings of an empty volume failed to resemble the published
imagery, and a fourth — common-mode subtraction — is **unresolved**, because
judging resemblance by eye is the failure mode this paper attributes to the work it
examines. Settling it requires a statistic fixed in advance.

**The first attempt at that statistic failed, and the failure is instructive.**
An absolute threshold was calibrated on synthetic controls — isotropically smoothed
noise as the negative, synthetic shafts and chambers as the positive — and separated
them perfectly, 0/5 and 5/5. Applied to real pipeline output it then classified
**9 of 12 renderings of an empty volume as architecture-like, including the raw
volume with no rendering applied at all.**

The rule was not wrong about those volumes. The calibration was against the wrong
null. A tomogram's depth axis is a DTFT of a smooth accumulated trajectory, so every
tile's depth profile is smooth **by construction**, and above-threshold voxels form
long vertical runs whether or not anything is there. Isotropically smoothed noise has
no such property.

This is the paper's own central result applied to the paper: **an absolute threshold
is not a detection rule.**

### C.2 The rule, fixed now

Four statistics on the above-threshold voxels (99th percentile) of a volume:

| | |
|---|---|
| `vrun` | median contiguous depth extent at one map position |
| `elong` | median z-extent ÷ horizontal extent of connected components |
| `ncomp` | number of connected components (architecture is few and large) |
| `span` | fraction of the depth axis occupied |

**A volume is called architecture-like only relative to a pipeline-matched null:**
its `vrun` must exceed **1.5×**, or its `ncomp` fall below **half**, that of a volume
produced by the identical pipeline from an input containing no scene, under the
identical rendering treatment.

### C.3 Calibration, already run

Planting four vertical shafts into the empty volume and re-rendering both arms
identically, the statistic separates planted from empty in **8 of 12** treatments,
with margins of 4–5× on `vrun` and 7–13× on `ncomp`. The four treatments where it
does not separate (`tile whiten`, `whiten + log`, `common-mode + whiten + log`,
`depth gain z⁴`) are **excluded in advance** — a statistic that cannot tell a planted
volume from an empty one under a given rendering cannot settle anything under that
rendering either.

Calibration: `src/shape_metric.py` → `runs/shape_metric.json`.

### C.4 What this will be applied to, and in what order

1. The real Giza volume, against a pipeline-matched empty volume. **Not yet run —
   requires the SICD, which is not present in the analysis environment.**
2. Only after (1) is complete and recorded: any comparison against published figures.

**No published figure will be scored before step 1 is committed.** The order matters,
because a metric chosen after seeing the target is not a metric.

### C.5 Result

*To be appended after the run. Deliberately empty at commit time.*
