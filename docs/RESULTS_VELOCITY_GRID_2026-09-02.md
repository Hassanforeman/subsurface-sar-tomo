# Velocity / grid-coverage sweep — 2 September 2026

Closes the adversarial review's top scientific gap and the paper's own §8 promise
("sweep the assumed velocity ±20-50% with the grid widened accordingly").
Script: `src/sweep_velocity_grid.py`; stability check inline. Run on all three Giza scenes.

## 1. The two questions, separated

- **Relabelling** (velocity/frequency changes, grid fixed at its Nyquist half-range):
  the tomogram T does not depend on v or f — they enter only in the axis label
  (`metric_depth_axis`). So no velocity choice can create or hide above-null contrast.
  Established previously (Figure 2); not re-run.
- **Grid coverage** (searching a wider depth range, which is what assuming a slow
  velocity would motivate): this is the real objection and is tested here directly.

## 2. Part A — searching deeper does NOT reveal a hidden reflector; it manufactures an alias

Real-data contrast vs alignment null at grid extents 0.5× / 1× / 2× / 4× the Nyquist
half-range z_half = n_sub·DZ_TARGET/2 (default n_sub=11):

| scene | 0.5× | 1× (default) | 2× | 4× |
|---|---|---|---|---|
| Giza 7 Feb | 1.7 (no) | 3.73 (no) | 23.6 (YES) | 22.7 (YES) |
| Giza 8 Feb | 2.05 (no) | 2.29 (no) | 18.1 (YES) | 16.9 (YES) |
| Giza 8 Mar | 1.84 (no) | 2.55 (no) | 29.3 (YES) | 28.7 (YES) |

At and below the correct grid, every scene is a null (<5×). Over-extending the grid to
2-4× makes the ratio jump to 17-29× and read as a "detection." **This is not a hidden
signal surfacing — it is aliasing**, the same axis-length contrast-inflation the paper
already withdrew for n_sub (the 1720× issue, §10.1), now via grid extent. Two proofs:

**Part B — the wide grid aliases even KNOWN planted reflectors.** Planting a damped
resonance at true depth z_true (Giza 7 Feb, z_half=27.5 cells):

| z_true (cells) | default grid recovers? | wide-4× grid |
|---|---|---|
| 13.8 (in range) | YES (peak 14.07, err 0.32) | ALIASED (peak 69.2) |
| 24.8 (in range) | YES (peak 25.29, err 0.54) | ALIASED (peak 80.2) |
| 41.2 (beyond z_half) | ALIASED to shallow | ALIASED |
| 82.5 (beyond z_half) | ALIASED | ALIASED |

A reflector inside the Nyquist half-range is cleanly recovered on a grid that spans it;
beyond z_half it aliases, and the wide grid corrupts even in-range reflectors. So the
peaks that appear at 2-4× are artifacts, not structure.

## 3. The guard that catches it: n_sub-stability (near-surface guard does NOT)

Peak depth (cells) vs sub-aperture count, Giza 7 Feb:

| grid | peak-depth spread across n_sub (11→128) |
|---|---|
| default (Nyquist-matched) | **0.25 cells** (all 1.50–1.75) — stable |
| wide 4× | **89.79 cells** (1.7 → 23.7 → 33.6 → 46.7 → 65.5 → 91.5 → 1.7) — jumps |

A real in-range reflector holds its depth across n_sub; the over-extended-grid alias
moves with n_sub. Note the aliased wide-grid peak sits at ~9-90 cells, i.e. NOT within
the 2-cell near-surface guard — so the near-surface guard and the alignment-null ratio
do NOT catch it. **Only the sub-aperture-count stability guard does.**

## 4. Consequence for §8 (report this precisely)

The paper's current §8 sentence — "no velocity produces above-null contrast, so the null
is robust" — is too strong as written. The correct, stronger statement:

1. Axis relabelling (any v, correct grid) cannot change the verdict — T is invariant.
2. The ONLY way to get above-null contrast on these scenes is to over-extend the depth
   grid past its Nyquist half-range, and that produces an ALIAS, not a detection: it
   corrupts known in-range reflectors identically and is not depth-stable across n_sub.
3. So a wrong (slow) velocity assumption does not hide a real signal — at worst it
   manufactures a false positive, which the n_sub-stability guard flags.
4. §8 should therefore (a) add the n_sub-stability guard to the velocity discussion, and
   (b) state that the alignment-null ratio and the near-surface guard are NOT robust to
   grid over-extension — only stability is. This matches Technical Bible §5's off-grid-alias
   finding and extends it to real Giza data.

This bounds the objection and adds a fourth independent artifact-generation knob (grid
extent) alongside sub-aperture count, window taper and accumulation.
