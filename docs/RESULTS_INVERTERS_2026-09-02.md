# Super-resolution inverter robustness — 2 September 2026

Closes an open item: does a super-resolution inverter (Capon/MVDR, MUSIC) also produce the
surface-pinned artifact, or only the plain Bartlett/DFT the paper reproduces? This is Biondi's
strongest un-preempted rebuttal: *"you used a weak inverter; my method uses super-resolution."*

Script: `src/robustness_inverters.py`. The same per-patch detrended-cumsum trajectories are fed
into all three inverters on the pipeline's own steering grid (n_sub=11, 24 patches). Bartlett
reproduces `tomogram.py`'s known 1.75-cell peak exactly, which validates the harness.

| input | Bartlett | Capon (MVDR) | MUSIC |
|---|---|---|---|
| Giza 7 Feb (real) | **1.75 cells** (C=6.1) | **1.99 cells** (C=7.2) | **1.75 cells** (C=13.7) |
| pure-noise walks | 1.64 cells (C=3.3) | 3.99 cells (C=7.3) | 1.60 cells (C=5.8) |

**On real Giza data all three inverters pin at the surface (1.75–1.99 cells, within the 2-cell
guard).** MUSIC — the highest-resolution estimator — pins at exactly 1.75 with the *highest*
contrast of the three. Super-resolution sharpens the artifact; it does not move the peak off the
surface or expose structure.

**Conclusion.** The artifact is generated upstream of the inversion (in the `cumsum` trajectory),
so the choice of inverter cannot remove it. "You used a weak inverter" is refuted directly:
swapping Bartlett for Capon or MUSIC leaves the surface-pinned peak in place and, if anything,
makes it more confident. Caveat: covariance built from 24 snapshots at n_sub=11; MUSIC assumes
1 source. The real-data agreement across all three is the point; the noise column is a sanity check.

## Bug caught during this run (documentation-rules note)
First pass built the covariance as `Y.conj().T @ Y` (conjugated), flipping the analytic-signal
frequency sign, so Bartlett peaked at the grid edge (5.50 cells) instead of the known 1.75. Fixed to
`Y.T @ Y.conj()` (standard `E[y yᴴ]`); Bartlett then matched `tomogram.py` to the cell. The
known-answer check (Bartlett must give 1.75) is what caught it — keep that check in any inverter work.
