# PROJECT HANDOFF — Subsurface SAR Doppler Tomography

*Single-document state of the project so anyone (you, a collaborator, or a fresh AI session) can
pick up exactly where we are. Last updated 2026-06-29, mid-session, during the Bingham stacking
downloads.*

---

## 1. What this project is

An independent, **validation-first reproduction and refutation** of Filippo Biondi & Corrado
Malanga's SAR Doppler micro-motion tomography — the method behind the disputed 2025 "underground
city beneath Giza" claims. We rebuild the method from their own papers and patent, add the controls
they skipped, and test it against known ground truth.

**Core thesis (now strongly established):** the *measurement* front-end (satellite radar as a remote
surface vibrometer) is legitimate; the *deep tomography* claim is unsupported and **reproducible as
an artifact**. We have shown, on real data, how the confident "structures" arise.

Read first: `docs/TECHNICAL_BIBLE.md` (v1.3 — §8.3 holds the publication / DOIs / PCI-submission record), then `docs/BIONDI_PATENT_RECIPE.md`.

---

## 2. Current status (one line)

Four real sites all null with passing controls; we then **decoded Biondi's patent (the "steering
matrix" is literally a DFT; depth set by an unphysical 22 kHz)**, **reproduced his recipe on Butte
and got a confident 1720× "detection" that our guards expose as a surface-pinned artifact**, and wrote a
**standalone refutation preprint**. The **Bingham multi-pass stacking experiment is now COMPLETE**
(5 same-geometry passes of a known-empty pit: per-scene mean 117.8× → stacked 96.7× vs null 1.5×,
**peak pinned at ~3 m = artifact reinforced by stacking, not real**) — folded into the refutation as
**Figure 4 in §3.5 (claim C5 closed)** and the PDF rebuilt. **The refutation paper is complete.**
Cross-sensor 5th site **DONE**: free **Capella "Cairo" spotlight SICD** (central Cairo, ~7 km off the
Giza plateau — no free scene covers the pyramids themselves; `fetch_capella.py` added). Result: reg
quality 0.62, **REAL 2.8× / null 1.6× → NULL, positive control PASS** — same null on an independent
sensor, so the Umbra nulls aren't sensor-specific (turns C5's cross-sensor "agreement" against the
claim). Folded into refutation Table 1 (now 5 sites / 2 sensors) + §3.4; PDF rebuilt (6 pp).
**Refutation paper complete and final.** Passed independent ChatGPT + Gemini + Grok review (all
converged, no factual/logical holes found): title softened to **"No Reproducible Evidence for Deep
Subsurface Structures…"**; added **patent→code fidelity Table 1** (block-by-block, from
BIONDI_PATENT_RECIPE.md); conclusion calibrated to "no reproducible evidence … reproducible as
artifacts"; Butte framed as the known-target benchmark; Derinkuyu/Cappadocia named as the paid-data
gold-standard next test. Rejected Gemini's rewrite (it reverted the title, re-overclaimed, and
mislabeled the stack as "coherent" and the front-end as "interferometric" — both false for our code).
Blurb drafted: `paper/Academia_upload_blurb.md`. **Preprint-ready.**
**Refutation PUBLISHED to Academia** (2026-06-30) as a new work — title "No Reproducible Evidence for
Deep Subsurface Structures Beneath the Giza Plateau…", clean abstract, year 2026, tags (Remote Sensing,
Synthetic Aperture Radar, Archaeological Prospection); auto-post skipped. **Stale 3-site v1 (work
169350197) DELETED** — profile now shows the new refutation + the 4-site v2 null-result, no duplicate.
**Academia housekeeping COMPLETE.** Optional future: a formal journal-formatted version (IEEE TGRS /
Remote Sensing of Environment / MDPI) with display equations and H1–H5 framing — not required for
preprint; and the user may write a measured announcement post (not auto-hyped).

**MERGED, PUBLISHED OPEN, AND SUBMITTED FOR FREE PEER REVIEW (2026-07-01).** The two SAR papers were
**merged** into one reproduction-and-refutation manuscript (`paper/Giza_SAR_Doppler_Reproduction_and_Refutation.pdf`,
built by `paper/build_merged.py`). Code/data are **open on GitHub** (github.com/Hassanforeman/subsurface-sar-tomo —
MIT license, CITATION.cff, rewritten README, release **v1.0.1**) and **archived on Zenodo**: code/data DOI
**10.5281/zenodo.21065675**, **preprint DOI 10.5281/zenodo.21066657**. The manuscript was **submitted to
PCI Archaeology** (Peer Community In — **free / diamond OA**; IEEE GRSL ruled out as not-free beyond ~3 pp)
on **2026-07-01**: illustration = the Butte REAL-vs-Null-vs-ground-truth figure, opposed reviewers
**Biondi + Malanga**, 5 suggested reviewers, **9 suggested recommenders incl. Flint Dibble**, AI-use
disclosed, no COI. PCI's server was painfully slow (submit POST returned 200 but the next page hung
repeatedly; the draft auto-saved each time, no duplicates); the **submission went through and the author
completed the recommender step manually**. **Status: SUBMITTED, awaiting a recommender to take charge
(~20-day window); if none does, no public record and it can go elsewhere — backup venue PCI Statistics &
ML.** Every field value, URL, and DOI is recorded in **TECHNICAL_BIBLE §8.3**. Only optional follow-up: a
**line-numbered PDF** if a reviewer requests one. An overnight auto-retry scheduled task was created and
then **disabled** once the submission completed.

