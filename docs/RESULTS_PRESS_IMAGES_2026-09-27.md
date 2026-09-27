# What the 2026 "Second Sphinx" press images are — descriptive audit — 27 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_PRESS_IMAGES_2026-09-27.md`, committed `7cca12e` before
download. **Source:** 58 images posted "with permission from Dr. Biondi" on
archaeologicalrescue.org/secondsphinx/ (T. Grassi, 26 Jun 2026); slides of the Bologna/Castel San
Pietro Terme presentation "Il Sonar Spaziale", footer dated 17/06/26, pages ~47-95. Fetched by
`fetch_press_images.sh` into `data/secondsphinx_2026/` (gitignored). Mechanical audit:
`src/press_image_audit.py` → `runs/press_image_audit.json`. Everything else is direct inspection
(file IDs cited so each point can be checked). Critique of method, not intent.

## 1. Inventory
57 slides export at 3308x2479 (a 4:3 deck); 62.jpg is 3301x2195. Only 17.jpg carries metadata:
Adobe Photoshop 26.11 (Macintosh), 2026-06-25 02:25 — that is the page author's edit time (his
screenshots on the page are timestamped the same night), **not** evidence about Biondi's tools.

| Group | Files | What they are |
|---|---|---|
| Great Sphinx "polarimetric Doppler tomography" | 07, 08 | Paper-style multi-panel figure, (a)-(h) |
| MATLAB tomogram | 17 (also inset in 27, 32) | MATLAB figure window + a tomogram photographed off a screen |
| Second Sphinx 2-D lines | 22, 29, 34, 60, 61 (and in 23-37) | jet heat-maps, no axes, no colour bar |
| Heat-map on photos of the Great Sphinx | 23-25, 30-31, 34-38 | lines placed beside/over photos, arrows drawn feature-to-blob; 38 is the heat-map perspective-warped onto a photo |
| Face-proportion templates drawn on heat-maps | 26, 43-52, 58 | head outlines, "linea occhi / base naso / linea bocca", golden-ratio spirals, "Rule of Fifths", ratios "1 : 0.68 : 0.62" |
| "3-D volumetric reconstruction" infographics | 40, 41, 41-1, 42, 57, 58, 62-1, 62, 63, 64 | dark-theme infographic panels with photorealistic renders of a sphinx, percentages, tables |
| Comparisons to a stylised sphinx picture | 53-56 | contour maps with arrows to a painted, intact sphinx with striped headdress |
| "Colloqui tra Filippo e AI" | 26, 31 (title), 66 (Google Gemini), 69-71 (Grok) | slides presenting chatbot outputs |
| Giza plateau 3-D scene | 78-1, 79 | textured terrain slab, pyramids, shafts, cubes, "Tag 13 … Tag 51" |
| Other | 19-20 (top-view heat-map vs a 3-D model of the known Great Sphinx), 28, 33, 72-74, 80 | maps, dig proposal, title slide |

## 2. Findings (grade: [E] seen on the slide; [S] strongly indicated; [H] hypothesis)

1. **The measured product is still the 2022 product.** Every Second Sphinx tomogram (22, 29, 34, 60,
   61) is a 2-D jet heat-map with no axes, no colour bar, no scale. The "3-D" is built from four such
   2-D views named Sfinge_101/102/103 + top view (40, 41, 58): 41 is titled "Fotogrammetria
   multi-vista + integrazione geometrica + filtraggio + fusione volumetrica". [E]
2. **The detail enters through templates, photos and AI — stated on the slides.** The pipeline slide
   (71, "Colloqui tra Filippo e AI (Grok)") lists: Multi-View Registration & 3D Reconstruction;
   **Thermal-to-Visible GAN (Pix2Pix / CycleGAN)**; 68+ landmark detection (DeepFace + MediaPipe);
   forensic facial approximation (Manchester method); golden-ratio / Egyptian canon grid; ArcFace /
   Eigenface embedding. A Pix2Pix/CycleGAN is an image-to-image generator: it synthesises a
   visible-light-looking image in the style of its training data. Face-landmark tools are built to find
   a face. [E that these are listed; what each did is not stated]
