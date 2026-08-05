# Five sites × eight sub-aperture counts — complete grid, 31 July 2026

*Prepared for the revision of the PCI Archaeo submission (ArticleID #1130). All runs use
`src/followup_experiments.py` with the fixed comparison window, the absolute surface-pinning guard,
and the alignment null. Raw outputs in `runs/followup_nsub_*.json`.*

**40 runs. 5 sites. 2 independent satellite operators. 3 continents.**
**0/40 detections. 40/40 surface-pinned. Peak depth confined to 2.5–3.9 m everywhere.**

---

## 1. The headline result

| site | sensor | native contrast range | ×span | fixed-window range | ×span | peak range | detections >5× | pinned (old → new guard) |
|---|---|---|---|---|---|---|---|---|
| Komati Power Stn, ZA | Umbra | 2.76 – 49.00 | 17.8× | 2.75 – 5.28 | 1.9× | 3.2 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Bingham Canyon, UT | Umbra | 3.87 – 128.64 | 33.2× | 2.88 – 5.40 | 1.9× | 2.5 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Butte, MT | Umbra | 3.33 – 29.49 | 8.9× | 2.33 – 7.52 | 3.2× | 3.2 – 3.9 m | **0/8** | 3/8 → **8/8** |
| Mount Vesuvius, IT | Umbra | 4.11 – 124.19 | 30.2× | 3.74 – 5.36 | 1.4× | 3.2 – 3.7 m | **0/8** | 3/8 → **8/8** |
| Cairo (central), EG | **Capella** | 2.75 – **272.52** | **98.9×** | 2.35 – 6.20 | 2.6× | 3.4 – 3.6 m | **0/8** | 2/8 → **8/8** |

Sites: an open-pit copper mine, a coal-fired power station, a historic hard-rock mining district,
an active volcano, and a dense city centre. Imaged by two unrelated commercial operators with
different constellations, different ground processors and different product chains.

## 2. Finding A — the reported depth is a property of the pipeline, not the ground

**Across all forty runs the peak lies between 2.5 m and 3.9 m** — between roughly 1.2 and 1.9
resolution cells. It does not vary with site, with geology, with sensor, or with sub-aperture count.

If the peak depth carried subsurface information, it would move when the subsurface moved. It does
not move at all. A method that returns the same depth over Vesuvius and over central Cairo is not
measuring either of them.

This is the strongest result in the study, and it is a **positive** claim rather than a negative
one: not "nothing was found at five sites," but "**the same thing is found everywhere, and it is the
processing chain.**"

## 3. Finding B — one undisclosed setting moves the headline number by up to 99×

The sub-aperture count is not stated in the 2022 paper, in patent WO2024008365A1, or in any
presentation. On the same scene, with everything else fixed, the native contrast spans:

- Cairo (Capella): **2.75 → 272.52** (98.9×)
- Bingham: **3.87 → 128.64** (33.2×)
- Vesuvius: **4.11 → 124.19** (30.2×)
- Komati: **2.76 → 49.00** (17.8×)

An investigator running Vesuvius at `n_sub = 128` would report a detection **124× above noise**;
at Cairo, **272×**. Both are zero-detection scenes under a correctly specified null. The published
method gives a user no way to know which number they are looking at.

This also confirms the v3 erratum: Komati reaches **49.00** at `n_sub = 128`, reproducing the 50×
published in v2.

## 4. Finding C — the corrected guard changes every row

The old 5%-of-depth-axis rule flags **14/40** runs as surface-pinned. The absolute two-cell rule
flags **40/40**.

The old rule's threshold scales with the depth axis, whose extent grows with `n_sub` while the bin
count stays fixed — so at low `n_sub` a peak 1.5 cells down was passed as "clear subsurface
structure." Every row in the published table sits in that regime.

## 5. Finding D — results are invariant to the depth-calibration constants

Bingham, run twice, changing only the assumed physics:

| | 6000 m/s, 42 km (pipeline default) | 3000 m/s, 75 km (patent's values) |
|---|---|---|
| contrast | 3.87 | **3.87** |
| shuffle null | 1.47 | **1.47** |
| alignment null | 1.62 | **1.62** |
| C / align | 2.40 | **2.40** |
| verdict | surface-pinned | **surface-pinned** |
| `dz_phys` | 2.11 m | 0.59 m |
| peak depth | 3.5 m | 1.0 m |
| **peak in cells** | **1.66** | **1.69** |

Every dimensionless quantity identical; only the metre labels move. All five sites were run at both
parameter sets with the same outcome.

**This is expected, not a discovery** — calibration constants scale an axis and cannot touch the
tomogram. Report it as a check that forecloses the "you used the wrong constants" objection, and as
the cleanest demonstration that **depth here is assigned rather than measured**: change the assumed
physics by 3.6× and the identical feature is reported at 3.5 m or at 1.0 m, with no other
consequence whatsoever.

## 6. Reproduction of published values

| site | published | this study |
|---|---|---|
| Butte | 3.3× | **3.33** |
| Vesuvius | 4.1× | **4.11** |
| Cairo (Capella) | 2.8× / 1.6× | **2.75 / 1.49–1.57** |
| Komati (corrected, v3) | 2.8× / 1.3× | **2.76 / 1.39** |

**The Cairo/Capella row is now verified.** It had not been re-run since submission and is flagged
"Outstanding verification" in the published manuscript. That flag can be removed.

Repeat runs of identical commands produce bit-identical output — the pipeline is deterministic
under a fixed seed. Worth one sentence in the methods.

## 7. Limitations — state these, do not let a referee find them

- **The fixed window reduces the `n_sub` confound but does not eliminate it.** Butte still spans
  **3.2×** across sub-aperture counts (7.52 at `n_sub`=32 against 2.33 at 128), versus 1.4–1.9× at
  the other four. Claiming the fixed window solves the problem would be overstating it. It changes
  no verdict, but it must be reported.
- ~~The peak-depth invariance has been measured at one crop and patch geometry only.~~
  **Tested 31 July — see §9. The invariance holds.**
- **All five scenes are X-band spotlight.** Nothing here speaks to C-band or L-band behaviour.
- **The alignment null is itself a modelling choice.** It is more conservative than the shuffle
  null, but it is not the only defensible null.

## 8. Changes for the revision

1. Replace the results table with the grid in §1, under the absolute guard and the alignment null.
2. Add the **peak-depth invariance** (§2) as the paper's principal finding — after the geometry test
   in §7 is done.
3. Add the **`n_sub` sensitivity** (§3) with the 272× figure; it is the sharpest single illustration
   of why undisclosed parameters make the method unreproducible.
4. Upgrade the **Bingham row** from "front-end only / no signal" — it produces a full tomogram and a
   surface-pinned verdict at every sub-aperture count.
5. Fix the Table 2 lead-in, which describes all five sites as indistinguishable from look-shuffled
   nulls while naming Bingham.
6. Remove the **"Outstanding verification"** note on Cairo/Capella.
7. Recompute the Komati ratio from unrounded values — v3 states **2.15**, derived from rounded
   inputs (2.8 ÷ 1.3); the unrounded figure is **1.99**, further below threshold. No conclusion
   changes, but this row has already required one erratum.
8. State that the analysis was repeated at the patent's own velocity and aperture with identical
   results.

---

## 9. E5 — the peak depth does not depend on the patch geometry either

`src/followup_experiments.py --experiment geometry`, Bingham, `n_sub = 11`, one-at-a-time sweep
around the baseline (512 crop, 64-px patches, 24 patches, 0.8 overlap):

| varying | crop | patch | n_patch | overlap | C | C/align | peak | **peak cells** | % axis |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 512 | 64 | 24 | 0.80 | 3.87 | 2.40 | 3.5 m | **1.66** | 30.1% |
| patch | 512 | 32 | 24 | 0.80 | 4.24 | 2.06 | 3.8 m | **1.78** | 32.4% |
| patch | 512 | 48 | 24 | 0.80 | 3.71 | 2.54 | 3.7 m | **1.77** | 32.1% |
| patch | 512 | 96 | 24 | 0.80 | 3.64 | 2.30 | 3.6 m | **1.71** | 31.1% |
| patch | 512 | 128 | 24 | 0.80 | 5.14 | 3.36 | 3.6 m | **1.71** | 31.1% |
| n_patch | 512 | 64 | 12 | 0.80 | 4.42 | 1.90 | 3.5 m | **1.67** | 30.4% |
| n_patch | 512 | 64 | 48 | 0.80 | 4.61 | 3.41 | 3.7 m | **1.77** | 32.1% |
| overlap | 512 | 64 | 24 | 0.00 | 3.59 | 2.05 | 3.5 m | **1.67** | 30.4% |
| overlap | 512 | 64 | 24 | 0.40 | 4.05 | 2.79 | 3.5 m | **1.64** | 29.8% |
| overlap | 512 | 64 | 24 | 0.60 | 2.38 | 1.58 | 3.6 m | **1.73** | 31.4% |
| overlap | 512 | 64 | 24 | 0.90 | 7.47 | 4.58 | 3.6 m | **1.69** | 30.8% |
| crop | 256 | 64 | 24 | 0.80 | 4.87 | 3.40 | 3.7 m | **1.77** | 32.1% |
| crop | 1024 | 64 | 24 | 0.80 | 2.70 | 1.89 | 3.6 m | **1.69** | 30.8% |

**Peak depth: 1.64 – 1.78 cells. Spread 1.09×. Standard deviation 0.05 cells.**
**0/13 detections. 13/13 surface-pinned.**

Patch size varied by 4×, patch count by 4×, overlap from none to 0.9, crop area by 16×. The
contrast itself moved substantially — 2.38 to 7.47, a factor of 3.1 — so the geometry demonstrably
changes what the pipeline computes. **The peak depth moved by 0.14 of a cell.**

No single factor drives it: patch 1.71–1.78, overlap 1.64–1.73, n_patch 1.67–1.77, crop 1.69–1.77.

### What this establishes

The reported depth is not a property of the scene, the geology, the sensor, the sub-aperture count,
the depth-calibration constants, or the patch geometry. It survives every knob we can turn. It is
**a fixed output of the inversion itself.**

Note the `% axis` column: the peak sits at **29.8–32.4% of the depth axis** in every single run. The
peak is not at a fixed *depth*; it is at a fixed *fraction of whatever axis the method is given* —
which is precisely why the original 5%-of-axis guard could never catch it, and why the axis-extent
confound mattered.

### The mechanism test this now points to — cheap, decisive, and not yet run

If the peak is an output of the inversion rather than of the data, then **feeding the inverter pure
synthetic noise should place the peak at the same ~1.7 cells / ~30% of axis.** No satellite data
required.

- Same position → the peak is the steering matrix's response to unstructured input. The patent
  itself describes that matrix as a DFT. This would demonstrate the paper's central thesis
  directly rather than by inference: on the only feature that carries the depth claim, real data
  is indistinguishable from noise.
- Different position → something in the real data *is* influencing the peak, and the invariance
  argument needs qualifying.

This should be run before the revision. It is the natural completion of the argument.

### Caveat

E5 was run on **Bingham only**. Repeat on Capella at minimum — a different sensor and processing
chain — before the invariance is stated as general.
