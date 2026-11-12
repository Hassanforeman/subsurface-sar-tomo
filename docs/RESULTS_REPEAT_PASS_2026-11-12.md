# Test R result — the patch pattern does not repeat between Giza passes (within the test's sensitivity) — 12 Nov 2026

**Pre-registration:** `docs/PREREGISTRATION_REPEAT_PASS_R_2026-11-12.md` (successor to the inconclusive Test Q).
**Scripts:** `src/test_r_repeat_pass.py`, `src/test_q_repeat_pass.py`. **Outputs:** `runs/test_r_giza.json`,
`runs/test_r_selftest.json`, `runs/test_r_power_summary.json`.

**Read these three caveats with the verdict:**
1. **Unblinded.** The same-line and different-line correlations were already known from Test Q before the
   control was fixed. Only the control is new.
2. **Sensitivity.** Validated on synthetic data, the test detects a repeating signal of about one pixel of
   oscillating displacement (3 of 3 pairs) but not half a pixel (1 of 3). It says nothing about weaker signals.
3. **Our reconstruction** (S-like pipeline) on Umbra data, not Seyfzadeh's or Biondi's code or data.

## Result (16 ground lines, three passes, primary image)

| Pass pair | Same line | Different lines | Effect | p | Planted repeat (control) |
|---|---|---|---|---|---|
| 7 Feb - 8 Feb (one day apart) | 0.102 | -0.001 | +0.103 | 0.014 | 0.86 (pass) |
| 7 Feb - 8 Mar | -0.010 | 0.010 | -0.020 | 0.675 | 0.70 (pass) |
| 8 Feb - 8 Mar | -0.108 | 0.020 | -0.129 | 0.998 | 0.75 (pass) |

**Verdict by the registered rule: DOES NOT REPEAT** (p > 0.20 in 2 of 3 pairs; control passed 3 of 3).
A planted signal that sits in the same place on every pass gives correlations of 0.70-0.86. The real
lines give -0.11 to +0.10.

- The one-day pair shows a small, statistically significant repeat (+0.10). It is an eighth of what a
  planted repeat gives. Possible causes: surface features (same look geometry a day apart), or chance
  among three pairs. Not followed up.
- Secondary (look-alike settings): effects +0.03 / +0.01 / +0.01; its control passed only 1 of 3, so it is
  INCONCLUSIVE and adds nothing.

## Not done
- **Bingham x5: INCONCLUSIVE at placement** (no line could be matched across all five passes; needs a
  terrain model). No Bingham image was built.
- Test Q remains INCONCLUSIVE. RESULTS_FAKE_TARGETS s5 (post hoc, one line) stays "do not cite"; cite this
  document instead, with the three caveats.
