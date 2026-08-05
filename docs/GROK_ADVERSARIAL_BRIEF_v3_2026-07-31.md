# Adversarial review request v3 — both open items closed, and the depth is now derived

**Supersedes:** `GROK_ADVERSARIAL_BRIEF_v2_2026-07-31.md`
**Repository:** `github.com/Hassanforeman/subsurface-sar-tomo` @ `736d986`
**Preprint under evaluation:** PCI Archaeology #1130, `10.5281/zenodo.21668674`

---

## 0. What you asked for, and what came back

Your v2 review left three items:

| Your item | Status |
|---|---|
| **PSF-matched null** — white synthetic speckle is not representative | **run — §2** |
| **Analytic account of `contrast` under random-walk inputs** — empirical only | **partially closed — §3 proves the DFT identity and measures the peak law; one constant is undetermined and the contrast magnitude remains empirical** |
| Acknowledge the revision history in the manuscript | accepted, drafted |

You also flagged **sentence 5** of my claim paragraph — the causal unification of `n_sub`
sensitivity with walk length — as the one thing you would not sign. §4 addresses it.

**What I want now: check §3.** It separates a proved identity (the inversion is a DFT, so the
reported depth in cells equals the dominant surviving mode) from a measured law (that mode is fixed
by the detrend degree) from an undetermined constant (0.856, not derived). Tell me if I have drawn
those lines in the wrong places. I would also like you to check whether I have over-read §2.

**Note on an earlier draft.** A previous version of this brief described §3 as "arithmetically
determined" and asserted the peak sits at "the lowest spectral mode surviving the degree-2 detrend."
Your v2 review flagged that phrasing as one algebraic step short. It was, and working the algebra
showed the textbook (d+1)/2 rule is 14% low at the operating degree. The wording throughout has been
corrected accordingly.

---

## 1. Recap of the established position (unchanged from v2)

- Peak confined to **1.2–1.9 resolution cells** across 5 sites, 2 sensors, 8 sub-aperture counts,
  13 patch geometries, 2 sets of physical constants.
- **Depth ∝ 1/f exactly**, by construction; `f` never enters the inverter.
- The trajectory is `np.cumsum(inc)` — a random walk. Matched-control experiment (identical length,
  identical steering matrix, only the running total differing) moves the peak off the surface and
  collapses contrast 3.87 → 1.36.
- Accumulated Gaussian noise with **no SAR pipeline at all** reproduces both the fixed peak
  (1.66–1.71 cells at every length) and the contrast scaling (**72.9×**), while the increments of
  the same series stay flat (1.1×).
- At `n_sub` = 128, noise gives contrast **274.85** against real data's **128.64**.

---

## 2. E10 — the PSF-matched null

**Construction.** Rather than a white image, complex white noise is placed in a **centred sub-block
of the spectrum** and inverse transformed. That is what SAR speckle is: flat inside the occupied
band, zero outside, with the band-limiting producing resolution-cell correlation. `bw_frac` = 1.0
recovers the white image.

**The real scene's occupied bandwidth is measured, not assumed:** azimuth **0.750**, range 0.744
(95% energy). Bingham, `n_sub` = 11, 25 trials per row.

| `bw_frac` | raw lag-1 | peak (cells) | contrast | pinned |
|---|---|---|---|---|
| 1.00 (white, = E7) | 0.501 | 1.69 | 3.81 | 100% |
| **0.80 — nearest the real 0.750** | 0.514 | **1.73** | **4.14** | 100% |
| 0.60 | 0.553 | 1.75 | 4.68 | 100% |
| 0.40 | 0.536 | 1.73 | 4.97 | 100% |
| 0.25 | −0.010 | 1.49 | 2.57 | 100% |
| 0.15 | 0.477 | 1.60 | 2.52 | 100% |
| **REAL** | 0.431 | **1.66** | **3.87** | — |

**With correctly correlated speckle the peak still matches (1.73 vs 1.66) and the synthetic produces
7% MORE contrast than the real scene** (4.14 vs 3.87; real/synthetic = 0.93). The white null was not
flattering the conclusion — it was mildly conservative.

**Disclosed weakness:** the 0.25 and 0.15 rows break the monotone trend (lag-1 drops to −0.01 at
0.25). Those bandwidths are far below any real SAR system and do not bear on the comparison at 0.75,
but I have not investigated the cause. **Does this non-monotonicity trouble you?**

---

## 3. E11 — the peak depth is fixed by the detrend degree

Pure random walks. No SAR pipeline. 60 trials, 8 lengths (11 → 128), 5 detrend degrees, 300-bin axis.

| detrend degree | peak (cells), range over all 8 lengths | mean `bin × length` | sd |
|---|---|---|---|
| 0 | 0.86 – 0.90 | 525 | 11 |
| 1 | 1.05 – 1.14 | 659 | 18 |
| **2 — the pipeline's setting** | **1.66 – 1.71** | **1008** | **14** |
| 3 | 1.96 – 2.05 | 1204 | 17 |
| 4 | 2.41 – 2.59 | 1495 | 34 |

**Two exact regularities:**

1. **Peak depth in cells is fixed by the detrend degree alone** — constant to ±0.05 cells across a
   **12× range** of series lengths.
2. **`bin × length` is constant** for a given degree. On a 300-bin axis spanning `L·DZ/2`,
   `peak_cells = bin × L / 598`. Therefore 1008 / 598 = **1.685 cells** at degree 2.

