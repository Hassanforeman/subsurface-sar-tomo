# Final reply to @filippobiondi2576 — post-experiment version

*Every claim is backed by `docs/SENSITIVITY_RESPONSE_BIONDI.md` after adversarial review and the
29 July follow-up experiments. Withdrawn claims (194×, "1 in 48", "flips the verdict four times")
are absent by design.*

---

Dr Biondi — thank you for the concrete suggestions. I ran them rather than argued about them, and
one of them turned out to matter.

**Precision.** Already float64/complex128 end to end. Across 96 configurations — four real sites
(Butte, Vesuvius, Bingham, Komati) × four sub-aperture windows × two precisions × three
coregistrators — float32 and float64 agree to three significant figures. It cannot be the difference.

**Coregistrator.** No estimator flips a verdict at any site, including the upsampled-DFT engine used
inside DORIS-lineage processors.

**The window — you were right that it matters, and I can now say why.** At Butte the detection
statistic runs 1.98 (Blackman) → 3.33 (Hann) → 5.95 (Hamming) → 8.30 (no taper). So I measured the
lag-1 autocorrelation of the detrended residual trajectories that actually enter the inverter. It
runs −0.103 → −0.010 → +0.095 → +0.244 across the same windows, and it tracks the detection
statistic at **r = +0.994**. The statistic rises with inter-look correlation and the correlation
changes sign. A bandwidth/SNR explanation predicts weaker residuals under stronger tapers but
predicts nothing about inter-look autocorrelation crossing zero — that is specifically a leakage
signature. The only configuration that crossed the threshold is the leakiest one, and the apparent
depth signal is looks bleeding into each other rather than angular diversity.

Your Hamming recommendation stays below the threshold at all four sites. The positive control
recovers in 96 of 96 runs, so the pipeline finds a signal when one is present.

**Three errors of my own, found by running your suggestions.** One row of my results table had been
run at a different sub-aperture count from the others and its verdict label was wrong. My
surface-pinning guard used a cutoff of 5% *of the depth axis*, which changes meaning when the axis
length changes — the same 3 m feature was flagged at one sub-aperture count and cleared at another.
And my null test shuffled look order, which destroys the smoothness that 80% sub-aperture overlap
guarantees even under pure noise, making it anti-conservative.

All three are fixed. The guard now triggers on absolute depth in resolution cells. The null now
preserves each patch's depth profile exactly and randomises only whether patches agree on a depth —
which is the actual question. With both repairs, Komati returns no detection at any sub-aperture
count from 11 to 128, peaking at 3.2–3.7 m every time: one consistent shallow surface feature, which
is the right answer for a power station. The conclusion is unchanged and now rests on better
instruments.

**The ask.** The coregistrator, the window, the precision and the sub-aperture count are given no
values in either 2022 paper or in WO2024008365A1, which names N_D as "the sampling-rate of the
mechanical wave" without saying what to set it to. The window demonstrably changes the outcome. If
these choices are decisive, publishing the values used for the Giza and Vesuvius results would
settle the empirical question faster than any further argument. I will re-run the identical pipeline
the day they appear.

**Two questions no configuration can resolve, because they are mathematical.** As written in the
patent, is the depth-focusing steering matrix a DFT? And on what physical axis is the ~22 kHz
investigation frequency defined, given the sub-aperture sampling — what is that axis's Nyquist limit?

This remains a critique of the published method, not of you. The surface-vibration measurement
front-end is legitimate; it is the deep inference that fails the controls. Code, scene IDs and
figures are open.

One small thing so I can cite you correctly: would you confirm this exchange from an account
publicly linked to your published work?
