# Validation Plan v2 — "Validate What Biondi Does" (June 2026)

*Builds on Grok's granular protocol (gate structure, pre-registration, blinding, kill criteria —
all kept) with corrections grounded in the actual pipeline code and a numpy stress test
(`src/steering_stress_test.py`). Where this differs from Grok, the reason is stated.*

---

## 0. Logic of the plan

To *validate what Biondi does* we must first *recreate his method faithfully* (add the pieces we're
missing), then *test it honestly* (controls that actually bite). A null on a strawman pipeline
proves nothing; a null on a faithful reproduction with hardened controls is decisive. So the order
is **recreate → harden controls → test → gate.**

---

## 1. Corrections to the prior plan (read first)

1. **Velocity is not the cause of our nulls.** The `steering()` matrix contains no velocity —
   `DZ_TARGET` is an arbitrary relative scale, and the tomogram is literally the power spectrum of
   the residual-motion-vs-look sequence. A velocity model only re-labels the depth axis; it cannot
   create above-null contrast. So "run ±20% velocity, report depth shift" is the *weak* test. Keep a
   one-line velocity note for metric labeling, but do not expect it to change a verdict.

2. **The real risks are steering *form* and *grid coverage*, and we demonstrated them.**
   `steering_stress_test.py` shows the inversion is robust to damped/chirped/quadratic signatures
   (good) but has three blind spots: heavy sub-cycle damping (missed), shallow/sub-resolution
   (mislocated to surface), and — the serious one — **off-grid reflectors aliasing into a confident
   false peak that the null test does not catch (~87× contrast).** Guards below.

3. **The positive control is self-referential but generalises.** It injects the exact tone the filter
   seeks, yet recovery still holds for off-shape signals — so it is more informative than feared. We
   still **harden** it (inject a heavily-damped resonance) to measure the true detection floor.

4. **No A100 for single-pass — but the stacked regime reopens it.** The single-scene inversion is a
   tiny matrix multiply (milliseconds); the cost there is SICD I/O + cross-correlation (CPU/IO). So
   no GPU for Phase 0–2. BUT Biondi runs **200+ scenes** (see Lever 0): a multi-acquisition stack is
   genuinely compute- and memory-heavy, and the *fact that he needs heavy compute is itself evidence
   he is not single-pass*. Profile the stacked pipeline first; revisit GPU/large-RAM only if the
   stacked inversion (CS-L1 over many scenes) actually demands it.

5. **Ku is for displacement sensitivity, not depth resolution.** Depth resolution = seismic
   wavelength + aperture. The drone win is **geometric aperture** (low R, wide arc), independent of
   radar band. Don't conflate them.

6. **Add the HVSR/resonance track Grok omitted.** Since the tomogram already *is* the residual-motion
   spectrum, reading resonance peaks (f ≈ v/4H) against Butte's known depths is nearly free and is the
   physically defensible "depth from surface vibration."

---

## Lever 0 — Multi-acquisition stacking (THE headline lever; new)

Verified from primary sources (his 2022 abstract says "series of SAR images"; on Joe Rogan, Jan 2026,
he says **"more than 200"** scans across COSMO-SkyMed + Capella + others): **Biondi is not
single-pass.** Our nulls bound the single-pass case; his configuration is a large multi-acquisition,
multi-sensor stack. Closing that gap is now the single highest-value experiment.

A stack buys two things one pass cannot, mapping onto the two physical stories from
`docs/BIONDI_METHOD_ANALYSIS.md`:
- **Multi-baseline / angular aperture** — passes from different orbital positions enlarge the
  synthetic aperture A, directly attacking the conditioning problem behind our nulls and sharpening
  δz = λR/2A. (This is classic TomoSAR territory — well posed, but satellite baselines still imply
  coarse vertical resolution, so manage expectations.)
- **Temporal aperture** — many dates give the seconds-to-months of surface-vibration record that
  ambient-noise seismology actually requires; coherent aggregation across dates raises SNR on any
  real resonance.

**Build (free):**
1. Find a free site with **deep repeat coverage** in Umbra/Capella open data (some sites have dozens
   of repeat spotlight passes). Prefer a ground-truthed one (re-task Butte if repeats exist).
2. Implement two stacking modes behind a flag in a new `src/stack.py`:
   (a) **temporal-vibration aggregation** — average per-date residual-motion spectra (coherent where
   phase allows) to boost any resonance peak; (b) **multi-baseline aperture** — assemble the
   per-pass looks into one enlarged steering inversion.