---

## 3. The person / working style

- User publishes as **Hassan Foreman** (Academia.edu). Email handle is hassanrasheid@.
- Novice with the terminal — **give ONE command at a time**, never batches on one line.
- Mac (Apple Silicon), **Python 3.13** (system 3.9 too old for sarpy).
- Prefers concise, direct, honest answers; **values intellectual honesty over hype**. He has been
  bringing "Grok" suggestions to cross-check — our job has repeatedly been the honest counterweight
  (Grok tends to over-optimism). Keep doing that.

---

## 4. How the files work (mechanics)

- Live project on the user's Mac at **`~/Desktop/subsurface-sar-tomo/`**, connected to Cowork, so the
  assistant can read/write it directly with Read/Write/Edit.
- Resume with `cd ~/Desktop/subsurface-sar-tomo`.
- The assistant can't run the user's local Python (sarpy + data) — **the user runs `--sicd` commands
  on their Mac and pastes results**; the assistant tests pure-numpy `--selftest` paths in its sandbox.
- Big SICDs (0.8–7 GB) download via `src/fetch_umbra.py` into `data/` (gitignored). Downloads are
  **silent** and boto3 writes to a **temp filename** (`..._SICD.nitf.<random>`) until complete, then
  renames. Use `bash check_downloads.sh` to see status.

---

## 5. Repository layout (current)

```
subsurface-sar-tomo/
├── HANDOFF.md                  <- this file
├── check_downloads.sh          status of the Bingham stacking downloads
├── docs/
│   ├── TECHNICAL_BIBLE.md      v1.2 — full reference (incl. §5 blind spots, §8.1 results, §8.2 reproduction-unmasking)
│   ├── BIONDI_PATENT_RECIPE.md the decode: steering matrix = DFT; 22 kHz; processing chain
│   ├── BIONDI_METHOD_ANALYSIS.md how the depth claim works + disclosed dataset clues (200+ scans)
│   ├── BUTTE_GROUND_TRUTH.md    West Camp workings (Travona 1500 ft; water table ~160 m) + §3a depth profile
│   ├── VALIDATION_PLAN_v2.md    corrected plan; Lever 0 = multi-acquisition stacking
│   ├── EXTERNAL_REVIEW_3.md     3rd review + our velocity/steering-matrix pushback
│   ├── MEDIA_QA_PREP.md         interview prep (incl. hostile Qs) — plain-speak answers
│   ├── COMMERCIAL_ASSESSMENT.md honest read on the GUI/business idea
│   ├── DATA_AND_OFFERING_MAP.md data landscape, accuracy, competitor table, offering map
│   ├── PROJECT_PLAN.md / VALIDATION_PROTOCOL.md  (older planning docs)
├── src/
│   ├── fetch_umbra.py          list/download free Umbra scenes
│   ├── inspect_scene.py        read SICD/CPHD, params, quicklook
│   ├── subaperture.py          Doppler sub-apertures + sub-pixel shift + MCA (range sub-bands)
│   ├── micromotion.py          adjacent-pair tracking, detrend, + LRSD robust-PCA denoise
│   ├── tomogram.py             END-TO-END + all controls + 22 kHz knob + guards + ground-truth/f-compare plots
│   ├── steering_stress_test.py pure-numpy proof of the inversion's blind spots (off-grid alias etc.)
│   └── stack.py                multi-acquisition stacking (Lever 0)  <-- ACTIVE EXPERIMENT
├── paper/
│   ├── build_paper.py + Single_Pass_SAR_Tomography_Reproduction.pdf   (null-result preprint, v2 w/ Butte)
│   └── build_refutation.py + Refutation_Giza_SAR_Doppler_Tomography.pdf   (the step-by-step refutation)
├── data/    raw SICDs (gitignored)        runs/   output figures
```

All `src/*.py` have a `--selftest` (pure numpy, sandbox-safe) and a `--sicd`/`--sicds` real-data mode.
**Every self-test currently passes** (subaperture incl. MCA; micromotion incl. LRSD; tomogram A–G;
stack A–B).

