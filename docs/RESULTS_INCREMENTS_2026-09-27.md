# The increments anomaly against a look-order-shuffle null — pre-registered test H — 27 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_INCREMENTS_2026-09-27.md` (committed `f2f5a3a` before the run).
**Script:** `src/increments_order_null.py` (run at `f2f5a3a`). **Output:** `runs/increments_order_null.json`.
The run reproduces the 2 Sep E8 numbers exactly (increments peaks 1.876 / 3.826 / 1.95 cells).

## 1. Result by the pre-registered rule: NOT ANOMALOUS

| Scene | cumsum peak | increments peak | lag-1 of increments | shuffle-null median | null pins (≤ 2 cells) | observed percentile | verdict |
|---|---|---|---|---|---|---|---|
| 02-07 U05 | 1.75 | 1.88 (PIN) | +0.10 | 3.77 | 14% | 10.3% | not anomalous |
| 02-08 U04 | 1.67 | 3.83 (clear) | −0.13 | 3.70 | 16% | 55.8% | not anomalous |
| 03-08 U04 | 1.77 | 1.95 (PIN) | +0.02 | 3.72 | 13% | 12.0% | not anomalous |

No scene falls below the 5th percentile of its own order-shuffle null → **NOT ANOMALOUS (0 of 3)**. The
order of the increments across looks does not pull the peak toward the surface beyond what shuffled
orders of the same values do.

## 2. Stated plainly, including what does not fit our prediction
- **Grok's mechanism is ruled out:** the increments are not smooth (lag-1 +0.10, −0.13, +0.02). Serial
  correlation from overlap is not what pins them.
- **Our H.2 chance estimate was too generous.** We argued from the white-noise arm (31% pinning) that
  "2 of 3 pinned" had P ≈ 0.23. Each scene's own shuffle null pins only 13–16% of the time; under those,
  P(≥ 2 of 3 pinned) ≈ 0.05. Both pinned scenes also sit on the surface-ward side of their nulls (10th
  and 12th percentiles). A post-hoc Fisher combination of the three percentiles gives p ≈ 0.13 (not in the
  rule; reported so it cannot be said we hid it).
- **So:** the anomaly is not an order effect and does not reach the pre-registered bar, but it is not a
  clean mid-null either. What remains is a weak surface-ward lean in the increments' values (not their
  order) on two scenes — likely the distribution of per-tile increment magnitudes interacting with the
  deg-2 detrend, untested. It stays reported as a small open residual, not explained and not evidence of
  structure. All three scenes remain full detection nulls.

## 3. Paper wording
Keep "sufficient generating mechanism demonstrated"; do not write "end-to-end established". Replace the
§5.4 caveat with: "On two of three Giza scenes the de-accumulated peak stays within 2 cells; against a
per-scene look-order-shuffle null this is not significant (10th and 12th percentiles; pre-registered
α = 0.05), and it is not caused by serial correlation of the increments (lag-1 ≤ 0.10)."
