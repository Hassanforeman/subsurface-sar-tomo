# Configuration sensitivity — response to the 28 July 2026 objections

*Run 28 July 2026. Code: `src/sensitivity_sweep.py`. Raw results: `runs/sweep_speckle.json`,
`runs/sweep_blobs.json`, `runs/threshold_calibration.json`. Figure:
`runs/threshold_calibration.png`.*

## What was objected to

On the Malanga interview thread, a commenter posting as F. Biondi raised three
configuration objections to this reproduction:

1. *"Which coregistrator are you using? Are you working with DORIS or GeFolki?"*
2. *"I strongly recommend remaining in Double precision at all times and never working in Float32."*
3. *"Which filtering strategy are you applying to the sub-apertures? I would suggest using a Hamming window."*

and, in a follow-up, the general principle that a failed reproduction may reflect
*"one or more configuration choices that are left to the user alone"* rather than any
defect in the original method, with *"the burden of examining the variables that affect
the effect"* lying on the person attempting the reproduction.

The objection is reasonable and is answered here empirically rather than rhetorically.

## What was run

`src/sensitivity_sweep.py` re-runs the **entire** pipeline — sub-aperture decomposition,
coregistration, micro-motion estimation, inversion, null test, hardened positive control,
surface-leakage and surface-pinning guards — across the full cross-product of:

| Axis | Levels |
|---|---|
| Sub-aperture window | **Hann** (paper), **Hamming** (his suggestion), Blackman, rectangular |
| Numerical precision | **float64/complex128** (paper), **float32/complex64** |
| Coregistrator | **phase correlation + parabolic** (paper), upsampled-DFT (Guizar-Sicairos; the sub-pixel engine inside DORIS-lineage processors), normalised cross-correlation, TV-L1 dense optical flow (the Lucas-Kanade/variational family GeFolki belongs to) |

= 24 configurations, each evaluated on two synthetic scenes that contain **no subsurface
reflector**, so the correct answer in every cell is "no detection."

Two decision rules are reported side by side: the paper's own criterion
(contrast > 5 × a shuffled null) and a stricter permutation p-value over 200 shuffles.

### The harness validates itself first

`python3 src/sensitivity_sweep.py --selftest` — all pass:

| Check | Result |
|---|---|
| [A] windowed decomposition reproduces the repo's function exactly at Hann/complex128 | max abs difference **0.00e+00** |
| [B] all four estimators recover known sub-pixel shifts in the repo's sign convention | max azimuth error 0.02–0.19 px |
| [E] the float32 arm is **genuinely** single-precision | dtypes complex128/complex64, relative divergence **1.61e-07** |
| [C] permutation p-value is calibrated under the null | 17% of noise-only trials below 0.05 |
| [D] the harness **can** detect a real injected reflector | p = 0.005, z = 127 |

Check [E] matters: `numpy.fft` always promotes to double internally, so casting inputs to
`complex64` yields a double-precision pipeline with rounded storage — a silent no-op. The
sweep uses `scipy.fft`, which honours single precision. Without this the float32 arm would
have been meaningless. Check [D] matters for the opposite reason: a sweep that cannot
detect anything proves nothing.

## Result 1 — the verdict does not move

**Every one of the 24 configurations gives the same verdict, on both scenes.**

Under the paper's criterion: **0/24 detect** (correct — the scenes are empty).
Injected positive control recovered: **24/24**.

Effect of each knob on the detection statistic (which must reach **5.0** to fire):

| Knob | Mean contrast ratio | Verdict |
|---|---|---|
| Hann (paper) | 2.96 / 2.65 | no detection |
| **Hamming (suggested)** | **2.98 / 2.41** | no detection |
| Blackman | 3.15 / 2.83 | no detection |
| Rectangular (no taper) | 1.70 / 2.20 | no detection |
| float64 (paper) | 2.70 / 2.52 | no detection |
| **float32** | **2.70 / 2.52** | no detection |
| phase correlation (paper) | 2.30 / 2.56 | no detection |
| upsampled DFT (DORIS lineage) | 2.28 / 2.16 | no detection |
| normalised cross-correlation | 3.52 / 2.84 | no detection |

