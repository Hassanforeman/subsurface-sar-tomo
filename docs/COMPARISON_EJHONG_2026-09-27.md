# ejhong/sar "SAR Depth, Tested" — what it is, and how it sits against our work — 27 Sep 2026

*Read from primary sources on 27 Sep 2026: site ejhong.github.io/sar, repo github.com/ejhong/sar
(README, METHOD_AUDIT.md, ROADMAP.md). Nothing here has been re-run by us yet. Where a point is our
reading rather than their statement, it is marked [ours].*

## 1. What it is

- **Form:** research notebook website + open code (GitHub, 7 commits). **Not peer-reviewed, not a paper,
  no DOI.** Undated; cites the 10 Aug 2026 retraction; METHOD_AUDIT has a "23 September 2026" section,
  so it is weeks old and still changing. Author identified only as "ejhong"; README says the simulation
  work was developed with Claude Fable 5.1, later review with Codex.
- **Code/results:** every experiment has a script (`experiments/rNN_*.py`), a downloadable results
  JSON and figures; tests in `tests/`. Per-run CSVs committed; large arrays not.
- **Data: NOT public.** Two ICEYE Spotlight Dwell Fine SLCs (Giza, ICEYE-X33, 2025-08-27; Sacsayhuamán,
  ICEYE-X35, 2025-08-22), ~10.5 GB each, "kept outside the repository". Only platform + date are given —
  no product IDs, no licence, no source. [ours] We searched the ICEYE open-data STAC catalogue: no Giza
  or Sacsayhuamán item found (the only 2025-08-27 item is Monaco, X44). So their numbers cannot currently
  be re-run by anyone else on the same pixels. Ours can (free Umbra open data, scene IDs published).
- **Formulation:** they implement the 2022 paper's steering form `Kz = 4π B⊥ / (λs r sinθ)` with B⊥ from the
  product's real state vectors, 50 reference/offset sub-aperture pairs, 32×32 complex registration to
  1/1000 px, common-reference tracking. We implement the patent's DFT steering with adjacent-pair
  tracking and `cumsum`. Two different routes to the same operator family.

## 2. What they independently CONFIRM of ours [ours: the mapping]

| Our settled result | Their matching result |
|---|---|
| Steering matrix = DFT; depth is a free relabel (22 kHz) | Kz on a uniform ladder → depth axis exactly periodic (27.4 m at Khafre, corr 1.000); scale set by a declared sound wavelength nobody measures (R2, R8, R15) — a uniform Kz ladder *is* a DFT |
| Grid over-extension manufactures an alias | Derivative protocol's grid runs past its own ambiguity limit (R2, R12) |
| Giza null; monuments ≈ empty ground; repeatable | Monuments vs desert standardised gap −0.007; Sacsayhuamán the same (R1, R6) |
| Rendering choices manufacture "architecture" from empty volumes | Rendered like the slides, real data shows wells everywhere, incl. empty plateau (R8) |
| Depth output carries nothing beyond the surface | Classifier: depth profiles AUC 0.51 at matched brightness (R5) |
| Output is a random walk; noise gives the same product | Their modal gate admits a structureless random walk 74% of the time (R15) |
| Undisclosed parameters prevent reproducing a specific figure | Stated identically in their audit |

## 3. Does anything of theirs NULLIFY or weaken ours?

Nothing overturns a settled item. Three things need care:
1. **Coherence (their R9/R10).** In a dwell, look separation = time = angle; coherence halves at 0.98 s.
   [ours] Our adjacent-pair looks overlap 80%, so each increment is coherent, but the accumulated
   trajectory spans the whole aperture. This does not weaken our mechanism — it gives a *physical reason*
   the increments are noise — but it means our HOW_BIONDI "Step 1: the surface-motion front end is real
   and stands" should be qualified: real for strong motion (bridges, ~1000 µm/s); the ambient
   microseism (0.1–10 µm/s) is below the measured floor (77 µm/s, their R4). **Action: soften wording.**
2. **Test F vs their T3.** They show (synthetic) that *surface scatterer spacing* predicts *apparent depth*.
   Our test F found *streak strength* is not predicted by surface *brightness / texture / registration*.
   Different quantity, different surface property — not a conflict, but it means our rejected hypothesis
   tested the wrong surface covariate if the real driver is spacing/periodicity. **New question Q4.**
3. **Their internal inconsistency to note, not rely on:** the site's R7 still quotes a 4,397 µm/s static
   floor while METHOD_AUDIT says that earlier number "should not be cited" (it measured a search window).
   Cite their R4 77 µm/s, not R7.

## 4. What THEY have that we don't (and whether to adopt)

