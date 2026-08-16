#!/usr/bin/env python3
"""
overlay_test.py — how much "structural correlation" can noise achieve against a
target, if you are allowed to align it to that target?

WHY THIS EXISTS
---------------
A public claim reports a "blind test" overlaying a tomographic product on optical
imagery of a shipwreck, achieving "structural correlation: 91.4%". The figure is
captioned "In-Situ Photo Overlay Test with Tiled Alignment".

The question this answers is not whether the physics permits the measurement. It
is narrower and more useful: **if you take a field containing no information about
the target, and you are permitted to align it to the target, what score do you get?**

If noise plus a fitted alignment reaches ~90%, then the statistic does not
distinguish a real detection from no detection, and no fabrication needs to be
alleged to explain the picture.

Three arms, all scored the same way:
  1. noise, no alignment        - the honest baseline
  2. noise + rigid alignment    - translation, rotation, scale fitted to the target
  3. noise + TILED alignment    - the field split into tiles, each shifted
                                  independently to fit. This is the caption's own words.

Control: the same noise fitted to a DIFFERENT target. If tiled alignment scores
just as well against the wrong answer, the score measures the alignment procedure
and not the data.
"""
import json
import numpy as np
from scipy.ndimage import gaussian_filter, rotate, zoom

RNG = np.random.default_rng(0)
N = 240


def hull_mask(n=N, split=True):
    """An elongated hull-like shape. Titanic lies in two pieces, so optionally split."""
    y, x = np.mgrid[0:n, 0:n]
    cx, cy = n / 2, n / 2
    m = (((x - cx) / (0.38 * n)) ** 2 + ((y - cy) / (0.10 * n)) ** 2) < 1.0
    if split:
        m[:, int(0.50 * n):int(0.56 * n)] = False
    return m


def other_target(n=N):
    """A deliberately WRONG target: same area, different geometry (an L/bend)."""
    m = np.zeros((n, n), bool)
    m[int(.44*n):int(.56*n), int(.16*n):int(.62*n)] = True
    m[int(.30*n):int(.56*n), int(.55*n):int(.66*n)] = True
    return m


def noise_field(n=N, smooth=4.0):
    """Band-limited noise. Contains no information about any target."""
    return gaussian_filter(RNG.normal(0, 1, (n, n)), smooth)


def to_mask(field, area):
    """Threshold a field so it occupies the same area fraction as the target."""
    k = int(round(area * field.size))
    thr = np.partition(field.ravel(), -k)[-k]
    return field >= thr


def dice(a, b):
    return 2.0 * (a & b).sum() / (a.sum() + b.sum() + 1e-12)


def rigid_fit(field, target, area):
    """Fit translation + rotation + scale to maximise overlap."""
    best = (-1, None)
    for ang in range(0, 180, 6):
        r = rotate(field, ang, reshape=False, order=1, mode="nearest")
        for sc in (0.8, 0.9, 1.0, 1.1, 1.25):
            z = zoom(r, sc, order=1)
            if z.shape[0] < N:
                p = N - z.shape[0]
                z = np.pad(z, ((0, p), (0, p)), mode="edge")
            z = z[:N, :N]
            for dy in range(-40, 41, 8):
                for dx in range(-40, 41, 8):
                    s = np.roll(np.roll(z, dy, 0), dx, 1)
                    d = dice(to_mask(s, area), target)
                    if d > best[0]:
                        best = (d, (ang, sc, dy, dx))
    return best


def tiled_fit(field, target, area, tiles=8, maxshift=14):
    """TILED alignment: split into tiles, shift each independently to fit locally.
    This is the operation named in the published figure's own caption."""
    n = field.shape[0]
    step = n // tiles
    out = np.zeros_like(field)
    for i in range(tiles):
        for j in range(tiles):
            ys, xs = slice(i*step, (i+1)*step), slice(j*step, (j+1)*step)
            tgt = target[ys, xs]
            best, bestv = None, -1
            for dy in range(-maxshift, maxshift + 1, 2):
                for dx in range(-maxshift, maxshift + 1, 2):
                    yy = np.clip(np.arange(i*step, (i+1)*step) + dy, 0, n-1)
                    xx = np.clip(np.arange(j*step, (j+1)*step) + dx, 0, n-1)
                    patch = field[np.ix_(yy, xx)]
                    k = max(1, int(round(area * patch.size)))
                    thr = np.partition(patch.ravel(), -k)[-k]
                    v = dice(patch >= thr, tgt)
                    if v > bestv:
                        bestv, best = v, patch
            out[ys, xs] = best
    return out


target = hull_mask()
wrong = other_target()
area = target.mean()
field = noise_field()

rows = []
d0 = dice(to_mask(field, area), target)
rows.append(("noise, no alignment", d0))

d1, params = rigid_fit(field, target, area)
rows.append((f"noise + rigid alignment (rot {params[0]}deg, scale {params[1]}, shift {params[2:]} )", d1))

d2 = dice(to_mask(tiled_fit(field, target, area), area), target)
rows.append(("noise + TILED alignment (the caption's own method)", d2))

d3 = dice(to_mask(tiled_fit(field, wrong, wrong.mean()), wrong.mean()), wrong)
rows.append(("same noise, TILED alignment fitted to a DIFFERENT target", d3))

w = max(len(r[0]) for r in rows) + 2
print("=" * (w + 14))
print("HOW MUCH 'STRUCTURAL CORRELATION' CAN NOISE ACHIEVE?")
print("input: band-limited noise. Contains no information about any target.")
print("=" * (w + 14))
for name, d in rows:
    print(f"{name:<{w}}{100*d:>10.1f}%")
print("=" * (w + 14))
print(f"\nBaseline (no alignment):        {100*rows[0][1]:.1f}%")
print(f"After tiled alignment:          {100*rows[2][1]:.1f}%")
print(f"Fitted to the WRONG target:     {100*rows[3][1]:.1f}%")
print("\nIf the last two are comparable, the score measures the alignment procedure,")
print("not the data. A blind test cannot contain a step that fits to the answer.")
json.dump({n: float(d) for n, d in rows}, open("runs/overlay_test.json", "w"), indent=1)
