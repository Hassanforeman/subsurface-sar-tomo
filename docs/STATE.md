# PROJECT STATE — single source of truth

**Read this first, before any other doc. Update this file at the END of every work session.**
Rule: if any other document disagrees with this one about *status*, THIS FILE WINS. For
*detail*, follow the pointer this file gives. When you close or open a question, edit the
ledgers below in the same session — that is how we stop doing double work.

*Last updated: 2026-11-09 (paper v6.3 POSTED to Zenodo after a third Grok review — Hassan reversed the 11 Oct hold; MDPI letter of concern on Biondi's 2022 Vesuvius paper SENT. Previous: 11 Oct v6.2 after Grok re-review of v6.1.)*

*How to keep this file and supersede docs correctly: `docs/DOCUMENTATION_RULES.md`. Entry point for new sessions: `/CLAUDE.md`.*

---

## 0. One-line status

Public: v6.3 preprint on Zenodo (9 Nov 2026; record 24062309, version DOI 10.5281/zenodo.24062309; concept DOI 10.5281/zenodo.21066657), under review at PCI #1130, + open code/data.
Previous public version was the 14 Aug Zenodo v4. Next step: tell the PCI recommender v6.3 is public (header says she is being informed); then revise once on the reports.
The 2022 Biondi/Malanga paper was **retracted 10 Aug 2026**. All three free Giza scenes: no detection at the
specified taper, but pre-registered falsification (ii) was MET on 2/3 scenes (incl. primary) — residual unexplained.

## 1. What is SETTLED — do NOT re-derive these (pointer = where the detail lives)

- **Steering matrix = DFT; depth is a free parameter set by an unphysical 22 kHz.** f only
  relabels the axis (T invariant). → BIONDI_PATENT_RECIPE.md; paper §3.1–3.2; RESULTS_..._FIVE_SITE §5.
- **Mechanism: trajectory is `np.cumsum(inc)` = a random walk; inversion is a DFT; degree-2
  detrend fixes the peak near 1.7 cells.** Reproduced from pure noise with no SAR data. → FIVE_SITE §12–§14.
  SCOPE (7–11 Oct): sufficient, not shown necessary; specific to accumulation. Test I (common-reference) could not
  compare routes (NOT TRACKABLE under its design; design weaknesses listed in RESULTS_COMMON_REFERENCE correction).
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
- **Depth constant derived exactly** (not just measured): peak = argmax of a parameter-free matrix
  quadratic form; deg-2 value = 1.680 cells (0.869/2.474 at deg 0/4), pipeline reproduces to MC error.
  No single clean constant — the 0.856·(d/2+1) law is only approximate. → RESULTS_DEPTH_CONSTANT_2026-09-02.md.
- **Super-resolution inverters (Capon, MUSIC) also surface-pin** (real Giza: Bartlett 1.75, Capon 1.99,
  MUSIC 1.75 cells) — the artifact is upstream of the inverter; "you used a weak inverter" is refuted.
  → RESULTS_INVERTERS_2026-09-02.md.
- **Five sites + Giza, two sensors: 0 detections at the specified Hann taper, all surface-pinned, peak 1.2–1.9 cells.**
  Exception to keep stating: Butte with a RECTANGULAR window = 5.07 (leakage; r = +0.977 over only 4 windows).
  n_sub-11 ratios (all run files committed 7–11 Oct): Giza 03-08 [primary] 2.51, 02-07 3.67, 02-08 2.28; Bingham 2.40;
  Butte 1.53; Komati 1.88; Cairo 1.76; Vesuvius 2.85. Max over all 24 Giza runs 4.30. → paper v6.2 Table 3.
- **Giza within-site repeatability (pre-registered): HIT** — 3 scenes agree to 0.10 cells, all null.
  → RESULTS_GIZA_REPEATS_2026-09-02.md.
- **§5.4 increments anomaly is real & reproducible** (peak stays pinned on 2 of 3 Giza scenes after
  de-accumulation) → accumulation sufficient but not shown necessary at Giza; "mechanism identified"
  in abstract/conclusion is too strong. → RESULTS_GIZA_REPEATS §3.
  **Test H (27 Sep, prereg `f2f5a3a`): NOT ANOMALOUS** vs each scene's look-order-shuffle null (10.3 / 55.8 /
  12.0 percentile; α 0.05); increments not serially correlated (lag-1 ≤ 0.10). Not an order effect. Residual:
  weak surface-ward lean of the increment VALUES on 2 scenes (P(≥2 pinned | null) ≈ 0.05); open, small.
  → RESULTS_INCREMENTS_2026-09-27.md.
- **Planted-signal floor:** ~0.2 px; below it the statistic is uninformative-to-backwards; the plant
  is found by DEPTH, and doesn't clear the 5× contrast rule until 0.5 px; metres conversion refused
  (needs (R/V)·v_LOS). → RESULTS_HARDENING §2; FIVE_SITE/E12.
