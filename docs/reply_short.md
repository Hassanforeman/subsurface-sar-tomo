# Shortened reply — for the YouTube thread

*About half the length of `reply_final.md`. Keeps the measured result, the self-corrections, the
request and the two questions; moves site-by-site detail to the repo link.*

---

Dr Biondi — thank you for the concrete suggestions. I ran them rather than argued about them, and
one of them turned out to matter.

Precision was already float64 end to end; across 96 configurations on four real sites, float32 and
float64 agree to three significant figures. No coregistrator flips a verdict, including the
upsampled-DFT engine used in DORIS-lineage processors. The positive control recovers in 96 of 96
runs, so the pipeline finds a signal when one is present.

**The window matters, and I can now say why.** At Butte the detection statistic runs 1.98
(Blackman) → 3.33 (Hann) → 5.95 (Hamming) → 8.30 (no taper). So I measured the lag-1
autocorrelation of the detrended residual trajectories that enter the inverter: it runs −0.103 →
−0.010 → +0.095 → +0.244 across the same windows and tracks the statistic at **r = +0.99**. It
changes sign. A bandwidth/SNR account predicts weaker residuals under stronger tapers but predicts
nothing about inter-look correlation crossing zero — that is a leakage signature. The only
configuration that crosses the detection threshold is the leakiest one. Your Hamming
recommendation stays below it at all four sites.

**Running your suggestions also found three errors of my own.** One row of my results table had
been run at a different sub-aperture count from the others, with the wrong verdict label. My
surface-pinning guard used a cutoff of 5% *of the depth axis*, which changes meaning when the axis
length changes. And my null test shuffled look order, which destroys the smoothness that 80%
sub-aperture overlap guarantees even under pure noise. All three are fixed and documented; the
conclusions are unchanged and now rest on better instruments.

**The ask.** The coregistrator, the window, the precision and the sub-aperture count are given no
values in either 2022 paper or in WO2024008365A1, which names N_D as "the sampling-rate of the
mechanical wave" without saying what to set it to. The window demonstrably changes the outcome. If
these choices are decisive, publishing the values used for Giza and Vesuvius would settle this
faster than any further argument, and I will re-run the identical pipeline the day they appear.

Two questions no configuration can resolve, because they are mathematical. As written in the
patent, is the depth-focusing steering matrix a DFT? And on what physical axis is the ~22 kHz
investigation frequency defined — what is that axis's Nyquist limit given the sub-aperture sampling?

This is a critique of the published method, not of you. The surface-vibration measurement front-end
is legitimate; it is the deep inference that fails the controls. Full results, code and figures:
github.com/Hassanforeman/subsurface-sar-tomo

One small thing so I can cite you correctly — would you confirm this exchange from an account
publicly linked to your published work?
