# Pre-registration H — is the "increments anomaly" more than chance? — 27 Sep 2026

*Committed BEFORE `src/increments_order_null.py` is run on any SICD. Only its synthetic selftest has run.*

## H.1 The open item
STATE §1 / RESULTS_GIZA_REPEATS §3: after removing the running total (`cumsum`), the peak stays "pinned"
(≤ 2 cells) on 2 of 3 Giza scenes (02-07: 1.88 cells; 03-08: 1.95), while 02-08 unpins (3.83). Grok (round
3) named this the gap a referee would cite, and proposed that overlap makes the increments serially
correlated ("already smooth"), pinning the peak without accumulation.

## H.2 What the existing E8 record already says (post hoc, stated before the new run)
From `runs/followup_increments_giza_*.json` (no new computation):
- Real increments are NOT smooth: lag-1 autocorrelation +0.087 (02-07) and +0.018 (03-08). Grok's "ρ ≳ 0.5"
  mechanism does not hold on our data; AR(1) prewhitening would change almost nothing, so it is dropped.
- The white-noise arm of the same experiment: increments peak median 2.80 cells, sd 0.98, **pinned 31% of
  the time**. The real values (1.88, 1.95) are ~0.9 sd below that median, and 1.95 sits just under the
  2-cell guard. If each scene independently has a ~31% chance to "pin", P(≥ 2 of 3 pin) ≈ 0.23.
- So the anomaly may be a threshold effect at chance level. That is a hypothesis from existing numbers; the
  run below tests it properly with a per-scene null instead of the white-noise image.

## H.3 Test (fixed now)
Identical E8 configuration (512 centre crop, patch 64, 24 patches on the centre row, n_sub 11, overlap 0.8,
Hann, phasecorr, degree-2 detrend, 300 bins, guard 2 cells, dz_phys from 6000 m/s / 22 kHz / 650 km / 42 km).
Per scene:
- Observed: scene peak (cells) from the real increments.
- Null: 1,000 look-order shuffles of the same increments (per tile, positions 1–10 permuted, inc[0]=0 kept;
  seed 0). Keeps every increment value and its tile, destroys order across looks.
- **ANOMALOUS** iff the observed peak lies below the null's 5th percentile (order across looks pulls the
  peak toward the surface). Overall: **ORDER-DEPENDENT PINNING** iff ≥ 2 of 3 scenes are anomalous; **NOT
  ANOMALOUS** iff 0 of 3; otherwise MIXED.
- Reported, not in the rule: the null's pinned fraction (P(peak ≤ 2 cells)), lag-1, cumsum peak.

## H.4 Positive control (synthetic, selftest)
White-noise increments sit mid-null (17th percentile → not flagged). Adding a one-cycle ordered component
across the looks (amplitude 1 sd of the increments — survives the deg-2 detrend, pins at ~1.64 cells) is
flagged at the 0th percentile. Control amplitude fixed on synthetic data only.

## H.5 Predictions (can be wrong)
From H.2: NOT ANOMALOUS — the observed peaks sit inside the order-shuffle null on all three scenes, and
the null itself "pins" a substantial fraction of the time. If instead ≥ 2 scenes are anomalous, there is an
ordered component in the Giza increments (look-index bias, Doppler-centroid drift, or surface spacing)
that the running total does not explain, and it will be reported as a third mechanism.

## H.6 What it cannot change
Test F, G and the C.4 verdicts; all three scenes remain nulls for detection either way.

## H.7 Result
*To be appended after the run. Deliberately empty at commit time.*