- **Withdrawn/retracted claims (do not resurrect):** 194×, 1720× as a detection margin, "80% overlap
  makes the peak", "the images are the rendered artifact", shuffle-null ratios (2.8/3.3/4.1×). → paper §10.
- **Pomposi (Zenodo Apr 2026):** independent, same conclusion, different route; cite at revision; his
  code bugs told privately only. → COMPARISON_POMPOSI_2026-08-13.md.
- **ejhong/sar — "SAR Depth, Tested" (GitHub + site ejhong.github.io/sar; after 10 Aug 2026; NOT peer-
  reviewed; correction 27 Sep: first logged as synthetic-only from the README — the site runs REAL data):**
  independent reimplementation on two ICEYE Spotlight Dwell scenes (Giza 2025-08-27, Sacsayhuamán
  2025-08-22). Same conclusion as ours, different formulation (interferometric-style Kz steering, not the
  patent DFT). Useful to us: (1) known-voids positive control — hundreds of surveyed 5-30 m burial shafts
  in the Giza cemeteries vs bare plateau: no signal (+0.031 brightness-matched); (2) analytic resolution
  bound s² ≥ δaz·L·Vs → ≥ 27-52 m; (3) seismic-array cross-correlation test: injected wave 0.49, real 0.004;
  (4) split-aperture halves give different depths; (5) depth axis periodic by construction (27.4 m at
  Khafre in their bank); (6) the public "BiondiProtocol/Replication-and-Verification" v1.7 code quantises
  registration to integer pixels. Cite at revision. Full comparison + new questions Q1-Q7 →
  COMPARISON_EJHONG_2026-09-27.md. Their raw ICEYE data are NOT public (not in ICEYE open catalogue).
  CORRECTION (ejhong archive banner, 28 Sep): (3) the array test, the R9 coherence curve, the R4 77 µm/s floor and R7
  were withdrawn/reinterpreted by their author — do NOT cite them; only the periodic free depth axis and the
  no-discrimination results still stand.
- **Commercial idea:** set aside, not ruled out (paper COI wording since v6.2). → COMMERCIAL_ASSESSMENT.md.
- **§7 shape metric, pre-registered step 1 (26 Sep): NEGATIVE by the 5/8 rule — BUT (7 Oct) raw/log/gamma are
  identical treatments, so on 6 distinct treatments 02-08 = 4/6 (majority). Report as unexplained positive of a flawed
  statistic, not a null.** Real Giza centre crops vs matched
  empty volume, 8 treatments: 02-07 0/8, 02-08 4/8 (near-miss), 03-08 [prereg primary] 0/8; planted-
  shaft control 8/8 on every scene. 0 of 15 crops reach the 5/8 threshold. Choices committed first
  (`ec411e3`). Paper §7's "provisional" can be updated. → RESULTS_SHAPE_METRIC_GIZA_2026-09-26.md;
  src/shape_metric_giza.py; runs/shape_metric_giza.json.
- **2022 figures, pre-registered C.4 step 2 (27 Sep): the displayed geometry is the CAD model's.**
  16 "tags association" pairs: model panel carries more independent detail than the tomogram panel in
  15/16 (median 9.7x; robust: 5.7x after equal median filter, tomogram 3.35x coarser). Only miss (Fig 49)
  is a heat-map over an engraving. Descriptive: NO tomogram panel has axes/scale (so P3 untestable and
  the tag association is uncheckable); the tomography is 2-D jet slices, never a rendered volume;
  4/16 tomogram panels are overlays on pre-existing interior drawings/photos. Weak-by-design test —
  the descriptive findings matter more. **Journal version checked:** the 16 pair images are identical to
  arXiv v1 (r = 1.00); no axes added despite the 2022 reviewer's demand; replication 15/16, 10.5x. Only
  tomograms with axes (J48, J53) are in PIXELS; the CAD is dimensioned in metres. J53 = a 5th overlay.
  → RESULTS_FIGURES_2026-09-27.md §6; src/figure_information*.py.
- **2026 Second Sphinx press images, pre-registered descriptive audit (27 Sep, prereg `7cca12e`).** 58
  slides. Input = four unscaled 2-D jet heat-maps (views 101/102/103 + top). Their own pipeline slide
  lists a Thermal-to-Visible GAN (Pix2Pix/CycleGAN), DeepFace/MediaPipe landmarks, ArcFace/Eigenface,
  golden-ratio canon grids, in slides titled as dialogue with Grok/Gemini; renders carry the known Great
  Sphinx form (est. length 73.0 m); percentages are model outputs; heat-maps hand-stretched onto photos
  (handles visible); Giza 3-D scene = identical primitives in a modeller. X1 hit, X2 hit, X3 partial.
  → RESULTS_PRESS_IMAGES_2026-09-27.md; src/press_image_audit.py; runs/press_image_audit.json.