---

## 6. The big result this session — patent decode + reproduction-and-unmasking

1. **Patent decode (`docs/BIONDI_PATENT_RECIPE.md`).** Biondi's patent (WO2024008365A1) states, verbatim,
   that the "steering matrix" *is a Digital Fourier Transform*, and the depth focus is "the DFT
   operator." So depth = the power spectrum of the sub-aperture residual — a DFT draws structure from
   *any* input. Our pipeline already does exactly this. The patent also discloses a **22 kHz**
   investigation frequency (ultrasonic; physically impossible for ambient seismic) and master/slave
   **range-Doppler (MCA)** sub-banding.
2. **Depth is a free parameter.** Self-test [E] + the `--f-compare` figure prove f only *relabels* the
   depth axis (δz=vR/2Af). The *same* Butte tomogram reads ~5 m at 22 kHz, ~100 m at 1 kHz, ~2 km at
   50 Hz. "Deep" is a dial, not a measurement.
3. **Reproduction-and-unmasking (TECHNICAL_BIBLE §8.2).** Running Biondi's recipe on Butte
   (`--n-sub 256 --n-chirp 3 --lrsd --f-investigation 22000`) gives a confident **1720× "ABOVE NULL"**
   that *passes a naive null test* — but it is **pinned at the surface (~4 m; 87% of energy in the
   shallowest 5%)**, matches none of the documented workings or the 160 m water table, and only appears
   at high sub-aperture count. New guards (**near-surface guard**, **sub-aperture-count stability**)
   flag it correctly as a surface/DFT artifact. This is, in miniature, how a Giza "shaft" is made.

**Pipeline additions this session:** MCA (`subaperture.multichromatic_subapertures`), LRSD
(`micromotion.lrsd_denoise`), and in `tomogram.py`: `metric_depth_axis` (the v/f knob), hardened
damped positive control, `shallow_pinned` near-surface guard, `look_count_stability` guard,
`_plot_compare` (vs ground truth), `_plot_fcompare` (relabelling). Flags: `--n-chirp --lrsd
--velocity --f-investigation --ground-truth --stability --f-compare`.

---

## 7. Results (all free Umbra X-band spotlight)

| Site | Collect | Reg. quality | Real/Null (honest n_sub) | Verdict | Pos. ctrl |
|---|---|---|---|---|---|
| Bingham Canyon | 2024-01-12-04-09-18_UMBRA-05 | 0.67 | front-end only | no signal | n/a |
| Komati Power Stn | 2023-08-13-07-03-04_UMBRA-05 | 0.85 | 50×/10× | null | n/a |
| Mount Vesuvius | 2023-11-15-19-47-28_UMBRA-05 | 0.72 | 4.1×/1.5× | **NULL** | PASS |
| Butte, MT | 2024-03-07-04-48-26_UMBRA-04 | 0.82 | 3.3×/1.4× | **NULL** | PASS |

Four sites, four nulls, all positive controls passing — including Biondi's own Vesuvius. The only
"detection" we ever produced is the deliberate 22 kHz / high-n_sub **artifact** on Butte (§6).

---

## 8. The two papers

- **Null-result preprint** — `paper/Single_Pass_SAR_Tomography_Reproduction.pdf` (v2, four sites incl.
  Butte). Published to Academia.edu (older 3-site version was replaced; v1 still on profile — user
  wanted v1 deleted but Academia rate-limited us; **left for the user to delete manually**, work id
  169350197).
- **Refutation preprint (NEW, the centerpiece)** — `paper/Refutation_Giza_SAR_Doppler_Tomography.pdf`.
  Rigorous, fair, step-by-step refutation of the Giza claims (C1–C5), embeds the reproduction figures,
  states falsifiability, critiques method-not-intent. **Built via `python3.13 paper/build_refutation.py`.**
  **One section still open: §3.5 wants the Bingham stack figure** (see §9).

---

## 9. Bingham multi-pass stacking (Lever 0) — ✅ COMPLETE

**Result (2026-06-29):** 5/5 passes downloaded and stacked (`--n-sub 128`). Per-scene mean contrast
**117.8× → stacked 96.7× (stacked null 1.5×)**, stacked **peak at ~3 m (2% of axis; 36% energy in top
5%) → SURFACE-PINNED → artifact reinforced by the stack, NOT real** (`runs/stack.png`). Prediction
confirmed. Folded into `build_refutation.py` as **Figure 4 in §3.5 (claim C5 closed)**; abstract +
conclusion updated; PDF rebuilt (5 pp). **Refutation paper complete.**

