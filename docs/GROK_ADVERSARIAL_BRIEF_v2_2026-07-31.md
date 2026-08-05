# Adversarial review request v2 — mechanism identified and tested

**Supersedes:** `GROK_ADVERSARIAL_BRIEF_2026-07-31.md`
**Repository:** `github.com/Hassanforeman/subsurface-sar-tomo` @ `741b0e9`
**Preprint under evaluation:** PCI Archaeology #1130, `10.5281/zenodo.21668674`

---

## 0. What changed since your last review, and what I want now

You reviewed a claim resting on an AR(1) null whose coefficient was **fitted** to the data it was
meant to test. You called that the strongest vulnerability, said the principled overlap-synthesis
null was the missing experiment, and told me not to lock the §5 language until it was run.

It has been run, and it produced a **different mechanism from the one I proposed**. Two of my three
mechanism claims are now withdrawn. The third has a matched-control experiment behind it.

**What I want from you this time:**

1. Is the E8 control genuinely matched, or is there a confound I have not seen? This is the load
   bearing experiment now.
2. At `n_sub` = 128, pure noise gives contrast **274.85** and real data **128.64** — noise beats
   data 2:1. Is that a legitimate result or a sign the synthetic input is not comparable?
3. Does the unification in §4 hold — is the `n_sub` sensitivity really the same phenomenon as the
   artifact, or am I collapsing two things that only correlate?
4. The mechanism story has now changed **three** times. At what point does that pattern itself
   become evidence that I am fitting explanations to data?
5. Arithmetic and inference, again. All of it.

---

## 1. The pipeline, and the one line that matters

Reproduced from Biondi & Malanga (Remote Sensing 14(20):5231, 2022) and patent WO2024008365A1:

1. one single-look-complex SAR image;
2. split its Doppler bandwidth into `n_sub` sub-apertures ("looks"), default overlap 0.8;
3. per patch, estimate displacement between **adjacent** looks by phase correlation;
4. **accumulate those increments into a trajectory**;
5. degree-2 detrend each trajectory;
6. invert against a steering matrix (the patent calls it a DFT) to get a depth profile;
7. label bins in metres via `dz_phys = (v/f)·R/(2A)`.

Step 4, in `src/sensitivity_sweep.py`:

```python
def adjacent_trajectory_e(looks, estimator="phasecorr", dtype=np.complex128):
    N = len(looks); inc = np.zeros(N, dtype=rdt)
    for k in range(1, N):
        dy, dx = fn(np.abs(looks[k-1]), np.abs(looks[k]), rdt)
        inc[k] = dx
        ...
    return np.cumsum(inc), coh          # <-- running total
```

The trajectory is a **cumulative sum of noisy increments** — a random walk, smooth by construction,
strongly autocorrelated regardless of scene or overlap.

---

## 2. Withdrawn claims

| # | Claim | Status | Killed by |
|---|---|---|---|
| M1 | "The inverter produces the peak from nothing; real data is indistinguishable from noise" | **withdrawn** | E6 v1: white noise peaked at 3.11 cells, 7% in band |
| M2 | "80% sub-aperture overlap manufactures the peak" | **withdrawn** | E7: at overlap **0.00** the peak is still at 1.73 cells and lag-1 is still 0.447 |

M1 was asserted before any null existed. M2 survived one experiment and died on the next.

Also fixed: the E7 verdict printer was hard-coded to announce M2 and did not examine the
zero-overlap row. It printed the right conclusion for the wrong reason. Now corrected.

---

## 3. E8 — the current mechanism claim, with a matched control

**Design.** `inc` and `cumsum(inc)` have **identical length** (`inc[0] = 0`), so the steering matrix
is unchanged and the *only* difference between arms is the running total. `inc` is recovered exactly
as `concatenate([[0], diff(traj)])` — verified exact.

**Bingham, `n_sub` = 11, overlap 0.8, 40 noise trials:**

| input | series | raw lag-1 | peak (cells) | contrast | pinned |
|---|---|---|---|---|---|
| real | cumsum (as published) | +0.431 | 1.66 | 3.87 | PIN |
| real | increments | −0.113 | 2.83 | 1.36 | clear |
| white noise (median) | cumsum | +0.505 | 1.71 | 3.60 | 100% |
| white noise (median) | increments | −0.055 | 2.94 | 1.41 | 18% |

**Capella, `n_sub` = 11** (different operator, constellation, ground processor):

| input | series | raw lag-1 | peak | contrast | pinned |
|---|---|---|---|---|---|
| real | cumsum | +0.488 | 1.69 | **2.75** | PIN |
| real | increments | −0.129 | 4.76 | 1.31 | clear |
| white noise | cumsum | +0.505 | 1.71 | **3.60** | 100% |
| white noise | increments | −0.055 | 2.94 | 1.41 | 18% |