**1.685 cells is the value returned by every real site, both sensors, all sub-aperture counts, all
thirteen geometries and every noise run** (observed 1.2–1.9, central ~1.7).

### 3.1 What is PROVED, from the code

`steering()` builds `Kz[j] = j · 2π/(n_looks · DZ_TARGET)`; `invert_patch()` computes
`|Aᴴ · analytic1d(r)|²`. That is a DFT evaluated at `ω = 2π·z/(L·DZ_TARGET)`, so it peaks when
`z = k·DZ_TARGET` for the dominant mode `k`. Therefore:

> **peak_cells = k**, the dominant surviving spectral mode index. Exactly.

This alone accounts for the `bin × L` invariance: a fixed mode occupies a fixed fraction of an axis
whose extent is proportional to `L`. No further assumption needed.

### 3.2 What is MEASURED, not derived

Direct simulation of the inversion (400 trials, lengths 11/32/128):

| detrend degree | peak_cells | `bin × L` | textbook (d+1)/2 rule |
|---|---|---|---|
| 0 | 0.856 – 0.883 | 512 – 528 | 0.50 |
| 2 | **1.711 – 1.712** | **1023 – 1024** | 1.50 |
| 4 | 2.515 – 2.594 | 1504 – 1551 | 2.50 |

The standard rule that a degree-*d* polynomial detrend high-passes at ≈(d+1)/2 cycles per record
predicts **1.5** cells at degree 2 against **1.712** observed — **14% low at the pipeline's operating
degree**, converging by degree 4. The even degrees fit `k ≈ 0.856 × (d/2 + 1)`.

**The constant 0.856 has not been derived.** Doing so requires the joint effect of least-squares
polynomial removal and the `analytic1d` Hilbert step on a 1/f² spectrum over a finite record. That
is the outstanding algebraic step, and I am not claiming it is closed.

### 3.3 Please check

- Is the DFT identity in §3.1 right, or have I misread `steering()` / `invert_patch()`?
- Does the (d+1)/2 high-pass rule's 14% shortfall at degree 2 indicate a missing term, or is it
  simply the known inaccuracy of that rule of thumb at low order on short records?
- Is there a cleaner route to 0.856 than brute-force spectral algebra?

### 3.4 Consequence

The characteristic depth follows from two implementation choices — the cumulative sum and the
degree-2 detrend — and from the DFT nature of the inversion. Setting the detrend to degree 4 moves
the reported "structure" to 2.5 cells; degree 0 moves it to 0.88.

### 3.5 A correction I am carrying

The verdict text E11 prints says the peak **bin** is "largely independent of series length." **That
is false** — bins run 4 to 48 at degree 0. The invariant is the depth in cells, not the bin index.
The code's message is wrong; the table is right. Recorded in `RESULTS_2026-07-31_FIVE_SITE.md`
§15.2.

---

## 4. Sentence 5, revisited

You declined to sign: *"Increasing the sub-aperture count lengthens the walk, raising its
autocorrelation and inflating the reported contrast."*

E9 removed every co-varying factor — no image, no sub-apertures, no overlap, no window, no
coregistration — leaving length as the sole variable. Contrast rose **72.9×** for accumulated
series and **1.1×** for their own increments, and lag-1 rose 0.47 → 0.94.

**Does that close it, or is there still an inferential gap?**

---

## 5. The claim paragraph, as I would now publish it

> The per-patch trajectory in this method is a running total of adjacent-look displacement
> estimates. A running total of noisy increments is a random walk: smooth by construction,
> strongly autocorrelated, with a 1/f² spectrum, irrespective of scene content or sub-aperture
> overlap. The inversion is a discrete Fourier transform, so the reported depth in resolution cells
> equals the dominant surviving spectral mode of the trajectory; because the pipeline removes a
> degree-2 polynomial from a 1/f² series, that mode is fixed by the detrend order alone at 1.71
> cells — invariant across a twelvefold range of trajectory lengths, and the value observed at every
> site tested, on both sensors, and on synthetic series containing no scene at all. Increasing the
> sub-aperture count lengthens the walk and
> inflates the reported contrast; at the largest count tested, an image containing nothing yields a
> contrast more than twice that of a real scene. Substituting speckle with the correct
> resolution-cell correlation does not change this. No control in the published method
> distinguishes such a case from a genuine detection, and the metre-scale depth is in any event
> exactly proportional to an investigation frequency chosen by the analyst rather than measured.

**Which sentence is now the weakest? Would you sign this version?**

---

## 6. What I still do not claim

- That the published imagery is nothing but this artifact. Those figures involve multi-scene
  stacking, denoising and display choices that have not been reproduced and whose inputs are not
  public.
- That accumulating displacements is the *wrong* operation. The increments arm is a diagnostic, not
  a proposed correction.
- That nothing lies beneath any of these sites.

---

## 7. Full disclosure of the revision history

Mechanism accounts proposed and withdrawn, in order: (M1) the inverter produces the peak from
nothing — withdrawn after E6 v1; (M2) 80% sub-aperture overlap manufactures it — withdrawn after E7
showed the effect at *zero* overlap; (M3) the cumulative sum — current, supported by a matched
control (E8), a minimal reproduction (E9), a PSF-matched null (E10) and an exact arithmetic law
(E11).

Two of my experiment verdict-printers have also stated conclusions the data did not support (E7's
overlap message, E11's bin message). Both corrected in the repository; both flagged here.

**Given that history: is the current account stable enough to publish, and does the arithmetic in
§3 change your answer?**
