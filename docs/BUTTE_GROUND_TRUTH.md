# Butte, MT — Shallow-Workings Ground Truth

*Supporting ground truth for the Butte true-positive test (scene
`2024-03-07-04-48-26_UMBRA-04`, footprint ~46.008 N, -112.534 W). Purpose: establish that a
**documented shallow void** genuinely sits under the scene, so the pipeline's null result is a
meaningful miss and not an absence of any target.*

---

## 1. Why Butte is an ideal true-positive target

Butte ("the Richest Hill on Earth") has the **largest network of underground workings per
square mile in the world** — on the order of **10,000 miles of tunnels** packed into roughly a
**7-square-mile** ore body, from **74 major mines**. Unlike Vesuvius (deep, contested) or Giza
(no public ground truth), Butte's subsurface is exhaustively mapped and the workings reach all
the way to the near surface. If a single-pass method can detect a known shallow void anywhere,
it should be here.

## 2. Depth structure (what "shallow" means here)

- After the Anaconda Copper Mining Company consolidated ownership in 1910, engineers mapped
  **each level at 100-foot vertical intervals**; shafts were sunk in 100-ft increments. So the
  workings form a dense stack of horizontal levels starting near surface.
- **Shallowest workings:** the **first levels sit around ~100 ft**, and the earliest
  **1870s–1900s mining was at/near the surface** (open cuts, glory holes, caved ground) before
  the district went deep.
- **Deepest workings:** shafts reach **~5,100 ft (nearly a mile)**; some workings extend **more
  than a mile** below ground surface.
- **Implication for our test:** the depth axis of `tomogram.py` is uncalibrated/relative, but
  the target band of interest is the **shallow stack (surface → few hundred ft)**, which is the
  regime the method has any geometric hope of resolving on a single pass. That target is
  unambiguously present under this footprint.

## 3. Mines near the scene footprint

The footprint (~46.008 N, -112.534 W) sits in the **southwest part of the Butte Hill**, in the
**Butte Mining District (a.k.a. Summit Valley Mining District), Silver Bow County**. Nearby
documented headframes / workings include the **Travona** (site of Butte's first silver strike,
1874 — originally the "Asteroid") and the **Anselmo**, both among the surviving headframes and
both with shallow early workings. Dozens of additional shafts honeycomb the hill immediately to
the north and east.

## 3a. Depth profile under the footprint (for tomogram comparison)

The footprint sits over the **West Camp** — the southwest mine group (Travona, Emma, Ophir,
Anselmo), shallower than the 1.5 km East Camp/central mines. Documented depths:

- **Travona** — oldest mine on the hill (1864, as the "Asteroid"); shaft to **1,500 ft ≈ 457 m**.
- **Emma / Ophir / Anselmo** — same hydraulically-connected West Camp system; workings to roughly
  the 1,000–1,200 ft range; levels driven at **100-ft (30.5 m) intervals** from near surface down.
- **Water table / mine pool** — the West Camp pool / extraction-well screen sits **~155–160 m below
  surface**; the saturated/dry boundary is a real seismic impedance contrast and the **single most
  likely genuine reflector** in the scene (and it moves with pumping — a temporal handle).

So the "real diagram of what's underground" here is: a near-surface-to-457 m stack of ~15 horizontal
levels at 100-ft spacing, three vertical shafts, and a water-table reflector at ~160 m. Rendered as
`runs/butte_ground_truth_section.png` (schematic from published depths — **not** a scan of the
Anaconda level maps, which are request-only from the NMMR).

**Comparison discipline (important):** our tomogram depth axis is **uncalibrated/relative**, so do
not expect metres to line up out of the box. Compare **layout first**: (i) is there a single dominant
reflector that could be the ~160 m water table? (ii) is there a *stack* of closely-spaced returns
matching the 100-ft level cadence? Absolute-depth comparison needs a West Camp velocity model
(v ≈ 300–2000 m/s near-surface weathered rock → faster in fresh granite); only then convert the
axis to metres and overlay this section.

## 4. Authoritative ground-truth sources

- **National Mine Map Repository (NMMR)** — OSMRE, Green Tree, PA. Federal archive of all
  closed/abandoned U.S. mine maps (>275,000 mines), including the **Anaconda Co. underground
  level maps** for Butte (mains, shafts, levels, surface openings). Searchable across 40+
  fields at **mmr.osmre.gov**; map images are not bulk-downloadable but can be **requested by
  Document Number at no charge for noncommercial use**.
- **Montana Bureau of Mines & Geology (MBMG)** — built the definitive **depth-coded 3-D model**
  of Butte's tunnels from Anaconda's record books, and publishes the map *"Butte, Montana,
  Richest Hill on Earth: 100 Years of Underground Mining"* (color-coded by depth). Also see
  MBMG open-file *Geology of the Butte Mining District*.
- **USGS** — *Maps showing locations of mines and prospects in the Butte 1°×2° quadrangle*
  (I-map 2050-C) for regional mine/prospect locations.

## 5. Bottom line for the paper

A known, densely mapped shallow void exists directly under the scene, with formal depth control
available from NMMR/MBMG. The pipeline — at the **best registration quality of any site (0.82)**
and with a **passing in-data positive control** — still returned **indistinguishable from null**
(REAL 3.3× vs null 1.4×; leakage 0.28, single-outlier-driven). This makes Butte the project's
strongest bounding result: on free single-pass X-band data, the method does not detect even a
documented shallow void where it would be most expected to succeed.

---

### Sources
- [New map plots Butte underground — Montana Standard](https://mtstandard.com/news/local/new-map-plots-butte-underground/article_f1de51e2-948f-5634-9aa0-87ad730d9cfd.html)
- [Computer Model Shows Berkeley Pit & Butte Mine Tunnels — PitWatch](https://pitwatch.org/computer-model-shows-berkeley-pit-butte-mine-tunnels/)
- [Mine Surveying, Mine Maps, and Mine Models — Story of Butte](https://storyofbutte.org/items/show/3504)
- [National Mine Map Repository (OSMRE)](https://www.osmre.gov/programs/national-mine-map-repository) · [NMMR search](https://mmr.osmre.gov/)
- [Geology of the Butte Mining District — MBMG open-file (mbmg627)](https://www.mbmg.mtech.edu/pdf-open-files/mbmg627_Butte-miningdistrict.pdf)
- [Travona Mine — Mindat](https://www.mindat.org/loc-6850.html) · [Anselmo Mine — Mindat](https://www.mindat.org/loc-27746.html)
- [Maps showing locations of mines and prospects in the Butte quadrangle — USGS I-2050-C](https://pubs.usgs.gov/imap/2050c/report.pdf)
