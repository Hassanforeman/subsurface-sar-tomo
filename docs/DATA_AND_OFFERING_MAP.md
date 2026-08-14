# Data Landscape, Accuracy & Offering Map

*A "for future reference" memo. If you ever circle back to the commercial idea, start here so you
don't re-learn it from scratch. Written to be honest, not encouraging — the encouraging version is
what wastes money. Figures are best-estimate as of mid-2026; re-check before acting on them.*

---

## 1. What our front end can probably measure (accuracy)

- **Method:** amplitude pixel-tracking of Doppler sub-aperture looks (not interferometric phase).
- **Validated (synthetic only):** sub-aperture shift to ~0.02 px; residual micro-motion to ~0.07 px.
- **Translated to ground:** on commercial spotlight pixels (~0.25 m), that is roughly **5–20 mm in
  ideal synthetic conditions — centimetre-class.** Real-world will be worse (decorrelation,
  atmosphere, SNR), and we have **never validated against ground truth.**
- **Versus competitors:** coarser than both. Kurloo ~2–3 mm (GNSS phase); InSAR mm-level (radar
  phase). They use phase; we use amplitude tracking, which is inherently blunter.
- **Honest takeaway:** our distinctive capability is a *different quantity* (fast vibration, not slow
  displacement) at *lower* precision — not a "better" version of what the market buys. Reaching
  mm-class would require interferometric phase processing (harder; decorrelation-prone single-pass).

## 2. The data we could get

**Free, global, periodic (the workhorses):**
- **Sentinel-1** (ESA, free/open) — systematically images all land every ~6–12 days, C-band.
- **NISAR** (NASA-ISRO, free) — global L-band, recently delivering data.
- These are the standard feedstock for InSAR deformation monitoring. Marginal data cost ≈ $0.

**Paid, on-demand, high-res (the right mode for *our* method):**
- **Umbra, Capella, ICEYE** — X-band spotlight to ~25 cm, self-serve **tasking APIs**; aggregators
  (Ursa Space, SkyFi) give one interface across providers. Order anywhere on Earth; pay per scene.

**The catch that drives everything:**
- Free global archives (Sentinel-1, NISAR) are stripmap/scan/TOPS modes — the **wrong mode** for our
  single-pass Doppler vibration method, which needs **spotlight** (long dwell, wide Doppler band).
- Spotlight (right for us) = **paid, per-scene tasking**, not free/global.
- So: the abundant free data feeds InSAR settlement (which we have NOT built); our method needs paid
  data per site.

## 3. Offering map — data → product

| Data source | Cost | Feeds our vibration method? | Feeds InSAR settlement? | Product it enables |
|---|---|---|---|---|
| Sentinel-1 / NISAR (global, free) | ~$0 | No (wrong mode) | Yes (the workhorse) | Slow-settlement monitoring, anywhere, ~zero data cost |
| Umbra / Capella / ICEYE spotlight | $/scene | Yes | Yes (task repeats) | Our vibration niche, or premium high-res monitoring |

**The irony to remember:** the free, plentiful data only supports the product we *don't* have
(InSAR settlement). Our actual tool (spotlight vibration) needs paid data and has unproven demand.

## 4. Competitive landscape (Queensland-relevant)

| | Kurloo | Geomotion (PS-InSAR) | Ours |
|---|---|---|---|
| Quantity | Slow displacement | Slow deformation | Fast vibration (~3 s) |
| Tech | GNSS-IoT ground device | Satellite InSAR (multi-pass) | Satellite single-pass Doppler |
| Install? | Yes (1 device = 1 point) | No | No |
| Coverage | Point-based | Wide-area (100 m²–10,000 km²) | Wide-area snapshot |
| Cadence | Daily | Weekly; needs time-baseline | One snapshot |
| Accuracy | ~2–3 mm (spec'd) | mm-level (spec'd) | ~cm-class, unvalidated |
| Maturity | Commercial, "defensible by design" | Commercial, operational | Research script |
| Blind spots | Cost/effort scales per point | Fails over vegetation/water/fresh earthworks; needs history | Unvalidated; paid data; unproven demand |

**On the paying use case (settlement), we are not in the race** — we have no product and would build
InSAR from scratch against funded incumbents, including a local QUT-backed one (Kurloo).

## 5. Honest strategic conclusion

- The 15-year non-monetization of satellite *vibration* sensing is a strong signal that **that
  specific product** is thin or hard. Our tool is the weakest horse in the stable: coarser accuracy,
  paid data, unproven demand.
- What genuinely changed in ~5 years — free global frequent data (Sentinel-1/NISAR), cheap
  constellations with self-serve tasking, collapsed cloud-compute cost — opened a window, but for
  **accessible, honest, cheap-data deformation monitoring**, not for our vibration method. That is
  *why* Kurloo and low-cost InSAR players are emerging now.
- If a business exists for us, the data economics point to **InSAR-settlement on free Sentinel-1 +
  an honesty/plain-language UX layer** — a UX/services company, not a physics one, on the
  competitors' turf, where the only edge is trust and translation.
- **The real prize we built is the refutation paper and the validation discipline** — a credible,
  genuine contribution. The commercial spin-off is a "maybe," and a *different* maybe than we started
  imagining.

## 6. If you ever circle back — what the honest product would take

1. **Build/borrow an InSAR pipeline** on free Sentinel-1 (co-registration, atmospheric correction,
   persistent-scatterer selection, uncertainty budget). Or resell/wrap an existing provider at first.
2. **Validate accuracy** against ground truth (survey leveling, GNSS, corner reflectors) and publish
   the error budget. No claims without it.
3. **Plain-language UX:** draw a box → "is your ground moving, yes/no, with confidence," no jargon,
   **no underground/void claims, ever** (that would contradict the refutation paper and torpedo the
   one asset — trust).
4. **Liability:** frame strictly as screening/early-warning, never certification; price real
   professional-indemnity insurance, not a $5–15k afterthought.
5. **Find the gap empirically first:** talk to 5–10 Brisbane/QLD construction & mining PMs — do they
   monitor ground movement, how, what's it cost, where do Kurloo/Geomotion fall short (greenfield,
   vegetated, fresh earthworks), and would they pay for a simpler/faster/plain-English version. One
   afternoon of this beats months of building. Build nothing until it says yes.

---

### Sources
- Kurloo specs/how-it-works: kurloogeomonitoring.com ; kurloo.io
- Geomotion InSAR: geomotion.com.au/insar-monitoring.html
- Sentinel-1 revisit/coverage: sentinel.esa.int ; registry.opendata.aws/sentinel-1
- NISAR data: science.nasa.gov/mission/nisar/data
- Tasking APIs: capellaspace.com/solution/automated-tasking ; info.ursaspace.com (feasibility/tasking)
- Commercial SAR comparison / resolution: spacenexus, eoportal (ICEYE), syntheticapertureradar.com