- **Test G (27 Sep, prereg `4a4a57d`, amendments `0bc7d7d`): known voids NOT distinguished — NULL.**
  Hundreds of surveyed 5-30 m mastaba shafts (W+E cemeteries) vs bare plateau, brightness-matched:
  d = −0.10 (02-07), −0.03 (03-08), both below the plateau-vs-plateau spread; displacement-planted control
  detected everywhere (|d| 1.9-2.0). Secondary 02-08 +0.30 vs −0.28 plateau spread (excluded by rule).
  Agrees with ejhong R13 on independent data. Q3: adjacent looks match ~0.6 (≈ pure-speckle filter-bank
  overlap 0.56), non-overlapping looks at the speckle floor (0.06-0.18) → increments are registration
  noise, measured. 02-08 SICD geolocation is off ~500 m (earlier centre-crop tests unaffected).
  → RESULTS_KNOWN_VOIDS_2026-09-27.md; src/known_voids_umbra.py; runs/known_voids_umbra.json.
- **Q2 (27 Sep, descriptive): the paper's single-pass Kz ladder on our Umbra geometry is near-uniform (CV 2e-6–2e-5;
  a geometric identity for near-linear motion) → DFT.** (7 Oct: 'B⊥' here = LOS-perp displacement, mostly along-track;
  true cross-track 1.05/0.77/16 m, consistent with Pomposi ~0.6 m.)
  (CV of ΔKz 2e-6–2e-5); depth repeat = (λs·r·sinθ)/(2ΔB⊥) = 292 / 240 / 71 m per metre of the unmeasured
  λs, different per scene (LOS-perp reading). Under the true cross-track reading (ΔB ≈ 0.07/0.05/1.07 m) the repeat is
  ~2.7e6/2.8e6/1.7e5 m per metre of λs — no usable depth resolution (paper v6.2 §3.2). Closes the "orbit curvature ≠ DFT" caveat. → RESULTS_KZ_LADDER_2026-09-27.md;
  src/kz_ladder_umbra.py; runs/kz_ladder_umbra.json.
- **Test F (27 Sep, prereg `603ca70`): vertical streaks are NOT surface-linked — H-surface REJECTED.**
  Streak strength vs registration quality / brightness: |ρ| ≤ 0.15 in all 3 scenes (null ~0); identity
  ρ(S, trajectory energy) = 1.00; displacement-planted control 4/4 everywhere. Do not describe streaks as
  "surface-driven". 02-08 near-miss split: MIXED (N1 0.14; blob elongation 26 = empty-noise 26, painted
  shafts 74-82) — not surface-correlated, not shaft-shaped; stays reported, not explained.
  → RESULTS_STREAKS_2026-09-27.md; src/streak_surface.py; runs/streak_surface.json.

## 2. Adversarial reviews already answered (don't re-litigate)

- Grok 29 Jul (config objections), Grok v2/v3 briefs, full dossiers v1/v2. → docs/private/GROK_*.
- Grok adversarial review of v5, 2 Sep — triaged; ~3 of its P0s already fixed in v5 (two Figure 4s,
  June footer, scene-ID disclosure); the rest valid. → ADVERSARIAL_REVIEW_v5_20260902.md (user upload).
- AI-assisted self-review (NOT independent; retitled 7 Oct), 2 Sep. → REVIEW_INDEPENDENT_2026-09-02.md.
- Grok hostile panel on v6, 7 Oct → v6.1 (docs/private/TRIAGE_HOSTILE_PANEL_2026-10-07.md).
- Grok re-review of v6.1, 11 Oct → v6.2 (10 must-fix items, all applied; nice-to-haves not yet triaged).

- **The end-product detail cannot come from the data** (3 Sep): a recognizable Sphinx face with a
  0.6 m cobra at 500-1200 m is 1-3 orders of magnitude finer than the method's own resolution (honest
  voxel 150-460 m tall / ~170 m wide via Fresnel; even 22 kHz best case ~2x12 m). The 2022 paper
  pairs a pre-made 3D MODEL with the blobby tomogram ("Tags association from tomography to 3D model");
  the 2nd-Sphinx pipeline compiles a "3D mesh" + AI. Detail enters downstream, not from radar.
  → BIONDI_IMAGERY_ANALYSIS_2026-09-03.md, src/resolution_vs_feature.py.

## 3. What is ACTUALLY OPEN (the only place new work should start)

**Runnable now (no new data):**
- [x] DONE 2 Sep: 8 verified accuracy fixes applied to build_v5.py + PDF rebuilt (16pp, 8 figs):
      "mechanism identified"→"sufficient generating mechanism demonstrated" (abstract+conclusion, +§5.4
      caveat); "quality-weighted" removed (3×, false of code); §3.3 shaft→"surface-pinned band"; §3.5
      117.8×/96.7× shuffle-null quotes dropped; §8 "shuffled nulls"→alignment/pipeline-noise; "exactly
      as disclosed"→"as disclosed". For Hassan's review; NOT submitted.
