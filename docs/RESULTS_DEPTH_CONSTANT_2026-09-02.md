# The artifact depth constant, derived — 2 September 2026

Addresses the last un-derived item in the depth law (FIVE_SITE §15.5: "the constant 0.856 has
not been derived… leaving it empirical is the correct choice"). Script: `src/derive_depth_constant.py`
(`--selftest` passes). This does NOT find a one-line closed form — there isn't a clean one — but it
replaces "measured over noisy trials" with an **exact, parameter-free value**, which removes the
Monte-Carlo caveat flagged in FIVE_SITE §10.4/§15.

## 1. The exact object

The reported depth in cells is the argmax of the *expected* tomogram of a degree-d-detrended random
walk through the pipeline's own analytic-DFT operator — a closed matrix quadratic form with no free
parameter and no simulation:

    E[power(z)] = f(z)ᴴ · H (I−P_d) C (I−P_d)ᵀ Hᴴ · f(z)
    C[i,j]=min(i,j)+1 (random-walk covariance); P_d = degree-d polynomial projection (the detrend);
    H = analytic1d as a matrix; f(z)_k = exp(−i·Kz_k·z), Kz_k = k·2π/(n·DZ) (the pipeline steering).

## 2. The values (exact, converging in n)

| detrend degree | n=32 | n=128 | n→∞ (asymptote) |
|---|---|---|---|
| 0 | 0.8696 | 0.8688 | **0.869** |
| **2 (the pipeline)** | 1.6824 | 1.6800 | **1.680** |
| 4 | 2.4845 | 2.4753 | **2.474** |

**The 24-patch pipeline reproduces these to Monte-Carlo error** (selftest: deg2 n=128 → sim
1.687±0.075 vs exact 1.680; deg0 → 0.871 vs 0.869; deg4 → 2.491 vs 2.475). So the exact expected-
spectrum peak *is* the pipeline's peak.

## 3. What this settles, and what it corrects

- **The depth is derived, not fitted.** peak_cells at degree 2 = **1.680** exactly (parameter-free).
  The manuscript's simulated "1.69–1.71" is the same object measured on a coarser grid / finite
  patch count; state the exact 1.680 and note the earlier figures are its Monte-Carlo estimates.
- **There is NO single clean constant.** The empirical law k ≈ 0.856·(d/2+1) is only approximate:
  the true per-degree prefactor drifts (0.870 → 0.840 → 0.825 for deg 0/2/4). Each detrend degree
  has its own exactly-computable constant; they do not collapse to one multiplier. The paper should
  drop any implication of a universal 0.856 and instead cite the exact per-degree values.
- **The textbook (d+1)/2 rule (→1.5 at deg 2) is 11% low** because it is a continuum high-pass
  approximation invalid at low order / short records — consistent with FIVE_SITE §15.5, now quantified
  against the exact value (1.680) rather than a simulated one.

## 4. Honest limit

No elementary closed form for 1.680 was found; the peak is the argmax of a transcendental quadratic
form (detrended-Brownian-motion analytic spectrum) and almost certainly has none. The advance is
that the value is now exact and parameter-free, and the 24-patch pipeline is shown to realise it —
which is what "derived" should mean here. Defensible manuscript wording: *"the reported depth equals
the peak of the expected tomogram of a degree-2-detrended random walk, an exact parameter-free
constant of 1.68 resolution cells (0.87 and 2.47 at degrees 0 and 4), reproduced by the pipeline to
within Monte-Carlo error; the textbook 1.5 underestimates it by 11% as a known small-record artefact
of the polynomial-detrend high-pass approximation."*
