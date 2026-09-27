# PROJECT STATE — single source of truth

**Read this first, before any other doc. Update this file at the END of every work session.**
Rule: if any other document disagrees with this one about *status*, THIS FILE WINS. For
*detail*, follow the pointer this file gives. When you close or open a question, edit the
ledgers below in the same session — that is how we stop doing double work.

*Last updated: 2026-09-27 (journal-version replication of step 2: images identical, no axes added, 15/16 again; C.4 step 2: the 2022 paper's paired figures measured — geometry is the model's; tomogram panels unscaled, 4/16 overlaid on known drawings. Previous: 26 Sep §7 step 1 negative).*

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
- **Depth constant derived exactly** (not just measured): peak = argmax of a parameter-free matrix
  quadratic form; deg-2 value = 1.680 cells (0.869/2.474 at deg 0/4), pipeline reproduces to MC error.
  No single clean constant — the 0.856·(d/2+1) law is only approximate. → RESULTS_DEPTH_CONSTANT_2026-09-02.md.
- **Super-resolution inverters (Capon, MUSIC) also surface-pin** (real Giza: Bartlett 1.75, Capon 1.99,
  MUSIC 1.75 cells) — the artifact is upstream of the inverter; "you used a weak inverter" is refuted.
  → RESULTS_INVERTERS_2026-09-02.md.
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
- **§7 shape metric, pre-registered step 1 (26 Sep): NEGATIVE.** Real Giza centre crops vs matched
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

## 2. Adversarial reviews already answered (don't re-litigate)

- Grok 29 Jul (config objections), Grok v2/v3 briefs, full dossiers v1/v2. → docs/private/GROK_*.
- Grok adversarial review of v5, 2 Sep — triaged; ~3 of its P0s already fixed in v5 (two Figure 4s,
  June footer, scene-ID disclosure); the rest valid. → ADVERSARIAL_REVIEW_v5_20260902.md (user upload).
- Independent from-scratch confirmation of the mechanism, 2 Sep. → REVIEW_INDEPENDENT_2026-09-02.md.

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
      different, later pipeline; step 2 says nothing about it). Source found 27 Sep: ~55 press-conference
      images published on archaeologicalrescue.org/secondsphinx/ "with permission". Descriptive first
      (axes? colour bar? voxel size? threshold?). [needs-data: download on Mac]
- [ ] Shape-metric near-miss (02-08 centre crop 4/8, mostly component-count arm, no vertical-extent
      gain; off-centre crops of 02-08 are all 0/8; 02-08 is the steepest look, incidence 29.4 deg vs
      36.8/35.3 for the other two, same side/azimuth). Framing: "two clean nulls + one unexplained
      near-miss" until tested: test the "surface content, not depth" explanation with a surface-matched null or a
      co-location test vs surface brightness. Secondary; cannot change the step-1 verdict. [needs-data:
      run on Mac] → RESULTS_SHAPE_METRIC_GIZA_2026-09-26.md §3.
- [ ] Paper: update §7 "provisional" wording + add step-1 result (at revision, per reviewer reports). [external]
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
- [ ] Line-numbered PDF if a reviewer asks.
- [ ] Email Pomposi (ally).

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