- [x] DONE 2 Sep: folded today's results into paper v5 (build_v5.py + PDF, 16pp/8figs): repeatability
      clause in abstract; MUSIC/Capon in §3.1; depth constant derived (1.68) in §5.3; velocity/grid
      sweep result in §8; Table 3 re-scored (E8 split + repeatability HIT rows; falsification conditions
      corrected — (ii) split, (iv) tested-not-triggered; dropped "none of four met"); §10.4 pruned.
      For Hassan's review; NOT submitted. Remaining paper polish is Hassan's editorial call.

- [x] Titanic claim VERIFIED (X post 15 Aug 2026): the frame is a labelled "In-situ Photo Overlay" — a real
      seabed PHOTO composited on the HarmonicSAR blob field. Detail is the photo's; radar layer is blobs.
      X-band skin depth in seawater ~2.5 mm vs 3800 m depth = no possible signal. Clearest example of the
      draping mechanism. → BIONDI_IMAGERY_ANALYSIS_2026-09-03.md §5.
- [x] DONE 27 Sep: prereg C.4 step 2 on the 2022 paper's 16 paired figures — see §1.
- [ ] Optional, not started: the same measurement on a 2025/2026 Giza or "Second Sphinx" figure (a
      different, later pipeline). DONE 27 Sep (descriptive) — see §1. Next: step (a) below.
- [x] DONE 27 Sep: test F (streaks vs surface) + near-miss split — see §1.
- [x] DONE 27 Sep: test G (Q1 known voids: NULL) + Q3 coherence + Q2 — see §1.
- [x] DONE 27 Sep: test H — NOT ANOMALOUS (see §1). Paper §5.4 caveat wording → RESULTS_INCREMENTS §3. Also owed: complex coherence + estimator peak height
      for R3; H1 spacing vs ALIAS location (not primary peak); H3 noise-face pass-rate methods note (low prio).
- [ ] Note: BiondiProtocol README changed on 27 Sep (now v1.7 package "for Ed", 5% overlap gate, per-pair B⊥);
      our earlier "CHAT-GPT" quote is from the prior README — cite with date or drop.
