# How Biondi produces his results — the complete mechanism

*The consolidated account Hassan wanted written down: the full pipeline from raw SAR to the final
"underground city"/Titanic imagery, separating what is real from what is manufactured, with an
evidence grade on every link. A critique of method and mathematics, not an allegation of intent.*

*Evidence grades:* **[E]** established/proven (by us or from his own words/figures) ·
**[S]** strongly evidenced · **[H]** hypothesis consistent with the evidence, not proven.

---

## The chain, step by step

### Step 1 — The real front-end: surface micro-motion **[E, legitimate]**
A single staring-spotlight SAR scene is split into Doppler sub-apertures; sub-pixel co-registration
between them recovers a sub-millimetre map of how the **surface** moved during the ~seconds-long
collect. This is Biondi's genuine, peer-reviewed capability (ships, bridges, the Mosul Dam). Nothing
penetrates the ground; the surface vibration is the only measurement. This part stands.

### Step 2 — The trajectory is a running total → a random walk **[E]**
Per patch, adjacent-look displacements are accumulated (`np.cumsum`). A running total of noisy
increments is a random walk: smooth, strongly autocorrelated, 1/f^2 spectrum — **by construction,
with or without any scene**. (We reproduce every downstream signature from accumulated Gaussian
noise with no SAR data at all.)

### Step 3 — The "steering matrix" inversion is a DFT → a surface-pinned peak **[E]**
The patent states the steering matrix "performs the DFT." So the depth tomogram is the power
spectrum of that random-walk trajectory, after a degree-2 detrend. That always peaks at a fixed
shallow position — **1.68 resolution cells** (we derived this exactly). Result: a confident, shallow
peak appears for any input. It is the expected output of the operator, not evidence of structure.

### Step 4 — Depth in metres is an axis relabel, set by an unphysical frequency **[E]**
Depth = (v/f)·R/2A. The investigation frequency f never enters the inversion; it only multiplies the
axis label. The patent uses f ≈ 22 kHz (ultrasonic — impossible for ambient seismic energy, which is
< ~100 Hz). Change f and the identical tomogram reads 5 m, 100 m or 2 km. "648 m" / "1.4 km" are
dial settings, not measurements.

### Step 5 — Manufacturing confidence **[E]**
The apparent strength is tunable by undisclosed knobs: raising the sub-aperture count inflates the
peak-to-median contrast without bound (longer walk = smoother = higher contrast); the window taper
moves it ~34%; over-extending the depth grid manufactures a high-contrast alias. None of these is
disclosed, so a reader cannot audit which number they are seeing. "200+ scans across 4 satellites
agree" is not corroboration: the **same operator** applied to every scene reproduces the **same
artifact** every time (we showed stacking a known-empty pit reinforces it). Consistency proves the
artifact is systematic, not that it is real.

### Step 6 — Turning blobs into recognizable objects (the crux) **[E for the mechanism; H for "this made a specific figure"]**
The depth product is genuinely low-resolution — tens to hundreds of metres per voxel under honest
physics, ~2 m x ~12 m even at his own unphysical 22 kHz best case (Fresnel-limited; see
`BIONDI_IMAGERY_ANALYSIS_2026-09-03.md`). A recognizable face (4-5 m, with a ~0.6 m cobra) or a hull
with rivets is **1-3 orders of magnitude finer than the method's own resolution**. So the detail
cannot be in the data. It is supplied downstream, by one of:
- **3D-model association** — his 2022 paper pairs the tomogram with a pre-made CAD model, captioned
  verbatim "Tags association from tomography to 3D model. (a): 3D model of Khnum-Khufu.
  (b): Tomographic reconstruction (magnitude)." The geometry is the model's. **[E]**
  *Measured 27 Sep 2026 (pre-registered):* across all 16 such pairs the model panel carries ~10x the
  independent detail of the tomogram panel (15/16); every tomogram panel is an unscaled 2-D heat-map
  (no volume is rendered anywhere), the link is hand-placed tags, and 4/16 tomogram panels are
  overlays on pre-existing drawings/photos of the known interior. → RESULTS_FIGURES_2026-09-27.md **[E]**
- **Photo overlay** — his 2026 Titanic frame is labelled on the image itself "In-situ Photo Overlay
  (tilted for alignment)": a real seabed photograph composited onto the blob field. The hull is the
  photo's; the radar layer is colour mush. **[E]**
- **AI + rendering** — "AI used as a secondary source"; isosurface/threshold/colour choices. We
  showed rendering an EMPTY noise volume produces discrete "solid bodies" and vertical shaft-like
  runs from nothing. **[E that rendering manufactures shapes; H that it made his specific images]**

### Step 7 — The epistemic wrapper **[E, from his own words]**
"These are photographs, no validation needed"; depth "by counting pixels"; "we asked an AI, 99.9%";
"#BlindTest" (while overlaying the known answer). None is validation. The Titanic post's "the hull
keeps emerging with surgical precision" is backwards — the precision is the overlaid photograph's.

---

## The one-paragraph version
He measures a real surface vibration field (legitimate), accumulates it into a random walk, and runs
a DFT that — for any input — yields a confident shallow peak whose "depth" is an arbitrary label set
by an unphysical frequency. The output is a coarse, blobby volume. The recognizable pyramids, Sphinx
face, and Titanic hull are then supplied by associating that volume with a pre-existing 3D model or
an actual photograph, cleaned up with AI and rendering. The measurement carries none of the detail;
the model/photo/renderer carries all of it. Multi-scan "agreement" is the same operator repeating
the same artifact. The Titanic frame — a photo overlay labelled as such, over water microwave radar
cannot penetrate (skin depth ~2.5 mm vs 3.8 km) — is the clearest single demonstration.

## What is NOT claimed (honesty guardrails)
- Not fraud/intent — this describes method and mathematics.
- We did NOT reproduce his exact published 3-D figures; Step 6's "this made that specific image" is
  [H]. What is [E] is the resolution gap, the two overlay examples (his own caption/label), and that
  rendering manufactures shapes.
- The surface-measurement front-end is real and useful for shallow deformation/monitoring.

## Pointers
Mechanism/derivations: paper v5 §3-§5; `RESULTS_2026-07-31_FIVE_SITE.md` §12-§15; depth constant
`RESULTS_DEPTH_CONSTANT_2026-09-02.md`. Imagery: `BIONDI_IMAGERY_ANALYSIS_2026-09-03.md`,
`src/resolution_vs_feature.py`. Method context: `BIONDI_METHOD_ANALYSIS.md`.
