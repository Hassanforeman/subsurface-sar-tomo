# How Biondi's "Second Sphinx" imagery is built — the resolution contradiction — 3 Sep 2026

Investigates Hassan's hypothesis: the SAR micro-motion tomography is genuinely low-resolution
(as we measured), but the recognizable DETAIL in the end-products (a Sphinx face with a cobra;
"chambers"; "shafts") does not come from the radar — it enters through a pre-made 3D model / mesh
and AI/rendering. Script: `src/resolution_vs_feature.py`.

## 1. What the 2nd-Sphinx ("Atto Finale") presentation claims

From the Archaeological Rescue Foundation write-up and coverage of the Castel San Pietro Terme
presentation: a buried sphinx "roughly the same size and shape as the Great Sphinx" west of it;
three large shafts; a cubic chamber ~500-600 m deep; more at ~1000-1200 m. The face is claimed to
show "proper proportions of the chin, mouth, nose, eyes, and even an intact Uraeus Cobra affixed to
the forehead." The pipeline is described as slicing the object into "two-dimensional cross sections"
compiled "into a three-dimensional mesh," with "AI used as a secondary source to dispel pareidolia."

## 2. The resolution contradiction (the decisive argument)

To render a feature you need at least ~2 samples across it (Nyquist). The claimed features:
whole face ~4 m (need voxel <=2 m), nose/mouth/eye ~1 m (<=0.5 m), the uraeus cobra ~0.6 m (<=0.3 m).

What the method can actually resolve at 500-1200 m depth (R=650 km, A=42 km):

| resolution limit | honest ambient seismic | authors' 22 kHz (unphysical) |
|---|---|---|
| vertical dz = (v/f)R/2A | **155-464 m** | 2.1 m |
| horizontal at z=500 m (Fresnel sqrt(lambda z)) | **173 m** | 11.7 m |
| horizontal at z=1000 m | **245 m** | 16.5 m |

The Fresnel point matters: a reflector at depth z spreads its surface imprint over ~sqrt(lambda z),
so the 0.5 m radar SURFACE pixel does **not** carry to depth — the inversion cannot localise a deep
feature finer than its Fresnel zone, whatever the surface sampling. (Pomposi independently put
single-pass depth resolution at ~285 m.)

**Conclusion.** Under honest physics one resolution cell is 20-300x LARGER than the whole 4-5 m
face — the face is sub-voxel and cannot exist in the data. Even granting the authors' own
unphysical 22 kHz best case, one voxel (~2 m x ~12 m at 500 m) is about the size of the entire
face, so the data can yield at most ONE blob for the whole head; a 0.6 m cobra needs ~6x finer than
their own claimed resolution and ~200x finer than honest physics. **The chin/nose/eyes/cobra detail
is 1-3 orders of magnitude finer than the method's own claimed resolution.** It is not measured.

## 3. Two claims that cannot both be true

- Claim A: the images resolve a face with a cobra (and chambers, spiral shafts) at 500-1200 m.
- Claim B: the input is spaceborne SAR surface-micro-motion, whose resolution at those depths is
  metres (their best case) to hundreds of metres (honest), by their own delta-z formula and by the
  seismic wavelengths ambient energy actually carries (<~100 Hz).

A and B differ by 1-3 orders of magnitude. B is fixed by physics and by the authors' own equation,
so the fine detail in A cannot originate in the measurement. It must be injected downstream.

## 4. Where the detail comes from (the CAD/mesh + AI mechanism)

This is not speculation about intent; it follows from the authors' own figures and words:
- **The 2022 paper pairs a pre-made 3D MODEL with the tomogram.** Figures 34-50 are captioned,
  verbatim, "Tags association from tomography to 3D model. (a): 3D model of Khnum-Khufu.
  (b): Tomographic reconstruction (magnitude)." The recognizable geometry is in the MODEL panel;
  the tomogram panel is a blobby magnitude. The final picture's realism is the model's, not the radar's.
- **The 2nd-Sphinx pipeline "compiles cross-sections into a 3D mesh"** and uses **AI** — both are
  detail-generating / detail-imposing steps downstream of the low-res data. A mesh fit to sparse
  blobs, or an AI "cleanup," supplies structure the blobs do not contain.
- **Our own test (paper §7):** isosurface-rendering an EMPTY (noise) volume through a plausible
  pipeline produces discrete "solid bodies" and vertical runs from nothing. Rendering choices alone
  manufacture architecture-like shapes. We could NOT reproduce his specific published figures, so we
  do not claim they ARE our artifact — but we show the class of operation that turns blobs into shapes.

**Most parsimonious reading:** the radar delivers a coarse, blobby vibration-vs-depth volume; the
recognizable Sphinx face / chambers are supplied by fitting/associating that volume to a
high-detail 3D model and by AI "confirmation," then rendered. The measurement cannot carry the
detail; the model and the renderer can. That is exactly the contradiction Hassan identified.

## 5. Titanic claim — UNVERIFIED (open)

Two web searches found no documented case of Biondi applying his SAR/micro-motion method to the
Titanic. The prominent 2026 Titanic 3D imagery is the unrelated Magellan/Atlantic Productions sonar
+ photogrammetry survey. If Biondi has made a Titanic claim, we need the source (a talk, post or
date) before analysing it. NB: if such a claim exists, the SAME resolution logic applies and is in
fact worse — the Titanic is under ~3,800 m of seawater, and microwave SAR does not penetrate water
at all, so any "micro-motion" of a seabed wreck is not observable from orbit by this method.

## 6. What would make this airtight (optional next steps)
- Pixel-measure a published "face" figure: count the actual distinct grey/colour levels and effective
  voxels across the face; show it carries far fewer independent samples than facial sub-features need.
- Obtain a frame where the tomogram-magnitude panel and the 3D-model panel are shown separately and
  demonstrate the detail lives only in the model panel.
- If a Titanic source surfaces, apply §2's math with the water-penetration point.