| Their item | Value to us | Adopt? |
|---|---|---|
| R13 known-void positive control: hundreds of surveyed 5–30 m cemetery shafts vs bare plateau, brightness-matched: +0.031 | The strongest real-target control in the whole debate | **Yes, if our Umbra footprints cover the cemeteries** (Q1) |
| R14 physical budget: X-band reach 0.51 m (1,277× short), record 1.86 s vs 150 s (81×), floor 8×, lateral 97× | Four independent physical failures, citable | Cite |
| R16 resolution bound s² ≥ δaz·L·Vs → ≥ 27–52 m | Clean analytic; complements our Fresnel argument | Cite; check with Umbra numbers (Q2) |
| R9/R10 coherence-time measurement | Explains *why* increments are noise | Replicate on Umbra (Q3) |
| R11 seismic-array cross-correlation: injected 0.49 vs real 0.004 | Kills the "dense seismic array" steelman | Cite |
| R3 split dwell: halves agree 4.3% vs 1.3% chance; profile corr 0.067 vs 0.074 unrelated | We have a split/repeatability row (E8); theirs is per-pixel | Compare, maybe adopt |
| R12/R15 the public derivative protocol (BiondiProtocol GitHub, v1.7) run unmodified: integer-pixel registration, 1 km aperture placeholder vs 5–10 km real, gate AUC 0.504 | We had not looked at this code | Read it (Q6) |
| Second continent (Sacsayhuamán) | Breadth | Cite |
| Steelman benchmark: depth *is* recoverable under a favourable active-source physical model | Honest bound: the idea is not impossible in principle, the recording is | Cite |

## 5. What WE have that they don't

- The **patent-exact** operator and the `cumsum` random-walk mechanism; exact depth constant (1.680 cells,
  deg-2) derived; pure-noise reproduction with no SAR at all.
- Super-resolution inverters (Capon, MUSIC) also surface-pin.
- n_sub contrast inflation; taper and config objections answered.
- **Open, re-runnable data:** three free Umbra Giza scenes plus five other sites, two sensors.
- **Pre-registration** of every recent test (they state theirs is "not a preregistered trial").
- **Audits of the published imagery**, which they explicitly do not do: the 16 paired 2022 figures (and
  the journal version), the 2026 Second Sphinx deck (templates, GAN/face tools, chatbots), the Titanic
  photo overlay, shape metric on real Giza, streak test F.
- The podcast record (discarding runs that "made no sense"; "very often one was inverting noise").

## 6. New questions this raises (candidates; each needs its own pre-registration before running)

- **Q1 Known voids on Umbra.** Do our three Umbra Giza scenes' full footprints cover the Eastern/Western
  cemeteries? If yes: pre-register a cemetery-vs-plateau test with our exact pipeline (their R13 on open
  data). [sandbox: footprint from SICD XML; run on Mac]
  *Checked 27 Sep (SICD ImageCorners):* all three scenes span ~29.955–30.003 N, 31.106–31.161 E (~4.4 km
  square); scene centre point = Khufu (29.9793 N, 31.1340 E). The Western Cemetery (just W of Khufu) and
  Eastern Cemetery (just E) are inside every footprint. **Q1 is feasible on free open data.**
- **Q2 Our geometry's ambiguity depth.** Compute Umbra's along-track Kz ladder from state vectors; where
  does our 300-bin grid sit relative to the repeat? [sandbox, metadata only]
- **Q3 Coherence vs look separation on Umbra** (their R9): does it collapse inside our aperture? Would
  make "increments are decorrelation noise" measured, not inferred.
- **Q4 Surface spacing → apparent depth on real data** (their T3 was synthetic): does each tile's dominant
  surface spatial frequency predict its peak depth bin? The right follow-up to our rejected test F.
- **Q5 Increments anomaly** (STATE §1): does axis periodicity / operator structure explain the pinned
  peak after de-accumulation, independent of the walk?
- **Q6 Derivative protocol:** who maintains BiondiProtocol (their ROADMAP says send findings to
  "Seyfzadeh" — likely Manu Seyfzadeh, whose name appears on the ARF page) [inferred]; is it endorsed by
  Biondi or independent? README says it was built "using CHAT-GPT operating Python".
- **Q7 Provenance:** how did ejhong obtain the ICEYE scenes; can the product IDs be published so others
  can buy/request the same data?

## 7. Citation stance
Cite at revision alongside Pomposi as an independent, real-data, same-conclusion reimplementation via
the paper's Kz route; note it is not peer-reviewed and its data are not public. Consider contacting the
author (convergence + our open data would let them publish IDs-based cross-checks).