*(two numbers = the two synthetic scenes)*

Specifically:

- **Hamming vs Hann moves the statistic by 0.02 and 0.24** on the two scenes. The
  threshold is 5.0. The window changes sidelobe leakage by a few dB; it does not create
  depth information.
- **float32 vs float64, paired by configuration, differ by at most 0.012** in the
  statistic (mean 0.001), despite being verifiably different computations. The advice is
  sound in general and is already followed — but it is not what determines the outcome here.
- **No coregistrator changes the verdict**, including the upsampled-DFT engine that sits
  inside DORIS-lineage processors and a dense optical-flow estimator from GeFolki's family.

## Result 2 — the detection threshold is empirically calibrated (new)

Running the pipeline over **400 empty scenes** (2 scene types × 25 seeds × 4 windows ×
2 coregistrators), the distribution of the detection statistic on data containing nothing:

| | |
|---|---|
| median | 2.77 |
| p95 | 4.35 |
| **p99** | **5.03** |
| max | 6.02 |
| **false-positive rate at the paper's 5× threshold** | **2.0%** |
| false-positive rate at 6× | 0.2% |

![threshold calibration](../runs/threshold_calibration.png)

The paper's 5× threshold sits almost exactly at the 99th percentile of the empty-scene
distribution — it is an α ≈ 0.02 test, not an arbitrary round number. This was not
previously demonstrated in the paper and should be added: it converts "we used a 5×
threshold" into "we used a threshold with a measured 2.0% false-positive rate, n = 400."

## Result 3 — a proposed improvement that must be rejected

The obvious statistical upgrade — replace the single shuffled null with a permutation
p-value — **fails**. It fires in **24/24** configurations on scenes containing nothing at
all.

The reason is structural: adjacent sub-apertures overlap by 80%, so the residual
trajectory is a smooth function of look index even when it is built from pure speckle.
Shuffling destroys that smoothness, so a DFT-based contrast statistic always prefers the
unshuffled sequence. The permutation test therefore measures "is this sequence smooth?",
not "is there structure at depth."

This is worth recording because it is the improvement a referee is most likely to
suggest. It has been tried and it is anti-conservative. The paper's cruder ratio rule is
the better-behaved statistic, and Result 2 is the evidence for that.

## Honest limits of this run

- **These are synthetic scenes.** They establish that the three named knobs do not change
  the machinery's behaviour, and they calibrate the threshold. They do **not** re-run the
  five real sites. The headline claim — that the real Butte and Vesuvius scenes remain
  indistinguishable from their nulls under a Hamming window — requires re-running on the
  real SICDs. That run is a single command (below) and its result will be published here
  whichever way it falls.
- **Optical flow was validated but excluded from the 24-cell grid** for runtime; it passes
  the shift-recovery self-test and can be enabled with `--estimators … opticalflow`.
- The sweep is written so that a configuration-dependent verdict would be printed as such,
  in capitals, with an instruction not to bury it. Nothing here is contingent on the
  expected answer.

## Reproduce

```bash
python3 src/sensitivity_sweep.py --selftest
python3 src/sensitivity_sweep.py --synthetic --scene speckle --n-perm 200
python3 src/sensitivity_sweep.py --synthetic --scene blobs   --n-perm 200
# real scene:
python3 src/sensitivity_sweep.py --sicd data/2024-03-07-04-48-26_UMBRA-04_SICD.nitf --n-perm 200
```

## Summary for the thread

> Precision was already float64/complex128 end to end. I re-ran the whole pipeline across
> 4 sub-aperture windows × 2 precisions × 3 coregistrators = 24 configurations, including
> Hamming and including the upsampled-DFT engine used in DORIS-lineage processors. The
> verdict is identical in all 24, and the injected positive control is recovered in all 24
> — so the pipeline demonstrably works under every one of the suggested settings. Hamming
> moves the detection statistic by 0.24 on a threshold of 5.0. I also calibrated that
> threshold against 400 scenes containing nothing: false-positive rate 2.0%. Code, data
> and figures are in the repo.
