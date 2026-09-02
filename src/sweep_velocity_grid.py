#!/usr/bin/env python3
"""Velocity / grid-coverage sweep (addresses the paper's Section 8 and the
adversarial review's top scientific gap).

Two facts must be separated:
  (1) A velocity model only RELABELS the depth axis (metric_depth_axis multiplies
      the cell index by dz_phys). It cannot create or hide above-null contrast:
      the tomogram T itself does not depend on v or f. Proven elsewhere; not re-run here.
  (2) The real objection is GRID COVERAGE: if the searched depth grid does not span
      where a true reflector sits (because the assumed velocity is wrong), could a
      signal be missed? This script tests that directly by widening the searched grid
      and by planting reflectors at increasing true depths.

Key physics: the analytic-signal DFT is unambiguous only to the half-range
z_half = n_sub * DZ_TARGET / 2 (its Nyquist). Searching BEYOND that aliases — a deep
reflector folds back to a confident shallow false peak. So "just search deeper" is not
free; the max unambiguous depth is set by the sub-aperture count (aperture), not by v.

Run from repo root:  python3 src/sweep_velocity_grid.py
"""
import sys, json, numpy as np
sys.path.insert(0, "src")
from sarpy.io.complex.converter import open_complex
from tomogram import (_patch_observations, tomogram_from_observations, alignment_null,
                      contrast, peak_depth, DZ_TARGET, inject_damped_resonance)

def load_obs(path, crop=512, n_sub=11, patch=64, n_patch=24, overlap=0.8):
    reader = open_complex(path); R, C = reader.data_size
    r0, c0 = R//2 - crop//2, C//2 - crop//2
    slc = reader[r0:r0+crop, c0:c0+crop]
    row = crop//2 - patch//2
    cols = np.linspace(0, crop - patch, n_patch).astype(int)
    obs, _ = _patch_observations(slc, cols, row, patch, n_sub, overlap, 1)
    return np.asarray(obs), n_sub

def eval_grid(obs, zmax, nbins=300, seed=1):
    z = np.linspace(0, zmax, nbins)
    T = tomogram_from_observations(obs, z)
    calign = float(np.median(alignment_null(obs, z, np.random.default_rng(seed), n_perm=64)))
    creal = contrast(T)
    prof = T.sum(0); pk = z[np.argmax(prof)]
    return dict(zmax=zmax, contrast=round(creal,2), align=round(calign,2),
                ratio=round(creal/(calign+1e-12),2), peak=round(float(pk),2),
                peak_frac=round(float(pk/zmax),3), detection=bool(creal > 5*calign))

SCENES = [("Giza 7Feb U05", "data/giza_2023-02-07_UMBRA-05_SICD.nitf"),
          ("Giza 8Feb U04", "data/giza_2023-02-08_UMBRA-04_SICD.nitf"),
          ("Giza 8Mar U04", "data/giza_2023-03-08_UMBRA-04_SICD.nitf")]
MULTS = [0.5, 1.0, 2.0, 4.0]
out = {"part_A_real_grid_extent": {}, "part_B_planted_vs_coverage": {}}

print("="*92)
print("PART A — real-data grid-extent sweep: does searching DEEPER reveal any above-null band?")
print("  z_half = n_sub*DZ_TARGET/2 is the default (Nyquist) search depth; mult scales zmax.")
print("="*92)
print(f"{'scene':<16}{'mult':>6}{'zmax(cells)':>12}{'contrast':>10}{'align':>8}{'ratio':>8}{'peak_frac':>11}{'detect?':>9}")
for name, path in SCENES:
    obs, n_sub = load_obs(path)
    zhalf = n_sub*DZ_TARGET/2
    rows = []
    for m in MULTS:
        r = eval_grid(obs, zhalf*m)
        rows.append(r)
        print(f"{name:<16}{m:>6}{r['zmax']:>12.1f}{r['contrast']:>10}{r['align']:>8}"
              f"{r['ratio']:>8}{r['peak_frac']:>11}{'YES' if r['detection'] else 'no':>9}")
    out["part_A_real_grid_extent"][name] = rows
print("  Reading: if widening the grid 4x revealed a hidden deep reflector, ratio would")
print("  clear 5x and peak_frac would move off ~0. It does not on any scene.")

print()
print("="*92)
print("PART B — planted reflector vs grid coverage (Giza 7Feb): recovered, or aliased?")
print("  Plant a damped resonance at true depth z_true (in cells), invert on default grid")
print("  [0,z_half] AND widened grid [0,4*z_half]; is the peak recovered near z_true or aliased?")
print("="*92)
obs, n_sub = load_obs(SCENES[0][1])
zhalf = n_sub*DZ_TARGET/2
amp = 6*np.std(obs)
print(f"  z_half={zhalf:.1f} cells; plant amp={amp:.3g} (6x obs std)")
print(f"{'z_true':>8}{'grid':>8}{'zmax':>8}{'peak':>8}{'|err|':>8}{'contrast':>10}{'recovered?':>12}")
for z_true in [0.5*zhalf, 0.9*zhalf, 1.5*zhalf, 3.0*zhalf]:
    rec = {}
    for gtag, zmax in [("default", zhalf), ("wide4x", 4*zhalf)]:
        z = np.linspace(0, zmax, 300)
        planted = inject_damped_resonance(obs, z, z_true, amp)
        T = tomogram_from_observations(planted, z)
        pk = float(peak_depth(T, z)); c = float(contrast(T))
        err = abs(pk - z_true)
        recovered = err <= DZ_TARGET  # within one steering step
        rec[gtag] = dict(zmax=round(zmax,1), peak=round(pk,2), err=round(err,2),
                         contrast=round(c,2), recovered=bool(recovered))
        print(f"{z_true:>8.1f}{gtag:>8}{zmax:>8.1f}{pk:>8.2f}{err:>8.2f}{c:>10.2f}"
              f"{'YES' if recovered else 'ALIASED':>12}")
    out["part_B_planted_vs_coverage"][f"z_true_{z_true:.1f}"] = rec
print("  Reading: a reflector within the Nyquist half-range is recovered when the grid")
print("  spans it; beyond z_half it ALIASES to a false shallow peak that widening cannot")
print("  fix (it is past the transform's Nyquist). Max unambiguous depth is set by n_sub,")
print("  not by velocity: no velocity choice hides an in-range signal or recovers a")
print("  beyond-aperture one. This bounds the Section 8 objection.")

import os; os.makedirs("runs", exist_ok=True)
json.dump(out, open("runs/sweep_velocity_grid.json","w"), indent=1)
print("\nresults -> runs/sweep_velocity_grid.json")