3. Re-run the controls (null, hardened PC, leakage, sub-aperture-count stability) on the **stack**,
   on Butte/Vesuvius.

**Decisive question:** does the null survive stacking? If a stacked run on a *known* shallow void
produces an above-floor, stability-stable, leakage-clean band aligned with ground truth → first real
positive, and the explanation for his results. If it stays null → our bound now covers the stacked
case too, which is a much stronger paper.

**Honest caveat:** "uniform across 200 scans" is not proof of reality — a fixed steering-matrix bias
or the off-grid alias we demonstrated would also reproduce on every scene. Consistency shows the
artifact (if any) is systematic, not that it is structure. Ground truth, not repetition, decides.

## 2. Phase 0 — Recreate Biondi's front-end faithfully (Mac; no spend)

Close the gaps between our pipeline and his, so we're testing *his* method:

- **MCA (multichromatic analysis)** — split the range chirp into sub-bands and estimate residual
  motion per sub-band per look. Today our observable is a single scalar trajectory per look; MCA adds
  a real second diversity axis (this is the most material missing piece).
- **LRSD denoising** — low-rank + sparse decomposition of the displacement field (his ship-paper
  step), via `cvxpy`. Separates coherent vibration from sparse noise.
- **Work from CPHD** (full phase history) where available, not just SICD, for maximal sub-aperture
  flexibility; prefer the **longest-dwell staring-spotlight** scenes (bigger Doppler aperture A and a
  longer micro-motion time series — the staring mode is central to his COSMO-SkyMed results).
- Keep: analytic-signal step, adjacent-pair quality-weighted tracking, high sub-aperture overlap.

**Gate 0:** synthetic self-tests still pass with MCA+LRSD in line; front-end residual on stable rock
stays small. Fail → debug before touching real depth claims.

## 3. Phase 1 — Harden the controls (Mac; no spend)

- **Sub-aperture-count stability gate** in `tomogram.py`: re-run each detection at N = 9/11/15/21
  looks; flag any peak whose depth spread > ~1 resolution cell as an artifact/out-of-range (kills the
  off-grid false positive demonstrated in the stress test).
- **Hardened positive control:** inject a heavily-damped resonance, not a pure tone; record the
  contrast floor at which it is still recovered. Report detections only relative to that floor.
- **Three null variants** (look-shuffle, sign-flip, phase-randomization) as Grok specified — kept.
- **Leakage** correlation < 0.3 — kept.

**Gate 1:** controls behave on synthetics (false-positive injection is now caught; hardened PC sets a
sensible floor). Fail → fix controls.

## 4. Phase 2 — Test depth, two parallel tracks (Mac; no spend yet)

Sites: **Butte** (known shallow void, best coherence) then **Vesuvius** (Biondi's own site).

- **Track A — tomographic inversion (recreated):** full pipeline + MCA + LRSD + hardened controls +
  sub-aperture-count stability. Multi-crop (5+ patches). 4-panel figure + metrics.
- **Track B — HVSR/resonance (defensible depth):** per-patch residual-motion power spectrum; test for
  resonance peaks and compare f ≈ v/4H against Butte's documented shallow level depths
  (`docs/BUTTE_GROUND_TRUTH.md`). Use realistic *near-surface* velocities (300–2000 m/s for soil/
  weathered rock), not just granite 4–6 km/s.

**Gate 2 (decisive):** PASS = above-floor detection, stable under sub-aperture-count variation, leakage
< 0.3, and (Track B) a resonance peak matching a known depth. NULL = publish as a bounding/limits
result and pivot to the surface-deformation product. Either outcome is publishable.

## 5. Phase 3+ — only if Gate 2 passes (funded)

Multi-pass stacking; drone/airborne aperture modeling (the real resolution lever); a paid
COSMO-SkyMed staring-spotlight match over a ground-truthed shallow target (Derinkuyu); commercial
pilot (surface deformation first).

---

## 6. Immediate next actions (this week)

1. Implement **MCA + LRSD** in `subaperture.py` / `micromotion.py` (Phase 0).
2. Add the **sub-aperture-count stability gate** and **hardened damped positive control** to
   `tomogram.py` (Phase 1).
3. Implement the **HVSR resonance** module and run Track B on Butte (cheap, high value).
4. Re-run Butte through the recreated+hardened pipeline; compare to the existing null.
5. Pre-register each real run in `VALIDATION_PROTOCOL.md` before processing.

*Kill criteria unchanged: a rigorous negative is a publishable result. We scale only on evidence.*
