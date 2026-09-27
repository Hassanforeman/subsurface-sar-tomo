# Q2 — the paper's depth steering on our Umbra geometry is a DFT to 5 decimal places — 27 Sep 2026

**Script:** `src/kz_ladder_umbra.py` → `runs/kz_ladder_umbra.json`. Descriptive geometry from each SICD's own
orbit polynomial (no pixels read, no hypothesis, nothing tuned — hence no pre-registration).
Question from COMPARISON_EJHONG §6 Q2 and the Grok triage (B1): if the paper's `Kz = 4π B⊥ / (λs r sinθ)` is
evaluated with real orbit geometry for our 11-look bank, is the ladder uniform (i.e. a DFT), and what sets
the depth scale?

| Scene | processed aperture | B⊥ span | CV of ΔKz | depth repeat per metre of λs |
|---|---|---|---|---|
| 02-07 U05 | 1.27 s | 6,510 m | 3.8 × 10⁻⁶ | 292 m |
| 02-08 U04 | 1.18 s | 6,059 m | 2.2 × 10⁻⁶ | 240 m |
| 03-08 U04 | 5.04 s | 25,784 m | 2.3 × 10⁻⁵ | 71 m |

**Findings.**
1. The steering wavenumbers are evenly spaced to within 2 × 10⁻⁵ (relative). Orbit curvature over a
   few-second aperture is negligible, so the paper's steering matrix *is* a DFT on this data to five
   decimal places. That closes Grok's B1 caveat ("could real orbit curvature make it not a DFT?") for
   Umbra spotlight: no. (Wording kept careful: "as implemented, depth is a Fourier bin".)
2. The depth axis repeats every (λs · r · sinθ) / (2 ΔB⊥). λs, the "sound wavelength", is not measured.
   With λs = 0.48 m the repeat is 140 / 115 / 34 m; with λs = 3.8 m it is 1,110 / 912 / 270 m. Same
   pixels, any depth — the same relabel we derived for the patent's 22 kHz, now on the paper's formula.
3. With one fixed λs the three scenes put the axis on **different** scales (292 vs 240 vs 71 m per metre
   of λs), because the depth scale follows the look geometry and aperture, not the ground. Consistent
   "depths" across scenes would require a different λs per scene.
4. 03-08's processed aperture is 5 s; our bank spans ~3.4 s of it, well past the ~1 s coherence half-life
   ejhong measured on ICEYE dwells. To be measured on Umbra directly (Q3, run with test G).

Agrees with ejhong R2/R8/R15 (27.4 m, corr 1.000 on ICEYE) by a separate computation on separate data.
