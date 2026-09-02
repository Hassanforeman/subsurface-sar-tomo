# Independent review of preprint v5 — 2 September 2026

*Scope: full re-read of `paper/Giza_SAR_Doppler_Reproduction_and_Refutation_v5.pdf`, the
project record (technical bible, results docs, preregistrations, erratum), a from-scratch
reimplementation of the core mechanism claim written only from the paper's prose, a re-run
of every pipeline self-test, and verification of the paper's external factual claims.*

---

## 1. Verdict

**The science is sound.** The central negative result — that the published method, rebuilt
faithfully from the public disclosure and run with elementary controls, yields no evidence
of deep subsurface structure, and that its confident outputs are reproducible as artifacts
of accumulate-detrend-DFT processing — survives independent scrutiny. The paper's habit of
attacking its own statistics (§5.5), withdrawing its own overclaims (§10), and publishing
predictions before data (Giza, mines) is the strongest part of the work.

## 2. What was independently verified today

**2.1 The mechanism claim, from scratch.** A ~40-line numpy script was written solely from
the §5 prose (no repo code consulted): white Gaussian increments → cumulative sum →
degree-2 polynomial detrend → analytic signal → DTFT power on the steering grid, pooled
over 24 patches. Results:

| quantity | paper v5 | independent rerun |
|---|---|---|
| peak position, deg-2 detrend, n=11–128 | 1.69 ± 0.02 cells | 1.66–1.73 cells |
| peak position, deg-0 | 0.88 cells | ~0.91 cells |
| contrast growth, 11 → 128 looks | 72.9× | 72.3× (3.28 → 237) |
| increments (no accumulation) | flat | flat (1.47 → 1.65) |
| pure-noise pooled contrast at default n=11 | — | **3.28** — inside the real-site range (2.75–6.06) |

The last row is worth emphasising: an input containing nothing lands in the middle of
Table 2. This is exactly the paper's thesis, confirmed by an implementation that shares no
code with the repository.

**2.2 Code-level checks.** `tomogram.steering()` is verbatim a DFT basis; `invert_patch`
is the power spectrum of the analytic residual; `micromotion` builds the trajectory with
`np.cumsum`; the investigation frequency appears only in `metric_depth_axis` (axis
labelling) and nowhere in the inversion. §3.1, §3.2 and Table 1 are accurate to the code.

**2.3 Self-tests.** `subaperture.py`, `micromotion.py`, `stack.py`, `tomogram.py`
(A–G incl. hardened damped positive control and near-surface guard) and
`verify_claims.py` (DTFT identity to 2×10⁻¹⁵; rank-sweep tuple 1/19/78/141/208) all PASS
on this machine, 2 Sep 2026.

**2.4 Physics spot-checks.** At 22 kHz in rock (Q≈100, v=6000 m/s) the amplitude
attenuation over 648 m is e^(−πfr/Qv) ≈ e^(−75) — nothing survives; ambient seismic
energy sits below ~100 Hz; 11 looks in a 1.27 s collect sample at ~8.7 Hz. The paper's
§3.2 claims are conservative relative to the physics.