**Why (original):** Biondi's strongest-sounding defence is "200+ scans across 4 satellites all agree." Stacking a
**known-empty** site (Bingham = bare open-pit rock, no void) tests whether stacking *manufactures*
false consistency. Prediction: the surface-pinned artifact reinforces → consistency is an artifact
property, not evidence → closes refutation §3.5 (claim C5) with real data.

**5 same-geometry passes (UMBRA-05, ~04:1x):**
```
2024-01-12-04-09-18_UMBRA-05   COMPLETE
2024-01-11-04-14-45_UMBRA-05   COMPLETE
2024-02-26-04-16-52_UMBRA-05   DOWNLOADING (~394 MB of ~800)
2024-03-11-04-16-18_UMBRA-05   TODO: fetch
2024-05-08-04-09-56_UMBRA-05   TODO: fetch
```
Fetch the remaining two (one at a time, ~800 MB each, silent):
```
python3.13 src/fetch_umbra.py --task "Bingham Copper Mine" --collect 2024-03-11-04-16-18_UMBRA-05 --products SICD
python3.13 src/fetch_umbra.py --task "Bingham Copper Mine" --collect 2024-05-08-04-09-56_UMBRA-05 --products SICD
```
Check progress: `bash check_downloads.sh` (it prints the stack command when 5/5). Then:
```
python3.13 src/stack.py --sicds data/2024-01-12-04-09-18_UMBRA-05_SICD.nitf data/2024-01-11-04-14-45_UMBRA-05_SICD.nitf data/2024-02-26-04-16-52_UMBRA-05_SICD.nitf data/2024-03-11-04-16-18_UMBRA-05_SICD.nitf data/2024-05-08-04-09-56_UMBRA-05_SICD.nitf --n-sub 128
```
**Then:** read `runs/stack.png` + the verdict; if it confirms the prediction, add it to
`build_refutation.py` as Figure 4 in §3.5 and rebuild the PDF. That makes the paper airtight.

---

## 10. Commercial investigation — DONE, honest conclusion

Explored a GUI/service business (`docs/COMMERCIAL_ASSESSMENT.md`, `docs/DATA_AND_OFFERING_MAP.md`).
Honest findings: the use cases the user imagines (settlement of foundations/roads) are **slow
deformation = InSAR (multi-pass)**, which is **a different tool than our single-pass vibration front
end** and an **already-served market** (Geomotion, Kurloo [QUT, Queensland], Sixense, etc.). Our front
end is **cm-class, unvalidated**, vs competitors' mm-class. Satellite vibration sensing has been
unmonetized for ~15 years — a strong "thin market" signal. Free global data (Sentinel-1, NISAR) only
feeds the InSAR product we *don't* have; our method needs paid spotlight tasking. **Verdict:** the real
prize is the paper + validation/honesty brand, not a product. If ever revisited: do customer-discovery
calls first, build nothing, never claim anything underground (it would discredit the paper).

---

## 11. Key facts not to lose

- **Steering matrix = DFT** (his patent). **22 kHz** investigation frequency is the unphysical knob
  that fakes deep, fine resolution. **f only relabels the depth axis** — proven.
- Depth res δz=λR/2A with λ the **seismic** wavelength; band-independent; "Ku for resolution" is wrong;
  the drone win is **geometric aperture**, not band.
- **Biondi is not single-pass:** "series of SAR images" (2022 abstract); "more than 200" scans across
  COSMO-SkyMed/Capella/Umbra/ICEYE (Joe Rogan 2026). Consistency across scans ≠ truth.
- **Mosul Dam = his legitimate surface work** (peer-reviewed); Giza deep tomography is the overreach.
  Use this contrast.
- Controls that matter (the original work has none): null, in-data positive control (now also a
  hardened damped variant), surface-leakage, **near-surface guard**, **sub-aperture-count stability**
  (qualified: stable-but-surface-pinned = artifact, not real).
- Patent WO2024008365A1 is lapsed/ceased. Independent repros: not-JASH, mfwarren (Nyquist, dimensional,
  mirror-symmetry; Sentinel-1 TOPS is the wrong mode).

---

*To resume (updated 2026-07-01): the experiments and the paper are **DONE**, and the merged manuscript is
**public (GitHub + Zenodo DOIs) and submitted to PCI Archaeology for free peer review**. See
TECHNICAL_BIBLE §8.3 for every DOI, URL, and form value. The next checkpoint is **external**: wait ~20
days for a PCI recommender to pick it up. If a reviewer asks, build a **line-numbered** version of the
PDF (the one open to-do). If no pickup, resubmit to **PCI Statistics & ML**. The Bingham stack and the
cross-sensor Capella site are already folded in; the commercial idea is parked with an honest "probably
not" in §10. The overnight PCI auto-retry task has been disabled.*
