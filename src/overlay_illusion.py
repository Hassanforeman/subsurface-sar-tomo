#!/usr/bin/env python3
"""
overlay_illusion.py — what an overlay presentation does, regardless of the data.

WHY THIS EXISTS
---------------
The published Giza figures (34-50) share one caption: "Tags association from
tomography to 3D model. (a): 3D model of Khnum-Khufu. (b): Tomographic
reconstruction (magnitude)." A CAD model and a tomogram, presented together.

The Titanic post states the same construction outright: "overlaying HarmonicSAR
data of the wreck with the existing optical imagery."

In both cases the reader is shown the target and the tomogram in one frame. This
script asks a narrow question: **when a tomogram containing no information about
the target is overlaid on an image of the target, what does the composite look
like?**

The answer does not depend on the tomogram. That is the point.

This is not a claim about what anyone did. It is a demonstration of what the
presentation format does, and it motivates one request that would settle it:
publish the tomogram on its own, without the underlay.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.ndimage import gaussian_filter

rng = np.random.default_rng(3)
N = 420

# ---------------------------------------------------------------- the "optical" reference
def wreck_photo(n=N):
    """A grey, textured, photograph-like image of a hull lying on a seabed."""
    y, x = np.mgrid[0:n, 0:n].astype(float)
    img = 0.10 + 0.05 * gaussian_filter(rng.normal(0, 1, (n, n)), 9)     # seabed
    cx, cy = n * 0.48, n * 0.54
    hull = (((x - cx) / (0.34 * n)) ** 2 + ((y - cy) / (0.085 * n)) ** 2) < 1.0
    hull[:, int(0.52 * n):int(0.57 * n)] = False                          # broken in two
    bow = (((x - n * 0.20) / (0.10 * n)) ** 2 + ((y - cy) / (0.05 * n)) ** 2) < 1.0
    img[hull] = 0.62
    img[bow] = 0.70
    for k in range(6):                                                    # deck detail
        r = int(cy + (k - 2.5) * 0.014 * n)
        img[r:r + 2, int(0.16 * n):int(0.50 * n)] *= 1.25
    img += 0.03 * gaussian_filter(rng.normal(0, 1, (n, n)), 1.2)          # grain
    return np.clip(img, 0, 1)

# ---------------------------------------------------------------- the "tomogram"
def tomogram_from_nothing(n=N):
    """Band-limited noise. No scene, no target, no information about the hull."""
    f = gaussian_filter(rng.normal(0, 1, (n, n)), 7)
    f = (f - f.min()) / (np.ptp(f) + 1e-12)
    return f

photo = wreck_photo()
tomo = tomogram_from_nothing()

fig, ax = plt.subplots(1, 3, figsize=(16.5, 6.0), facecolor="white")

ax[0].imshow(photo, cmap="gray", vmin=0, vmax=1)
ax[0].set_title("A. The optical reference\n(the wreck, photographed)", fontsize=11)

ax[1].imshow(tomo, cmap="turbo")
ax[1].set_title("B. The tomogram, ALONE\nbuilt from random numbers - no scene, no target",
                fontsize=11)

ax[2].imshow(photo, cmap="gray", vmin=0, vmax=1)
ax[2].imshow(tomo, cmap="turbo", alpha=0.55)
ax[2].set_title("C. B overlaid on A at 55% opacity\n"
                "reads as though the tomogram reveals the hull", fontsize=11)

for a in ax:
    a.set_xticks([]); a.set_yticks([])
    for s in a.spines.values():
        s.set_color("0.6")

fig.suptitle("Every structure visible in panel C comes from panel A. Panel B contains no "
             "information about the target.", fontsize=13)
fig.text(0.5, 0.035,
         "The composite cannot distinguish a tomogram that found the hull from one that "
         "found nothing.\nThe test that separates them is to publish panel B on its own.",
         ha="center", fontsize=10.5, color="0.25")
fig.tight_layout(rect=[0, 0.075, 1, 0.93])
fig.savefig("runs/overlay_illusion.png", dpi=140, bbox_inches="tight", facecolor="white")
print("figure -> runs/overlay_illusion.png")

# quantify: how much does the composite resemble the photo, vs the tomogram?
comp = 0.45 * photo + 0.55 * tomo
print(f"\ncorrelation of the composite with the PHOTO    : {np.corrcoef(comp.ravel(), photo.ravel())[0,1]:+.3f}")
print(f"correlation of the composite with the TOMOGRAM : {np.corrcoef(comp.ravel(), tomo.ravel())[0,1]:+.3f}")
print(f"correlation of the TOMOGRAM with the PHOTO     : {np.corrcoef(tomo.ravel(), photo.ravel())[0,1]:+.3f}")
print("\nThe tomogram and the photo are uncorrelated. The composite resembles both,")
print("because it contains both. A viewer cannot unmix them by eye.")
