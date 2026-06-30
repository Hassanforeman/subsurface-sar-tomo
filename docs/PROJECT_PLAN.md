# Project Plan — Subsurface SAR Doppler Tomography

*Strategy: stay free until the depth axis validates, then spend. Build from the bottom of
the depth ladder up. Let pre-registered results — not enthusiasm — decide how high we climb.*

---

## Objective

Determine, honestly and quantitatively, whether single-image SAR Doppler micro-motion
tomography reproduces **known** subsurface structure — at what depth, what resolution, and
what false-positive rate — and, where the physics allows, improve it. Convert a validated
shallow capability into commercial value (subsidence/void/infrastructure monitoring) before
attempting the contested deep/archaeological targets.

## Guiding constraints
- **Free data only** (Umbra/Capella open archives) through validation.
- **Small scenes** (4×4 km spotlight) to fit Mac-class processing in early phases.
- **Pre-registration + blinding + null tests** on every validation (see VALIDATION_PROTOCOL.md).
- **Honest kill criteria** at each gate. A rigorous negative result is a win.

---

## Phase 0 — Pipeline bring-up & synthetic truth  *(Mac, free, ~1–2 weeks of effort)*
**Goal:** a working, trustworthy chain before any real interpretation.
- Set up env (`requirements.txt`), read the pinned Bingham SICD/CPHD with `sarpy`
  (`src/inspect_scene.py`).
- Stand up the chain: Doppler sub-aperture decomposition → sub-pixel coregistration /
  micro-motion estimation → steering-matrix inversion (matched-filter first).
- Reuse/port the open repos: `not-JASH` (estimators, synthetic generator, null tests) and
  `mfwarren` (Python ingestion).
- **Synthetic ground truth:** inject known vibrating scatterers, confirm the chain recovers
  them. Implement the mandatory fixes (analytic-signal step, Nyquist-safe f, dimensionally
  consistent steering law).

**GATE 0 (go/no-go):** pipeline recovers synthetic scatterers within one resolution cell,
and null tests show the recovery is above chance. *Fail → fix code; do not proceed.*

## Phase 1 — Measurement-side validation on Bingham  *(Mac, free)*
**Goal:** prove the *measurement* half on real data with known surface change.
- Run on Bingham (UMBRA-05/06 passes). Bingham has exhaustively documented geometry and a
  famous 2013 landslide → known surface deformation to check the micro-motion estimate.
- Verify sub-aperture coregistration, coherence, and that measured surface motion tracks
  reality. This validates everything *up to* the depth inversion.

**GATE 1:** surface micro-motion / coherence behaves physically and matches known change.
*Fail → the measurement front-end is broken; stop and diagnose.*

## Phase 2 — Subsurface validation on Vesuvius  *(Mac → rented A100, free data)*
**Goal:** first true test of the **depth axis** against independent ground truth — on
Biondi's *own* peer-reviewed site.
- Pin the free Vesuvius capture(s) from Umbra's "Volcanoes" collection (geo-search the 214
  UUID captures by bbox ≈ 40.82 N, 14.43 E). Cross-check with Capella if available.
- Add super-resolution estimators (Capon, MUSIC, CS-L1).
- **Blinded** inversion; overlay the known magma-chamber/conduit depths only afterward.
  Full null-test battery.
- Move heavy inversion to a rented A100 once the Mac prototype is correct.

**GATE 2 (the decisive gate):** does the depth axis localise known structure above null,
within the predicted δz? 
- *Pass* → the method has earned a climb toward depth and toward paid sites.
- *Fail* (the honest likely outcome for deep claims) → **pivot**: the binding limit is
  aperture/conditioning; redirect to Phase 3 multi-aperture, and/or write up the negative
  result + feasibility bounds as a preprint.

## Phase 3 — Resolution optimisation  *(rented GPU, free data)*
**Goal:** push the levers that the math actually rewards (TECHNICAL_BIBLE §3.3).
- **Aperture:** stack multiple coherent passes / multi-satellite to grow A and add looks.
- **Super-resolution inversion** as the primary algorithmic gain.
- **Drone/airborne feasibility study:** model a low-R, wide-angular-aperture geometry
  (the legitimately promising hardware direction — geometry, not band).
- Quantify achieved δz vs predicted, with ground truth, at each setting.

**GATE 3:** demonstrate a measurable, validated resolution/depth improvement over baseline.

## Phase 4 — Paid sites & commercial wedge  *(spend begins)*
Only after Gate 2/3 successes:
- **Task** Capella/Umbra (or buy COSMO/archive) over Gran Sasso (known deep lab — direct
  head-to-head with Biondi's claim) and, if warranted, Giza.
- **Commercial pilot** on the *shallow, validated* capability the market already buys:
  subsidence over old workings, tailings-dam/void monitoring, infrastructure deformation —
  the space Biondi's respected Mosul-Dam/bridge work already lives in.

---

## Compute & cost staging
| Phase | Hardware | Cost |
|---|---|---|
| 0–1 | Mac (CPU, Python) | $0 (free data) |
| 2 | Mac prototype → rented A100 (hours) | low (GPU rental only) |
| 3 | Rented A100/H100 (longer jobs) | moderate |
| 4 | GPU + **paid SAR tasking** | real spend — gated behind validation |

## Top risks & mitigations
- **Deep inversion is physically unsupported** (likely). → Bottom-up ladder; honest kill
  criteria; negative result is still publishable.
- **Wrong data mode** (TOPS) wastes effort. → Spotlight CPHD/SICD only (Umbra/Capella).
- **Confirmation bias / pareidolia.** → Pre-registration + blinding + null tests, always.
- **Undisclosed steering matrix** in the source papers. → Re-derive from the patent +
  not-JASH report; keep an explicit "literal vs corrected" taxonomy.
- **Compute blowup on full scenes.** → Small 4×4 km scenes; tomographic *lines* not full
  volumes early; GPU only when the math is proven.

## Definition of success
A reproducible pipeline plus a **pre-registered, blinded, ground-truth-validated** statement
of what this method can and cannot resolve at depth — the thing the entire public debate
lacks. That artifact is simultaneously the engineering foundation, the basis of a preprint,
and the credibility a commercial pilot requires.

## Immediate next actions
1. Pull the pinned Bingham scene (`src/fetch_umbra.py`) and inspect it (`src/inspect_scene.py`).
2. Geo-search Umbra's "Volcanoes" collection to pin the free Vesuvius capture (Phase 2 input).
3. Fill in `VALIDATION_PROTOCOL.md` for the Vesuvius test *before* processing it.
