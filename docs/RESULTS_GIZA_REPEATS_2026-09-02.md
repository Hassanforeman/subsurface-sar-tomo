# Giza within-site repeatability — all three acquisitions — 2 September 2026

Closes the pre-registered prediction (`PREREGISTRATION_GIZA_2026-08-13.md`, prediction 8
and falsification condition iv) that was listed "untested" in v5 §10.4 and flagged by
the adversarial review as the most exposed loose end. Run on Fable-5-era pipeline,
deps freshly installed; all three free Umbra Giza scenes.

## 1. The three scenes

| Collect | Acq | Sensor | Array | az res | collect dur | role |
|---|---|---|---|---|---|---|
| 7e7cd796… | 2023-02-07-07-58-27 | UMBRA-05 | 5674×5351 | 0.827 m | 1.27 s | analysed in v5 (the paper's Giza row) |
| 44da7805… | 2023-02-08-07-54-55 | UMBRA-04 | 5674×5351* | ~0.83 m | ~1.3 s | repeat #1 |
| 5aa49658… | 2023-03-08-07-57-53 | UMBRA-04 | 10502×20272 | 0.209 m | 5.04 s | **pre-registered primary; Pomposi's scene** |

## 2. Headline: the null reproduces on all three; repeatability prediction HIT

| Scene | 8-pt ladder pinned | detections >5× | cumsum peak (cells, n=11) | tomogram verdict | pos ctrl | leakage |
|---|---|---|---|---|---|---|
| 7 Feb UMBRA-05 | 8/8 | 0/8 | 1.75 | indistinguishable from null | PASS | 0.07 |
| 8 Feb UMBRA-04 | 8/8 | 0/8 | 1.67 | indistinguishable from null | PASS | 0.07 |
| 8 Mar UMBRA-04 | 8/8 | 0/8 | 1.77 | indistinguishable from null | PASS | 0.10 |

**Pre-registered prediction 8 ("three acquisitions agree to ~0.1 cells"): HIT.** Cumsum
peak depth is 1.75 / 1.67 / 1.77 cells — a spread of 0.10 cells across three independent
acquisitions on two look-directions and a 4× resolution range (0.21–0.83 m). Every scene
is 8/8 surface-pinned with 0/8 detections. Falsification condition iv (peaks disagree)
is **not** triggered. The site the claim is about is a null on every free scene of it
that exists.

## 3. The §5.4 increments anomaly is reproducible, not a one-off — REPORT AS SUCH

The v5 open item (§5.4): at 7 Feb, removing the cumulative sum collapses contrast but does
NOT move the peak off the surface, unlike Bingham/Cairo. The repeats resolve which way this
goes — and it is the less convenient way for the mechanism story, so it must be reported:

| Scene | cumsum peak | increments peak | increments contrast | increments verdict |
|---|---|---|---|---|
| 7 Feb UMBRA-05 | 1.75 (PIN) | 1.88 | 1.86 | **stays PIN** |
| 8 Feb UMBRA-04 | 1.67 (PIN) | 3.83 | 1.43 | clears (unpins) |
| 8 Mar UMBRA-04 | 1.77 (PIN) | 1.95 | 1.62 | **stays PIN** |
| white noise | 1.71 | 2.80 | 1.49 | unpins (31% pinned) |

**Two of the three Giza scenes keep the peak pinned after de-accumulation** (7 Feb, 8 Mar),
while 8 Feb clears like Bingham/Cairo and like pure noise. Contrast collapses on all three.
So the §5.4 statement stands and is now *reproduced on a second scene*: at Giza, accumulation
is sufficient to generate the artifact (empty-input walks pin) and accounts for the contrast,
but is **not shown to be necessary for the surface-pinning** — a weak residual pinning survives
de-accumulation on 2 of 3 Giza scenes. This does NOT rescue the method: all three are still
full nulls (0/8 detections, 8/8 pinned). It means the honest wording in v5 §5.4 was right, and
the abstract/conclusion "the mechanism is identified" is too strong (matches the adversarial
review's W5). The residual +autocorrelation in the increments arm (7 Feb +0.087, 8 Mar +0.018,
8 Feb −0.100) is weak, scene-variable, and unexplained; report as open.

## 4. Bug fixed during this run

`experiment_increments` verdict-printer (the one §10.3 says was "corrected to read the row")
crashed with `KeyError: 'peak_median'` on every REAL scene: real rows carry keys
`peak_cells`/`contrast`, noise rows carry `peak_median`/`contrast_median`/`pinned_frac`, and
the printer read the noise keys unconditionally. Patched to read either schema (`_peak`,
`_contrast`, `_pinned` accessors). The printer now runs and prints the correct per-arm verdict
(shown above). This is exactly the class of defect the paper discloses in §10.3 — a fourth
instance — and should be added to that list. Backup at /tmp/fe.bak; diff is in src/.

## 5. What this changes in the paper

1. §10.4 "within-site repeatability untested" → now tested and HIT; move to results.
2. Table 3 / falsification condition iv "not met" → should read "tested across three
   acquisitions; prediction of ~0.1-cell agreement HIT; condition not triggered."
3. §5.4 → strengthen: the increments-arm pinning is reproduced on 8 Mar (2 of 3 scenes),
   so it is a site property, not a 7 Feb artifact; still a full null.
4. Add the printer KeyError to the §10.3 verdict-printer list.