3. **The reconstructions carry the known Great Sphinx's form.** The renders (40-42, 57, 58, 62-64) show
   nemes headdress, forepaws and body proportions of the Great Sphinx; 19-20 compare to a 3-D model of
   the Great Sphinx itself; 53-56 compare to a painted intact sphinx. 42's "estimated total length
   73.0 m" is the Great Sphinx's commonly quoted length. [E for what is shown; S that the template
   supplies the shape]
4. **The infographic panels have the look of generative-AI images.** Garbled/misspelt text in the
   graphics (41: "Normalizaazione"), glossy dashboard styling, photoreal renders with no named software,
   and several sit in slides titled as conversations with Grok/Gemini. 41 carries its own disclaimer:
   probabilities "calcolate su base geometrica, volumetrica e multi-vista (non archeologica)". [S, not
   proven: we cannot identify the generator]
5. **The probabilities are chatbot/classifier outputs, not measurements.** 96.1% (66, Gemini;
   62 "FUSIONResNet+GCN"), 94% (70, Grok "blind test"), 83% / 78% / 72% (41, 40, 58). The "blind test"
   (69) says Grok got the maps with no prior indication; we cannot see what it was given, and the same
   deck shows the maps annotated with face templates (43-52). [E numbers; blindness unverifiable]
6. **Manual placement is visible.** Presentation-software selection handles on stretched heat-maps
   (38, 39, 47, 60); 38 is the heat-map skewed in perspective onto a photograph of the Great Sphinx.
   This is the by-eye stretch the 2022 reviewer described, done on screen. [E]
7. **Scale belongs to templates, not data.** 58's axes are fractions of an assumed height H ("Linea
   occhi 0,62 H", "Totale lunghezza ≈ 2.22 H"), i.e. the canon's proportions. The only metric depth
   axis in the set is 07/08 (Great Sphinx: "Heigth (m)" 0 to −1200, horizontal in pixels) — the
   frequency-set relabel already derived (TECHNICAL_BIBLE; depth = (v/f)·R/2A). [E]
8. **The Giza 3-D scene is a modeller scene built from primitives.** 78-1/79: identical helical blue
   columns, identical yellow boxes, grid floor, an on-screen navigation control (79 bottom-left), and
   the 2022 "Tag N" labelling (up to Tag 51). [E]
9. **Display tool for tomograms: MATLAB.** 17 shows the MATLAB figure toolbar; its right panel is a
   photograph of a screen. [E]

## 3. Pre-stated expectations (E.3)
- **X1 HIT** — no image states a voxel size together with a threshold / iso-level. None states a
  threshold at all.
- **X2 HIT** — 78-1/79 show modeller traits (navigation control, grid floor) and repeated identical
  primitives.
- **X3 PARTIAL** — the Second Sphinx lines are the 2022 format without metric axes (hit); the Great
  Sphinx figure 07/08 has a metric depth axis (miss for that figure).

## 4. What this means (honest reading)
- For the 2026 images, Step 6 of HOW_BIONDI_DOES_IT moves from [H] to largely [E] **by their own
  slides**: the input is 2-D heat-maps; the shape is supplied by a known-sphinx template, face-
  proportion grids, a generative image-to-image network, face-landmark/embedding tools and chatbot
  dialogue; the percentages are those tools' outputs.
- It does **not** tell us which specific pixel came from which tool, nor that any image was made
  dishonestly. It does settle that the published appearance is not a rendering of a measured volume.
- Irony worth stating plainly: we used Grok for leads and verified everything; the 2026 deck presents
  Grok and Gemini outputs as validation. A language/vision model asked about sphinx-annotated maps
  will produce confident sphinx numbers. That is not evidence either way about the ground.

## 5. Hypothesis for the next pre-registered test (feeds STATE item "shafts are surface-driven")
The raw 2026 product is the same 2-D range x depth heat-map, and its most prominent features are
vertical streaks (61; 07/08; 17). [H] A vertical streak is a patch whose whole detrended spectrum is
elevated — a surface property — so streaks should co-locate with surface-trajectory energy. This is
testable on our own Giza lines; it is the next step (a).

## 6. What this does not show (E.4)
Intent; which generator made which graphic; whether any buried feature exists. Images are not
redistributed; the contact sheets in runs/ stay out of git.