- [ ] (was) NEW from ejhong comparison: Q1 known-void cemetery test on our Umbra scenes
      (feasible: cemeteries inside all 3 footprints); Q2 Umbra Kz ambiguity depth; Q3 coherence vs look
      separation; Q4 surface spacing → apparent depth (follow-up to rejected test F). → COMPARISON_EJHONG §6.
      Grok round (27 Sep) triaged → docs/private/GROK_TRIAGE_EJHONG_2026-09-27.md (design notes for Q1-Q4;
      Grok wrongly said the BiondiProtocol repo doesn't exist — we fetched it).
- [ ] Outreach to ejhong (draft: docs/private/OUTREACH_EJHONG_DRAFT.md; propose cross-check on open Umbra
      data, ask for ICEYE product IDs, ask citation). Hassan to send. [external]
- [x] DONE 27 Sep: HOW_BIONDI Step 1 qualified (strong driven motion only; ambient below floor). Paper v5
      wording on the "legitimate front end" should get the same qualifier at revision. [external]
- [ ] Candidate (not pre-registered yet): real-crop streak statistics vs matched empty-noise nulls
      (RESULTS_STREAKS §4). [sandbox-ok once volumes cached / Mac]
- [x] TESTED 27 Sep (test F: MIXED, see §1). Original item: Shape-metric near-miss (02-08 centre crop 4/8, mostly component-count arm, no vertical-extent
      gain; off-centre crops of 02-08 are all 0/8; 02-08 is the steepest look, incidence 29.4 deg vs
      36.8/35.3 for the other two, same side/azimuth). Framing: "two clean nulls + one unexplained
      near-miss" until tested: test the "surface content, not depth" explanation with a surface-matched null or a
      co-location test vs surface brightness. Secondary; cannot change the step-1 verdict. [needs-data:
      run on Mac] → RESULTS_SHAPE_METRIC_GIZA_2026-09-26.md §3.
- [ ] **7 Oct: hostile-panel review (Grok) → v6 NOT READY, major revision.** Verified: shape metric has 3
      identical treatments (02-08 = 4/6 distinct); prereg falsification (ii) met on 2/3 Giza scenes (was
      mis-scored); E5 never run; ejhong R4/R9/R7/array test withdrawn 28 Sep (we cite them); §3.1 DFT sentence
      false; AI disclosure omits Claude; podcast quote trimmed + unverified. Triage + plan:
      docs/private/TRIAGE_HOSTILE_PANEL_2026-10-07.md. Decisions (Hassan): did NOT contact MDPI; leave git history +
      disclose; keep one paper; cut podcast quote. → paper v6.1 written in place (PAPER_v6_DRAFT_2026-09-27.md,
      deviations Table 5, scoped mechanism, shape 4/6, power, AI/COI/fair-dealing fixed). Corrections appended to
      PREREGISTRATION_GIZA; HOW_BIONDI Step 1 fixed; REVIEW_INDEPENDENT retitled. kz_ladder now reports
      along/cross-track (cross-track 1.05/0.77/16.0 m vs Pomposi ~0.6 m). Owed: common-reference variant;
      complex coherence; non-Giza run files; Table 1/Fig 1 port; Reisner citation check.
- [x] **Test I RUN 7 Oct (Mac, at 1474fd7): NOT TRACKABLE.** 0/24 patches pass the planted-shift control on
      all 3 Giza scenes (both estimators); CR error 0.06–0.2 px beside the reference, 0.4–18 px beyond (speckle
      signature). Mechanisms not separable on these data; paper §4.2 + limitations updated; scope note stands.
      Interpretation: on these scenes a full-aperture trajectory can only be built by chaining adjacent steps.
      → docs/RESULTS_COMMON_REFERENCE_2026-10-07.md; runs/common_reference.json. Do not re-run as is.
      (Original entry follows.) Prereg:
      docs/PREREGISTRATION_COMMON_REFERENCE_2026-10-07.md; script src/common_reference.py (selftest PASS, sandbox).
      Run on Mac: `python3.13 src/common_reference.py` → runs/common_reference.json. Design-phase synthetic facts
      (disclosed in prereg): speckle is untrackable across the aperture (|look| corr ~0 beyond 2 looks); pipeline
      phasecorr fails the CR control even on point scatterers (2/24), NCC passes (22/24); CR pinning is not
      diagnostic alone (motion-free scenes pin 0/100/38% at strengths 5/15/30; planted real shifts pin 100%) —
      any low-order error covariance gives a shallow argmax. Readings: A (pin without accumulation?) and
      B (scene-wide common shift beyond motion-free null?). [sandbox-ok selftest / Mac for real run]
      Sandbox note: no pip access this session → scipy.fft shim at /tmp/shim (`from numpy.fft import *`).
- [ ] Paper v6 DRAFT written 27 Sep: paper/PAPER_v6_DRAFT_2026-09-27.md (markdown; folds in F/G/H, Q2/Q3, shape
      metric, figure + press audits, ejhong/Pomposi; §7 'provisional' superseded). Next: Grok review, then reviewer
      reports, then port to build_v6.py/PDF. [writing]
      Grok referee pass applied 27 Sep (docs/private/GROK_PAPER_REVIEW_v6_2026-09-27.md). Open TODOs in draft:
      per-site alignment ratios: Giza 3.67, Bingham 2.40, Butte 1.53, Komati ≤2.41 recorded; Vesuvius 2.85 (re-run 7 Oct,
      raw 4.11 reproduced exactly, run file committed); Cairo 1.76 (re-run 11 Oct on the Mac mini, raw 2.75
      reproduced exactly, align null 1.57, peak 1.71 cells PIN; run file committed). Bingham/Butte/Komati run files
      still not in repo. NOTE: repo now lives on the Mac mini (1.7 TB free); the iMac disk was full.
      11 Oct: v6.1 Table 1 ported (block-by-block, with "where the patent is silent" column) and Figure 1 ported
      (docs/figures/fig1_fcompare_butte.png = runs/fcompare_2024-03-07…png; it is the 256-look Butte run, inferred
      from its 270 m axis at δz 2.1 m). Ref [14] confirmed + [15] Der Manuelian 2017 (G 7000 X >27 m) added;
      shaft range now cited as ~1 m to >27 m. Dispersion paragraph written with refs [17]–[21]; MDPI review_report quote RE-VERIFIED 11 Oct
      (earlier-submission R1 Reviewer 2) and cited as [16]. 11 Oct: Bingham re-run 2.40 (raw 3.87 exact) and Komati n_sub-11 ratio 1.88 (raw 2.76 exact), run files
      committed. Butte re-run 1.53 (raw 3.33 exact; scene is in Umbra task "ad hoc"), run file committed.
      ALL six Table 3 sites now have n_sub-11 run files. No paper TODOs remain except the Reproducibility-gap note for n_sub>11.
      and non-Giza scenes are NOT on disk (checked 29 Sep; data/ holds only Giza) — re-fetch via src/fetch_umbra.py to
      regenerate. Butte rect 5.07 now disclosed in §5.1. Podcast citation [8]; v5 tables/figures to port.
- [x] ejhong outreach POSTED 29 Sep: github.com/ejhong/sar/issues/1 (open, renders correctly). Awaiting reply. [external]
- [x] **11 Oct: paper v6.2** after Grok re-review of v6.1 (all 10 must-fix items applied; see paper §10 v6.2 list).
      DFT "any input" line also withdrawn in README, Academia blurb, podcast doc; banners on build_v5/refutation/merged.
- [ ] NEXT: changes letter to the PCI recommender (draft: docs/private/PCI_CHANGES_LETTER_v6.2_2026-10-11.md)
      v6.2 PDF BUILT 11 Oct: paper/Giza_SAR_Doppler_Reproduction_v6.2.pdf via `bash paper/build_v6.sh` (16 pp).
      ~~DECISION (Hassan, 11 Oct): HOLD — do not send v6.2 or the letter until PCI reviewer reports arrive; then
      revise once and send v6.x + letter + response together. Grok's nice-to-have list not yet triaged. [external]~~
      SUPERSEDED 9 Nov (Hassan): post now, ahead of Biondi's announced 'redemption'. Third Grok review (9 Nov) → v6.3
      (header DRAFT removed; Vesuvius/Butte July positive controls stated in §5.1; 4/4 scoped to Giza; Table 5 prior-exposure
      named a limitation; abstract item 5 reworded). v6.3 PDF: paper/Giza_SAR_Doppler_Reproduction_v6.3.pdf. PUBLISHED on Zenodo 9 Nov 2026 as version v6.3
      (https://zenodo.org/records/24062309, DOI 10.5281/zenodo.24062309; title, date, description updated; signed in via GitHub).
- [x] 9 Nov 08:33: told the PCI recommender (Di Palma, cc PCI contact) that v6.3 is public; reviewers may continue on their
      version; one consolidated revision + response letter will follow the reports. [external]
- [ ] Send the changes letter + revision when PCI reports arrive. [external]
- [x] 9 Nov 08:36: replied on X (@darealHassan) to @GrassiTrevor's post arguing the retraction was political because the
      Vesuvius paper stands: https://x.com/darealHassan/status/2119559718473744463 (method not target; Vesuvius reproduction
      found only a surface artifact; planted signals recovered; concept DOI). [external]
- [ ] WATCH (9 Nov): Grassi (embedded Khafre Project filmmaker; 'THE BIONDI PROTOCOL' playlist, 20 videos) tells Tsoukalos
      'get ready for final proofs this week'. Tsoukalos (Ancient Aliens) mocked the retraction ('You don't say'). When the 'proofs'
      appear, judge them against paper v6.3 §9 'What would change this conclusion' (4 criteria). Playlist also flags an
      'ArchaeoSAR Project to scan all the world's most important sites' (Grassi video, ~May 2026). [external]
- [x] 9 Nov: method nuggets from 9 Khafre Project videos (English auto-transcripts) → docs/BIONDI_TRANSCRIPT_NUGGETS_2026-11-09.md.
      Key: data = Capella + Umbra (+CSG); Biondi says Umbra 'power a bit insufficient'; Doppler band treated as acoustic, using
      HALF of 22–25 kHz (0–10 kHz) and 5–7 s sub-apertures; inversion = FFT ('global operation'); 'tuned the software … go as deep
      as you can'; 'kept on changing the parameters … in the end it's a sphinx'; 3-D models hand-built from ~200 tomographies;
      MATLAB→C++→CUDA. QUOTES UNVERIFIED (auto-transcripts) — check audio before any public use.
- [ ] Candidate (NOT pre-registered): Capella Giza scene (answers 'Umbra insufficient'); run his disclosed half-bandwidth +
      5–7 s sub-aperture configuration on the three Giza scenes. [Mac fetch + sandbox]
- [x] 8 Nov 2026 (Sun 18:30 AEST): Academia notified 'Corrado read your paper' — profile link slug CMalanga, i.e. Corrado
      Malanga (co-author of the retracted 2022 paper). He read the ACADEMIA copy, which still carries the August title
      ('A Controlled Reproduction of Single-Source…'). Expect any Khafre Project rebuttal this week to target that version.
- [x] 9 Nov: Academia work 169418222 updated to v6.3 (only the v6.3 PDF attached; title, DOI 10.5281/zenodo.24062309, abstract). [external]
- [x] 9 Nov: prebuttal table of 15 likely Khafre Project retorts, graded A/B/C → docs/PREBUTTAL_KHAFRE_2026-11-09.md.
      Open gaps to close: Capella Giza scene ('Umbra insufficient'); his disclosed half-bandwidth + 5–7 s windows.
- [x] 9 Nov: TEST J run (pre-registered 982586b, design agreed with Grok): his disclosed half-band and 5–7 s looks on Butte,
      Capella Cairo (35 s), Bingham, Komati + noise control. 12/12 runs surface-pinned (1.62–1.78 cells); falsification rule NOT
      triggered; P1 FAILED: two pinned Butte runs exceed 5× (5.59, 5.09); noise alone gives 4.14–4.18; ratio tracks overlap
      (Capella 6 s looks at 0.52 overlap: 1.88). → PREREGISTRATION_DISCLOSED_CONFIG_2026-11-09.md (results section).
      Follow-up same day: Giza ×3 (in data/ after all) + Vesuvius (from the 'My Passport for Mac' drive), Arm A only (collects
      1.2–5.0 s, so 5–7 s looks are impossible): 8/8 surface-pinned; 4 more pinned runs >5× (Giza 02-07 5.85/6.23, 03-08 5.41,
      Vesuvius 5.33). Total 20 runs, 20 pinned, 6 over 5×, falsification rule never triggered. External drive also holds Vesuvius
      and four more Bingham-area Umbra passes (2024-01-11, 02-26, 03-11, 05-08).
- [x] 9 Nov POST-HOC overlap sweep (Hassan's hypothesis): pure noise's alignment-null ratio rises with look overlap and
      exceeds 5× at 0.93–0.95 in 4/5 noise images → the fixed 5× rule is invalid at the half-band overlaps; main cause of P1
      failure. Residual: at 0.90 four real scenes sit just above the 5-seed noise range (5.0–5.8 vs ≤4.27); peaks always 1.5–1.9 cells.
- [ ] Revision: replace the fixed 5× rule with a configuration-matched noise threshold (e.g. noise 95th percentile at the same
      overlap, many seeds); report the Test J P1 failure and this post-hoc explanation together.
      DECISION (Hassan, 9 Nov 12:08): HOLD — do not revise the paper now. Keep Test J + the overlap sweep for the PCI response
      letter; reviewers are expected to raise the settings question. Note: the repo is public, so these results are already visible.
- [x] 9 Nov: MDPI letter of concern on Biondi 2022 Vesuvius (Remote Sens. 14(15):3828) SENT 08:04 → docs/MDPI_CONCERN_VESUVIUS_2026-11-09.md.
      New findings in that paper: 200 Hz 'set by us' + 972 m/s set the depth scale; seismograph spectra plotted to ±22 kHz from
      IV.VCRE/VBKN HH channels that sample at 100 sps (INGV FDSN, checked 9 Nov); Jan vs Feb 2022 acquisition date conflict. [external]
- [ ] Candidate (NOT pre-registered): test I-b — narrower common-reference design: screened persistent-scatterer
      patches, control scored by look distance, chain-length dose–response, same estimator for both routes. [sandbox+Mac]
**Needs data fetched on Hassan's Mac (sandbox is 403-blocked from the S3 buckets):**
- [ ] Volcano breadth (Merapi scenes listed; download → run). IN PROGRESS.
- [ ] Butte rect-window anomaly (5.07 vs alignment null) + the "monotonic sites = the structured
      ones" caveat — the one real loose thread; needs Butte back + ≥1 more structured/unstructured pair.
- [ ] E12 on a real SICD → floor in metres via (R/V)·v_LOS (deliberately not done; referee-bait if rushed).

**External / administrative — CONFIRM CURRENT STATUS (I can't see these):**
- [x] PCI Archaeology (ArticleID #1130): recommender is Dr Francesca Di Palma; the errata letter
      (PCI_LETTER_v2_2026-08-14.md) WAS sent 14 Aug. One review was done by 14 Aug; a second reviewer
      was secured (Queffelec, 25 Sep 2026). Status: waiting on reviewer 2. Next action: none until
      reports arrive — then revise v4/v5 per reports + the errata list.
- [x] Retraction aftermath (checked 26 Sep): Biondi publicly contests the retraction and demands the
      journal specify the errors (the notice is non-specific) — our preprint is the specific,
      reproducible version. Team continues promoting the "Second Sphinx" via presentations, now citing
      AI facial-recognition "88-96% match" — see BIONDI_IMAGERY_ANALYSIS_2026-09-03.md (detail comes
      from model/AI downstream, not radar). Sources: Retraction Watch 31 Aug 2026; MDPI rs18162679.
      Re-checked 27 Sep: errors still not itemised publicly; RW adds that Conyers, asked to review in 2022,
      declined to recommend without a reviewer who understood the equations; public critiques target
      penetration, not the micro-motion mechanism (our paper's niche). Verified in arXiv v1 intro: an
      irrelevant cold-fusion-in-lithium citation [24]. No public Zebker result; no September Biondi rebuttal found.
- [ ] Line-numbered PDF if a reviewer asks.
- [ ] Email Pomposi (ally).
- [x] 9 Nov: ICB (Rosan Dahal, Year 9 STEM) asked for a deck + invited Hassan to present. Deck built:
      docs/outreach/Radar_and_the_Pyramids_Year9.pptx. Reply sent 13:46 (no attachment); deck sent in a follow-up 13:50, attachment confirmed.
- [ ] 10 Nov: Grassi trailer "THE BIONDI VALIDATION" (x.com/GrassiTrevor/status/2119825208802676982). Premiere 11 Nov 11:11 GMT (9:11 pm Brisbane) on youtube.com/@trevorgrassi. Likely claim: the 2022 Khufu map matches ScanPyramids' North Face Corridor. Pre-premiere criteria recorded as prebuttal #16. Watch the video before replying.
- [x] 10 Nov: 2022 Khufu paper re-read for its treatment of known/later-confirmed structures and its acquisition table
      → docs/REVIEW_BIONDI2022_KHUFU_2026-11-10.md. New: paper says SAR found "no trace" of the muon Big Void (names another
      object "Big-void"); its NFC = 15.4 × 5.7 m room + 43.9 m conduit to the Grand Gallery vs the real 9 m × 2 m blind corridor
      (2023); metres were measured on the CAD with screen-ruler software; Table 1 (stripmap, PRF 2 kHz, 6 m antenna) cannot carry
      12.5 kHz/24 kHz and gives δz ≈ 46 m by their own formula (arXiv only, confirm in journal PDF); "ramps" at 42° = arris slope 41.99°.
- [x] 10 Nov: **H2 (topographic parallax) WITHDRAWN, test K cancelled** before any pre-registration or data. Straight-line
      SAR is symmetric about the flight line, so height gives no look-to-look shift in a slant-plane image; real-orbit residual
      is 0.003-0.08 px per step per 100 m (below the 0.2 px floor). Geometry tool kept: src/test_k_parallax.py.
      Also corrected: our Giza centre crops ARE on Khufu/Khafre (SCPs), not flat ground. -> REVIEW_BIONDI2022_KHUFU section 6.
- [x] 10 Nov: tracker check on the pipeline's own looks, synthetic + real Giza 02-07 -> RESULTS_TRACKER_BIAS_2026-11-10.md.
      True 2 px shift read by phase correlation as 0.18 at 11 looks (same fact as E12's "12% survives", already known), 0.02 at
      32, ~0 from 64; NCC 1.9 at 11, 1.1-1.4 at 32, 0.1-0.2 at 128. Cause: zero-lag peak of un-windowed whitened phase
      correlation. Circular patch plants (tests F, G, I) are read exactly at any look count, so they test the back end only.
- [ ] PCI revision wording (HOLD): state the attenuation and cause in section 5.6; qualify the 4/4 planted controls as circular
      patch plants; qualify the 11-128 look-count claim (tracker cannot register real shifts from ~32 looks).
- [ ] Candidate (NOT pre-registered): Giza x3 at 11 looks with NCC + noise-matched threshold, to answer "your tracker is deaf".
- [ ] Synthetic only, to verify: shared-band blindness (overlapped looks give zero gain to real slow-time motion on speckle).
- [ ] Remaining candidates from the review (NOT pre-registered): L Khufu known-chamber test with symmetry controls;
      M solid-pyramid simulation; N overlay permutation test on their figures; O dated scorecard of the 2022 CAD vs 2023.
- [ ] Watch: ICB line-manager decision on an in-person talk; agree a date only with Hassan (he works days).

## 4. Environment / mechanics (saves a session of rediscovery)

- Live repo on the Mac: `~/subsurface-sar-tomo` (Passport drive died Aug 13; repo rebuilt from GitHub).
- The Cowork sandbox mounts it but starts WITHOUT sarpy/scipy → `pip install sarpy scipy` each session
  (~35 MB; ~1 clean shot). Sandbox + cloud container are BOTH 403-blocked from Umbra/Capella S3 —
  new scenes must be fetched on the Mac, then the mounted pipeline runs on them.
- GOTCHA: `runs/` is gitignored and its figure PNGs are GONE except what today's runs regenerate.
  The 8 paper figures survive ONLY inside the committed v5 PDF. To rebuild the paper, first restore
  figures: `git show HEAD:paper/Giza_..._v5.pdf > /tmp/o.pdf` then extract page-order images to
  `runs/` (see the 2 Sep session; Figs 2/3/4 = Butte/Bingham data are gone and can ONLY be recovered
  this way). Otherwise build_v5.py silently drops missing figures.
- Working style: one terminal command at a time; honesty over hype; be the honest counterweight to
  Grok's optimism (Hassan's explicit preference).

## 5. Doc map (what's current vs superseded)

- **CURRENT:** this file, RESULTS_FIGURES_2026-09-27.md, RESULTS_SHAPE_METRIC_GIZA_2026-09-26.md, HOW_BIONDI_DOES_IT.md (the consolidated mechanism account), TECHNICAL_BIBLE.md (v1.5), paper v5 PDF, the three RESULTS_*_2026-09-02.md,
  REVIEW_INDEPENDENT_2026-09-02.md, FIVE_SITE, SENSITIVITY_RESPONSE_BIONDI.md.
- **STALE — do not use for status:** docs/private/HANDOFF.md (dated ~1 Jul: says "Bingham in flight /
  paper done" — both superseded by v5 + Giza + retraction). Kept for history only.
