# PROJECT STATE — single source of truth

**Read this first, before any other doc. Update this file at the END of every work session.**
Rule: if any other document disagrees with this one about *status*, THIS FILE WINS. For
*detail*, follow the pointer this file gives. When you close or open a question, edit the
ledgers below in the same session — that is how we stop doing double work.

*Last updated: 2026-09-02.*

*How to keep this file and supersede docs correctly: `docs/DOCUMENTATION_RULES.md`. Entry point for new sessions: `/CLAUDE.md`.*

---

## 0. One-line status

The reproduction-and-refutation is complete and public (v5 preprint + open code/data on
GitHub/Zenodo); the 2022 Biondi/Malanga paper was **retracted 10 Aug 2026**; all three free
Giza scenes are analysed and null; the remaining work is a short list of open items in §3.

## 1. What is SETTLED — do NOT re-derive these (pointer = where the detail lives)

- **Steering matrix = DFT; depth is a free parameter set by an unphysical 22 kHz.** f only
  relabels the axis (T invariant). → BIONDI_PATENT_RECIPE.md; paper §3.1–3.2; RESULTS_..._FIVE_SITE §5.
- **Mechanism: trajectory is `np.cumsum(inc)` = a random walk; inversion is a DFT; degree-2
  detrend fixes the peak near 1.7 cells.** Reproduced from pure noise with no SAR data. → FIVE_SITE §12–§14.
- **Depth-law derivation.** peak_cells = dominant surviving DFT mode (PROVED); empirical law
  k ≈ 0.856·(d/2+1); the (d+1)/2 rule gives 1.5 vs 1.712 observed (expected, not a gap). → FIVE_SITE §15.2/§15.5.
  ONLY the closed form of the 0.856 prefactor is open (see §3).
- **n_sub "sensitivity" is the same phenomenon as the walk** (longer walk = smoother = higher
  contrast); native contrast not comparable across n_sub; use fixed-window. → FIVE_SITE §13; SENSITIVITY §4b.
- **Velocity/calibration constants only relabel the axis** (verdict invariant); the real risk is
  grid OVER-EXTENSION, which manufactures an alias caught by n_sub-stability (not by the near-surface
  guard or alignment null). → RESULTS_VELOCITY_GRID_2026-09-02.md; sweep_velocity_grid.py.
- **Window taper:** moves the number, never the verdict; 0 detections under any taper on any Giza
  scene; Hann is not universally loudest. → RESULTS_HARDENING_2026-09-02.md; SENSITIVITY §4/§4c.
- **Config objections (coregistrator, float32/64, Hamming) don't change the outcome.** → SENSITIVITY §2–§3.
- **Five sites + Giza, two sensors: 0 detections, all surface-pinned, peak 1.2–1.9 cells.** → FIVE_SITE §1; paper Table 2.
- **Giza within-site repeatability (pre-registered): HIT** — 3 scenes agree to 0.10 cells, all null.
  → RESULTS_GIZA_REPEATS_2026-09-02.md.
- **§5.4 increments anomaly is real & reproducible** (peak stays pinned on 2 of 3 Giza scenes after
  de-accumulation) → accumulation sufficient but not shown necessary at Giza; "mechanism identified"
  in abstract/conclusion is too strong. → RESULTS_GIZA_REPEATS §3.
- **Planted-signal floor:** ~0.2 px; below it the statistic is uninformative-to-backwards; the plant
  is found by DEPTH, and doesn't clear the 5× contrast rule until 0.5 px; metres conversion refused
  (needs (R/V)·v_LOS). → RESULTS_HARDENING §2; FIVE_SITE/E12.
- **Withdrawn/retracted claims (do not resurrect):** 194×, 1720× as a detection margin, "80% overlap
  makes the peak", "the images are the rendered artifact", shuffle-null ratios (2.8/3.3/4.1×). → paper §10.
- **Pomposi (Zenodo Apr 2026):** independent, same conclusion, different route; cite at revision; his
  code bugs told privately only. → COMPARISON_POMPOSI_2026-08-13.md.
- **Commercial idea:** parked, honest "probably not". → COMMERCIAL_ASSESSMENT.md.

## 2. Adversarial reviews already answered (don't re-litigate)

- Grok 29 Jul (config objections), Grok v2/v3 briefs, full dossiers v1/v2. → docs/private/GROK_*.
- Grok adversarial review of v5, 2 Sep — triaged; ~3 of its P0s already fixed in v5 (two Figure 4s,
  June footer, scene-ID disclosure); the rest valid. → ADVERSARIAL_REVIEW_v5_20260902.md (user upload).
- Independent from-scratch confirmation of the mechanism, 2 Sep. → REVIEW_INDEPENDENT_2026-09-02.md.

## 3. What is ACTUALLY OPEN (the only place new work should start)

**Runnable now (no new data):**
- [ ] MUSIC/Capon robustness — does a super-resolution inverter also surface-pin? Preempts the
      "you used a weak inverter" rebuttal. `tomo_demo.py` has both. NEVER RUN.
- [ ] 0.856 prefactor in closed form (spectral algebra of detrend-projection + Hilbert on 1/f²).
      Hard; optional; a genuine theory win if it lands.
- [ ] Apply the four verdict-printer / wording fixes from the Grok v5 review (abstract "mechanism
      identified" → §5.4 wording; §3.3 shaft sentence; §3.5 shuffle-ratio quotes; §8 "shuffled nulls";
      delete "quality-weighted"; Table 3 pre-registration scoring incl. E8 + the now-HIT repeatability).

**Needs data fetched on Hassan's Mac (sandbox is 403-blocked from the S3 buckets):**
- [ ] Volcano breadth (Merapi scenes listed; download → run). IN PROGRESS.
- [ ] Butte rect-window anomaly (5.07 vs alignment null) + the "monotonic sites = the structured
      ones" caveat — the one real loose thread; needs Butte back + ≥1 more structured/unstructured pair.
- [ ] E12 on a real SICD → floor in metres via (R/V)·v_LOS (deliberately not done; referee-bait if rushed).

**External / administrative — CONFIRM CURRENT STATUS (I can't see these):**
- [ ] PCI Archaeology: did a recommender pick it up? Was the Di Palma letter (PCI_LETTER_v2_2026-08-14.md) sent?
- [ ] Line-numbered PDF if a reviewer asks.
- [ ] Email Pomposi (ally).

## 4. Environment / mechanics (saves a session of rediscovery)

- Live repo on the Mac: `~/subsurface-sar-tomo` (Passport drive died Aug 13; repo rebuilt from GitHub).
- The Cowork sandbox mounts it but starts WITHOUT sarpy/scipy → `pip install sarpy scipy` each session
  (~35 MB; ~1 clean shot). Sandbox + cloud container are BOTH 403-blocked from Umbra/Capella S3 —
  new scenes must be fetched on the Mac, then the mounted pipeline runs on them.
- Working style: one terminal command at a time; honesty over hype; be the honest counterweight to
  Grok's optimism (Hassan's explicit preference).

## 5. Doc map (what's current vs superseded)

- **CURRENT:** this file, TECHNICAL_BIBLE.md (v1.5), paper v5 PDF, the three RESULTS_*_2026-09-02.md,
  REVIEW_INDEPENDENT_2026-09-02.md, FIVE_SITE, SENSITIVITY_RESPONSE_BIONDI.md.
- **STALE — do not use for status:** docs/private/HANDOFF.md (dated ~1 Jul: says "Bingham in flight /
  paper done" — both superseded by v5 + Giza + retraction). Kept for history only.