**2.5 External facts.** The retraction is real: Remote Sensing 18, 2679 (10 Aug 2026),
covered by Retraction Watch on 31 Aug 2026 ("serious methodological flaws and statistical
errors"; the authors disagreed). Retraction Watch does not mention this project, so the
paper's "I make no claim to have prompted that decision" is accurate and should stay.

## 3. Where a referee will push — prepared answers

**Q1. "You refuted your own reimplementation, not the authors' pipeline."**
The strongest objection, and §9 already contains the right answer: the conclusion is
scoped to *the method as published* (paper + patent, mapped block-by-block in Table 1);
any essential undisclosed step is precisely what the original authors must supply. §5.5
strengthens this: since four undisclosed filter taps can manufacture 100% false detections
from empty input, *no* pipeline can be evaluated without full disclosure. Keep the scoping
sentence in every answer.

**Q2. "Where does the degree-2 detrend come from?"** The 1.69-cell constant is a function
of detrend degree (independently confirmed: deg-0 ≈ 0.9, deg-2 ≈ 1.7, deg-4 ≈ 2.5–3.0
cells). The paper discloses the dependence but should state crisply whether degree-2 is
the disclosed method's choice or a reproduction choice — one sentence in §5.3 or Table 1.
Either way the artifact class is unchanged; only its cell position moves.

**Q3. "§3.1 says a DFT returns structured output from *any* input — that's false for
white noise."** A picky referee could poke this sentence: a DFT of white increments gives
a near-flat expected spectrum (independently measured: pooled contrast ~1.5, no pin). The
peakedness comes from the *accumulated* (random-walk) input, as §5 correctly develops.
Recommend tightening §3.1's wording to "any smooth or trend-contaminated input" so the
rhetoric matches the mechanism section. This is a wording fix, not a substance fix.

**Q4. "No p-values; the 5× rule is ad hoc; 48 runs are not independent."** True — the
eight n_sub rungs per site are strongly correlated, and the paper should not let "48 runs"
read as 48 independent tests (it currently lists the factors, which is fair). Cheap
strengthening for the journal version: permutation p-values against the alignment null at
the default setting, per site, with the caveat of §5.5 attached.

**Q5. "The Giza increments anomaly (+0.087) could be the real signal."** Prepared answer:
even in the increments arm the peak stays surface-pinned (1.88 cells) with contrast 1.86 —
below every threshold; an unexplained lag-1 autocorrelation of 0.087 is not a 648 m city.
Real ambient micro-motion (urban traffic, wind) is *expected* to correlate adjacent looks
weakly; that supports the front-end, not the depth inference. Candidate tests: the two
unanalysed Giza repeats, and time-of-day/site-type comparison.

**Q6. "Your pre-registered within-site repeatability test is still unrun."** The most
exposed loose end: two further Giza acquisitions are downloaded and unanalysed, and the
repeatability prediction was pre-registered. Run them before review concludes, or a
referee will ask why a registered prediction was left untested. Same for the promised ±20–50%
velocity/grid-coverage sweep (§8) and the pre-registered mines/Gran Sasso extension.

**Q7. "You call the front-end legitimate, then show it passes only 12% of a displacement."**
Clarify: legitimacy refers to the prior peer-reviewed uses (ships, bridges, Mosul Dam —
large coherent targets, mm-scale motion), not to this pipeline's sensitivity at
micro-motion amplitudes. E12's 12% transfer and the 0.2 px floor quantify exactly why the
same front-end cannot support the deep claim.

**Q8. E12 statistics.** The "confidence anti-correlated with truth" claim rests on medians
over ~8–12 trials at one depth and one n_sub. Add dispersion (5–95%) and a second planted
depth before leaning on it in interviews; the caveats are already in the results doc.

**Q9. "An AI wrote this."** The disclosure block already answers it: tools used
extensively, author directed and verified everything, every figure regenerates from the
pipeline, no AI-generated illustrations. The right posture in Q&A: the results are
checkable in minutes from the repo — provenance of the typing is irrelevant to whether
`verify_claims.py` passes.

## 4. Minor housekeeping

- Untracked files in the repo: `find_gran_sasso_v2_local.sh`, `kalgoorlie.bundle`,
  `sar-v5-stress-test.bundle` — commit or ignore deliberately.
- Three corrected verdict-printers are disclosed in §10.3; keep that disclosure in sync if
  any further printer is touched.
- The technical bible §8 predates v5's re-based nulls and withdrawn ratios (it still
  quotes 27×/50×/1720× era numbers in places); §8.5 added today records this review, but a
  fuller bible refresh against v5 is worth an hour.

## 5. Bottom line for public questions

The defensible one-sentence summary: *"Rebuilt exactly as disclosed and run with the
controls the original omitted, the method produces the same surface-pinned artifact
everywhere — including Giza — and its reported depths are an axis label set by an
unphysical, analyst-chosen frequency; every claim is reproducible from the open repo in
minutes."* Never extend it to "the published images are fake" (§7 is explicitly
unresolved) or "the authors acted in bad faith" (the paper disclaims intent, correctly).