Note Capella's real contrast (2.75) is **24% below** the pure-noise value (3.60).

---

## 4. The unification — `n_sub` sensitivity IS the random walk

Bingham, E8 at three sub-aperture counts:

| `n_sub` | lag-1 real / noise | real contrast | **noise contrast** | real / noise |
|---|---|---|---|---|
| 11 | 0.43 / 0.51 | 3.87 | 3.60 | 1.07 |
| 32 | 0.82 / 0.81 | 26.42 | 21.04 | 1.26 |
| **128** | **0.88 / 0.95** | **128.64** | **274.85** | **0.47** |

At `n_sub` = 128, removing the cumulative sum moves the real peak from 1.50 → **52.66 cells** and
contrast 128.64 → 2.49; noise 1.71 → 13.70 and 274.85 → 1.72; pinning 100% → **0%**.

**The proposed unification.** Autocorrelation rises with `n_sub` (0.43 → 0.82 → 0.88 real;
0.51 → 0.81 → 0.95 noise) because a longer random walk is smoother. Smoother walk → higher contrast.
So the `n_sub` sensitivity previously reported as a separate finding — 3.87 → 128.64 on Bingham,
2.75 → 272.52 on Cairo — **is** the cumulative sum, not an independent quirk.

**Is this collapse legitimate, or am I asserting causation from a co-varying quantity?**

---

## 5. The three numbers I would build the paper on

1. **`n_sub` = 128: noise 274.85 vs real 128.64.** Data containing nothing produces >2× the apparent
   structure of a real scene.
2. **Cairo real at `n_sub` = 128 was 272.52; noise gives 274.85** — agreement to within 1%. The most
   dramatic figure in the five-site grid is reproduced to the percent by an image with no scene.
3. **Real/noise across `n_sub` = 1.07, 1.26, 0.47** — scattered around unity, no systematic excess
   in either direction.

---

## 6. Unchanged from v1 and, I believe, still solid

- Peak confined to **1.2–1.9 resolution cells** across 5 sites, 2 sensors, 8 `n_sub` values,
  13 patch geometries, 2 sets of physical constants.
- **Depth ∝ 1/f exactly**, by construction — `f` never enters the inverter, only the final axis
  rescaling. You confirmed this reasoning; nothing has changed in the code path.
- The 5%-of-axis surface-pinning rule flags 14/40 runs; an absolute 2-cell rule flags 40/40.
- Three published values reproduce to two decimals (Butte 3.33 vs 3.3; Vesuvius 4.11 vs 4.1;
  Cairo 2.75 vs 2.8), so the reimplementation is faithful.

---

## 7. Known weaknesses — attack these

1. **The synthetic SLC is white.** Real speckle carries resolution-cell correlation from the system
   PSF. This is the one remaining identified way the null could differ systematically from the data.
   You raised it; it is still not closed. **How much does it threaten §3–§5?** Does the E8 *contrast*
   (cumsum vs increments, same input either way) insulate the conclusion from this, since both arms
   share whatever spectral character the input has?
2. **Removing the cumsum is a diagnostic, not a proposed correction.** Accumulating relative
   displacements into an absolute trajectory is a reasonable operation. I am *not* claiming the
   method "should" use increments. Is my framing in §8 below sufficiently careful?
3. **Three mechanism revisions in ~36 hours.** M1 asserted pre-test; M2 died on the next experiment;
   M3 has a matched control. Is that a healthy sequence or a warning sign?
4. **Noise trial counts are modest** — 40 at `n_sub` 11/32, 20 at 128.
5. **All X-band spotlight.** Nothing here bears on C-band or L-band.
6. **`contrast` itself** is a shape statistic whose behaviour under strongly autocorrelated inputs I
   have not characterised analytically. Could the entire effect be a known property of that
   statistic rather than of the tomography?

---

## 8. The claim I intend to make, for you to attack as worded

> The per-patch trajectory in this method is a running total of adjacent-look displacement
> estimates. A running total of noisy increments is a random walk, which is smooth by construction
> and strongly autocorrelated irrespective of scene content or sub-aperture overlap. The inversion
> reads that smoothness as coherent subsurface structure and places a peak approximately 1.7
> resolution cells beneath the surface — on every site tested, on both sensors, and on synthetic
> images containing no scene at all. Increasing the sub-aperture count lengthens the walk, raising
> its autocorrelation and inflating the reported contrast; at the largest count tested, an image
> containing nothing yields a contrast more than twice that of a real scene. No control in the
> published method accounts for this, and the reported depth is in any case exactly proportional to
> an investigation frequency chosen by the analyst rather than measured.

I am **not** claiming the technique cannot work in principle, that increments are the correct
operation, or that nothing lies beneath any of these sites.

**Which sentence in that paragraph is the weakest, and would you sign your name under it?**
