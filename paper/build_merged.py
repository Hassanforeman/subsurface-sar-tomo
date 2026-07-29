#!/usr/bin/env python3
"""
build_refutation.py — rigorous, standalone step-by-step refutation of the single-pass
SAR Doppler tomography claims of subsurface structures beneath the Giza plateau.

Run:    python3.13 paper/build_refutation.py
Output: paper/Refutation_Giza_SAR_Doppler_Tomography.pdf
Dep:    reportlab  (figures embedded from ../runs/ if present)
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, HRFlowable)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "runs")
OUT = os.path.join(HERE, "Giza_SAR_Doppler_Reproduction_and_Refutation.pdf")

TITLE = ("No Reproducible Evidence for Deep Subsurface Structures Beneath the Giza Plateau: "
         "A Controlled Reproduction of Single-Source SAR Doppler Micro-Motion Tomography")
AUTHOR = "Hassan Foreman"
AFFIL = "Independent researcher"
DATE = "July 2026 — preprint v3 (merged reproduction + refutation; see Changes in v3, §3.4)"

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["BodyText"], fontName="Times-Roman",
                      fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Times-Bold",
                    fontSize=12.5, leading=15, spaceBefore=12, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Times-Bold",
                    fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=3)
title_st = ParagraphStyle("title", parent=ss["Title"], fontName="Times-Bold",
                          fontSize=15, leading=19, alignment=TA_CENTER, spaceAfter=6)
center = ParagraphStyle("center", parent=body, alignment=TA_CENTER, spaceAfter=2)
absst = ParagraphStyle("abs", parent=body, fontSize=9.5, leading=13, leftIndent=18,
                       rightIndent=18, spaceAfter=4)
claim = ParagraphStyle("claim", parent=body, fontSize=9.5, leading=13, leftIndent=14,
                       rightIndent=14, textColor=colors.HexColor("#333333"),
                       borderColor=colors.HexColor("#bbbbbb"), spaceAfter=4)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, leading=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#333333"), spaceBefore=2, spaceAfter=10)
ref = ParagraphStyle("ref", parent=body, fontSize=9, leading=12, spaceAfter=3,
                     leftIndent=14, firstLineIndent=-14)

story = []
def P(t, st=body): story.append(Paragraph(t, st))
def S(h=6): story.append(Spacer(1, h))
def rule(): story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#999999"), spaceBefore=6, spaceAfter=6))

def fig(fname, caption, width=5.2*inch):
    path = os.path.join(RUNS, fname)
    if os.path.exists(path):
        try:
            from PIL import Image as PImage
            w, h = PImage.open(path).size
            ar = h / w
        except Exception:
            ar = 0.5
        story.append(Image(path, width=width, height=width*ar)); P(caption, cap)
    else:
        P("[figure %s not found — run the pipeline to generate it]" % fname, cap)

def claim_block(label, text):
    P(f"<b>{label} &mdash; Biondi&rsquo;s claim.</b> {text}", claim)

# ------------------------------------------------------------------ front matter
P(TITLE, title_st)
P(AUTHOR + " &mdash; " + AFFIL, center)
P(DATE, center)
S(3); rule()

P("<b>Abstract.</b> In 2022&ndash;2025, F. Biondi and C. Malanga reported that processing of "
  "spaceborne synthetic-aperture-radar (SAR) data by a Doppler sub-aperture &lsquo;micro-motion "
  "tomography&rsquo; reveals high-resolution three-dimensional structures hundreds of metres to "
  "kilometres beneath the Giza plateau &mdash; including vertical shafts descending ~648 m, "
  "spiral stair-like features, and large chambers. I do not dispute that the surface-vibration "
  "<i>measurement</i> underlying the method is real and useful. I dispute the deep <i>inference</i>. "
  "Working only from the authors&rsquo; own published method and patent, I rebuild the pipeline "
  "faithfully, add the elementary controls the original work omits (a look-order null, an in-data "
  "positive control, a surface-leakage test, a depth-of-peak guard, and a sub-aperture-count "
  "stability test), and apply it to free <b>X-band spotlight</b> data from two independent commercial "
  "sensors (<b>Umbra</b> and <b>Capella</b>) &mdash; the same data class used in the 2025 Giza work, "
  "which closes the &lsquo;different data&rsquo; objection &mdash; over five sites, including a site "
  "with exhaustively documented underground ground truth (Butte, Montana). I show, step by step, that "
  "(i) the &lsquo;steering matrix&rsquo; is, by the patent&rsquo;s own words, a discrete Fourier "
  "transform, which produces structured output from any input; (ii) the depth axis is set by an "
  "investigation frequency of ~22 kHz that is physically impossible for the cited mechanism, and "
  "the reported depth is therefore an arbitrary relabelling, not a measurement; (iii) a faithful "
  "reproduction yields a confident, high-contrast &lsquo;detection&rsquo; that is in fact a "
  "surface-pinned processing artifact corresponding to none of the known subsurface structure; and "
  "(iv) every real site, including the authors&rsquo; own Vesuvius, is statistically "
  "indistinguishable from its null; and (v) stacking five acquisitions of a known-empty site "
  "reinforces a surface-pinned artifact rather than revealing structure, so agreement across "
  "&lsquo;200+ scans&rsquo; reflects the shared operator, not corroboration. I conclude that the "
  "deep-tomography claim is unsupported and "
  "reproducible as an artifact. This is a critique of method and mathematics, not of intent.", absst)
S(2)
P("<b>Keywords:</b> synthetic aperture radar; Doppler tomography; micro-motion; reproducibility; "
  "null result; artifact; Giza.", absst)
rule()

# ------------------------------------------------------------------ 1
P("1. The claims under examination", h1)
P("I restate the authors&rsquo; claims as fairly and specifically as I can, from the 2022 "
  "peer-reviewed paper, the lapsed patent WO2024008365A1 (the fullest public method disclosure), "
  "and the 2025 Khafre presentations:")
claim_block("C1 (mechanism)", "Electromagnetic waves do not penetrate solids; instead, ambient "
            "seismic energy makes the surface and subsurface vibrate, and the subsurface "
            "&lsquo;becomes transparent like a crystal&rsquo; when observed in the micro-movement "
            "domain.")
claim_block("C2 (measurement)", "Splitting the azimuth (Doppler) spectrum of SAR data into "
            "sub-apertures and tracking sub-pixel displacement recovers this surface vibration "
            "field &mdash; a technique the authors validated on ships, bridges and dams.")
claim_block("C3 (inversion)", "A steering matrix A(K_Z, z) focuses the vibration observations in "
            "depth, yielding 3-D tomograms, with depth resolution δz = λR/2A where λ is the "
            "<i>seismic</i> wavelength = v/f.")
claim_block("C4 (deep result)", "Applied to Giza, the method reveals eight cylindrical shafts in "
            "pairs descending to ~648 m (the patent and talks also cite Gran Sasso at 1.4 km), "
            "spiral stair-like structures, and large chambers, interconnecting the pyramids and "
            "Sphinx.")
claim_block("C5 (confirmation)", "More than 200 acquisitions across four satellite operators "
            "(COSMO-SkyMed, Capella, Umbra, ICEYE) return the same structures, which the authors "
            "treat as independent confirmation.")
P("I address each below. My standard throughout is the one the original work does not meet: a "
  "result is a detection only if it exceeds chance <i>and</i> survives controls <i>and</i> "
  "corresponds to independent ground truth.")

# ------------------------------------------------------------------ 2
P("2. Reproduction methodology", h1)
P("I reimplemented the pipeline exactly as disclosed: Doppler sub-aperture decomposition; "
  "adjacent-pair, quality-weighted, detrended sub-pixel tracking; an analytic-signal step that "
  "removes the known ±z mirror-symmetry ghost; multichromatic (range sub-band) analysis and "
  "low-rank+sparse denoising as the authors describe; and a depth focus by discrete Fourier "
  "transform. To this I added the controls the original omits: a look-order-shuffle <b>null</b>; "
  "an in-data <b>positive control</b> (inject and recover a reflector; I also use a hardened, "
  "damped variant); a <b>surface-leakage</b> correlation; a <b>near-surface</b> guard; and a "
  "<b>sub-aperture-count stability</b> test. Every stage passes a synthetic self-test against "
  "known truth (Figure 1); quantitatively, the sub-aperture shift estimator validates to 0.02 px, the "
  "adjacent-pair, quality-weighted micro-motion estimator recovers an injected residual to 0.07 px, and "
  "the end-to-end inversion recovers an injected layer at roughly 27&times; the null level &mdash; so a "
  "genuine signal of that character would be surfaced. Data are free X-band spotlight scenes from two "
  "independent sensors, Umbra and Capella &mdash; the same data class the 2025 work used.")
fig("tomogram_selftest.png",
    "Figure 1. The reproduced inversion on synthetic data: an injected layer is recovered well "
    "above the null, with positive-control and leakage checks passing. The machinery works; the "
    "controls are calibrated.", width=4.8*inch)

P("To make the fidelity of the reproduction checkable rather than asserted, Table 1 maps each "
  "disclosed processing block (patent WO2024008365A1, Fig. 0.5, blocks 1&ndash;11) to the "
  "corresponding component of this implementation. The correspondence is one-to-one; in particular, "
  "the depth-focusing &lsquo;steering matrix&rsquo; is implemented, exactly as the patent specifies, "
  "as a discrete Fourier transform.")
maptbl = [["Disclosed step (patent Fig. 0.5)", "This reproduction"],
          ["SLC image, 2-D DFT (blocks 1-2)", "open_complex SICD reader; FFT in the sub-aperture stage"],
          ["Doppler sub-apertures (master/slave) + range sub-bands (blocks 3-6)",
           "subaperture.decompose_subapertures; multichromatic_subapertures (MCA)"],
          ["Pixel-tracking between sub-apertures (block 7)",
           "micromotion.adjacent_trajectory (adjacent-pair, quality-weighted) + detrend; optional lrsd_denoise"],
          ["Raw tomographic complex vectors (block 8)", "per-patch detrended residual trajectories"],
          ["Steering matrix = DFT depth focus (block 9)",
           "tomogram.steering (DFT basis) + invert_patch (DFT power spectrum)"],
          ["Tomogram, geocode in depth (blocks 10-11)",
           "depth profile; metric_depth_axis (depth-axis labelling)"]]
mt = Table(maptbl, colWidths=[3.0*inch, 3.1*inch])
mt.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
    ("FONTSIZE", (0,0), (-1,-1), 8), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")), ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(mt)
P("Table 1. The authors&rsquo; disclosed processing chain mapped one-to-one onto this reproduction, "
  "so a reader can verify the implementation against the source rather than take its faithfulness on "
  "trust.", cap)

# ------------------------------------------------------------------ 3 refutations
P("3. Step-by-step refutation", h1)

P("3.1 The &lsquo;steering matrix&rsquo; is a discrete Fourier transform (addresses C3)", h2)
P("The patent states, verbatim, that &lsquo;the steering matrix A(K_Z, z) represents the best "
  "approximation of a matrix operator performing the Digital Fourier Transform (DFT) of Y,&rsquo; "
  "and that the depth focus is performed by &lsquo;the DFT mathematical operator.&rsquo; The depth "
  "tomogram is therefore the power spectrum of the per-pixel sub-aperture residual. This is the "
  "crux: a DFT returns a structured, peaked spectrum from <i>any</i> input vector &mdash; signal, "
  "noise, or a residual processing trend alike. A confident-looking tomogram is thus the expected "
  "output of the method <i>whether or not</i> anything lies beneath the surface. It is not, by "
  "itself, evidence of structure.")

P("3.2 The 22 kHz investigation frequency is unphysical, and depth is therefore a free parameter "
  "(addresses C3, C4)", h2)
P("Depth follows δz = λR/2A with λ = v/f. The patent synthesises at an investigation frequency "
  "f ≈ 22 kHz. This is ultrasonic. Ambient and seismic ground motion is overwhelmingly below "
  "~100 Hz; a coherent 22 kHz elastic wave in rock would attenuate within metres and is orders of "
  "magnitude above the sub-aperture pair-axis Nyquist limit &mdash; the aliasing flaw also noted by "
  "independent reproductions. Because f enters only as an axis scale, it does not change the "
  "tomogram pattern at all; it merely relabels the depth axis. Figure 2 makes this concrete: the "
  "identical Butte tomogram, rendered at 22 000 / 1 000 / 50 Hz, places the same feature at ~5 m, "
  "~100 m, or ~2 000 m respectively. The reported depths (648 m, 1.4 km) are a choice of frequency, "
  "not a measurement.")
fig("fcompare_2024-03-07-04-48-26_UMBRA-04_SICD.nitf.png",
    "Figure 2. One tomogram, three investigation frequencies. The data are unchanged; only the "
    "depth axis rescales (δz = vR/2Af). &lsquo;Deep&rsquo; structure is an axis relabelling.",
    width=6.3*inch)

P("3.3 A faithful reproduction yields a confident artifact, not structure (addresses C3, C4)", h2)
P("I ran the authors&rsquo; recipe (256 Doppler sub-apertures, multichromatic analysis, "
  "denoising, 22 kHz) over Butte, Montana &mdash; the most densely mapped underground mining "
  "district on Earth, whose West Camp workings (Travona, Emma, Ophir, Anselmo) are documented as "
  "100-ft-spaced levels from near surface to ~457 m, with a water table / mine pool at ~160 m. The "
  "result (Figure 3) is a striking band at <b>1720&times; the null contrast</b> &mdash; it "
  "<i>passes</i> a naive contrast-vs-null test as a detection. Yet the entire feature is pinned at "
  "the surface (~4 m; 87% of all energy in the shallowest 5% of the axis), aligns with <i>none</i> "
  "of the documented levels or the 160 m water table, and only appears when the sub-aperture count "
  "is driven high. It is a surface/low-frequency residual concentrated by the high-order DFT. My "
  "near-surface and stability guards flag it as an artifact; the authors&rsquo; pipeline, lacking "
  "them, would report it as a discovery. This is, in microcosm, how a &lsquo;shaft&rsquo; is "
  "produced. Butte therefore serves as the closest available known-target benchmark within the "
  "free-data regime: at honest settings the method recovers nothing matching the documented workings "
  "(Section 3.4); at the authors&rsquo; settings the only confident feature is a surface artifact "
  "aligned with none of them.")
fig("repro_2024-03-07-04-48-26_UMBRA-04_SICD.nitf.png",
    "Figure 3. Reproduction on Butte, MT. Left: real tomogram (1720&times; null) &mdash; a confident "
    "band pinned at the surface. Centre: shuffled null. Right: documented workings (100-ft levels to "
    "457 m; water table ~160 m). The &lsquo;detection&rsquo; matches nothing real.", width=6.3*inch)

P("3.4 Every real site is indistinguishable from its null &mdash; including Vesuvius (addresses C4)", h2)
P("At honest settings (with the depth-of-peak and stability guards active), five free X-band sites "
  "across two independent sensors &mdash; Bingham Canyon, Komati, Mount Vesuvius and Butte (Umbra), "
  "and central Cairo (Capella) &mdash; are each statistically indistinguishable from their "
  "look-shuffled nulls, while in-data positive controls confirm the pipeline would surface a genuine "
  "signal. Mount Vesuvius is decisive because it is the authors&rsquo; own peer-reviewed site: the "
  "method, reproduced on free data with controls, does not recover subsurface structure there either. "
  "The Capella scene matters for a separate reason: it reproduces the null on an <i>independent "
  "sensor</i>, so the result is a property of the method, not of any one data provider &mdash; the "
  "very cross-sensor agreement the authors cite as confirmation (C5) yields nulls, not structure, "
  "once controls are applied.")
tbl = [["Site", "Sensor", "Reg. quality", "Real / Null", "Verdict", "Pos. ctrl"],
       ["Bingham Canyon", "Umbra", "0.67", "front-end only", "no signal", "n/a"],
       ["Komati Power Stn", "Umbra", "0.85", "2.8x / 1.3x", "NULL", "PASS"],
       ["Mount Vesuvius", "Umbra", "0.72", "4.1x / 1.5x", "NULL", "PASS"],
       ["Butte, MT", "Umbra", "0.82", "3.3x / 1.4x", "NULL", "PASS"],
       ["Cairo (central)", "Capella", "0.62", "2.8x / 1.6x", "NULL", "PASS"]]
t = Table(tbl, colWidths=[1.35*inch, 0.8*inch, 1.0*inch, 1.15*inch, 0.95*inch, 0.85*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(t)
P("Table 2. Five free single-pass X-band sites at honest settings, across two independent sensors "
  "(four Umbra, one Capella): every real tomogram is indistinguishable from its null; positive "
  "controls pass where run. All Umbra rows are computed at the pipeline default of "
  "<b>11 Doppler sub-apertures</b> (512&times;512 centre crop, 64-pixel patches, 24 patches, 0.8 "
  "sub-band overlap, Hann taper, float64).", cap)

P("<b>Changes in v3 (July 2026).</b> The Komati Power Station row of Table 2 read "
  "&ldquo;50&times; / 10&times;, null&rdquo; in the published v2 of this preprint (Zenodo 10.5281/zenodo.21067830; that PDF labels itself &lsquo;v1.0&rsquo; internally). That row had been computed at 128 Doppler "
  "sub-apertures rather than the default 11 used for every other row, and its verdict label was "
  "incorrect for that setting: at 128 sub-apertures the pipeline returns <i>above null but "
  "surface-pinned &mdash; artifact</i>, not <i>null</i>. Re-run at the default the site gives "
  "2.8&times; / 1.3&times; (ratio 2.15), with the hardened positive control passing and "
  "surface-leakage correlation 0.32. Two independent code paths agree on the corrected value, and "
  "the Butte and Vesuvius rows reproduce their published figures to two decimal places. The site "
  "remains a null result on either reading; the correction <i>increases</i> the margin, since "
  "50&times; / 10&times; is a ratio of exactly 5.0 and sat precisely on the decision rule. No "
  "conclusion in this paper changes. The error was found while stress-testing the pipeline against "
  "an external methodological objection; that work is documented in "
  "<font face=\"Courier\">docs/SENSITIVITY_RESPONSE_BIONDI.md</font> in the repository.", body)

P("<b>Outstanding verification.</b> The Cairo (Capella) row has not been re-verified against the "
  "sub-aperture count stated above, because that scene is not held in the local archive. It is "
  "flagged here rather than assumed correct, and will be re-run for the revision.", body)

P("3.5 &lsquo;200 scans, four satellites&rsquo; is consistency, not corroboration (addresses C5)", h2)
P("Agreement across many acquisitions and sensors is offered as independent confirmation. It is "
  "not. A <i>systematic</i> processing artifact &mdash; a fixed DFT bias, a surface-pinned residual, "
  "the 22 kHz relabelling &mdash; reproduces on every scene and every sensor by construction, "
  "because the same operator is applied to each.")
P("I demonstrate this directly on real data. I stacked five same-geometry Umbra passes of Bingham "
  "Canyon &mdash; a bare open-pit mine of exposed rock containing no subsurface void &mdash; acquired "
  "on five different dates, i.e. precisely the multi-acquisition strategy offered as confirmation. "
  "Each single pass already yields a high-contrast peak (mean 117.8&times; its per-scene null); "
  "stacking the five preserves it at 96.7&times; against a stacked null of 1.5&times;, and the "
  "per-scene profiles agree closely (Figure 4). Yet the reinforced, consistent feature sits at ~3 m "
  "depth (2% of the axis, with 36% of its energy in the shallowest 5%) &mdash; pinned at the surface, "
  "over ground known to contain no such structure. The stack manufactures agreement, not evidence: a "
  "consistent artifact reinforces under stacking exactly as a real reflector would, because the same "
  "DFT operator is applied to each scene. Reproducibility of an output is a property of the "
  "algorithm, not of the ground; the only thing that separates a real reflector from a shared "
  "artifact is ground truth and controls &mdash; which the original work does not apply.")
fig("stack.png",
    "Figure 4. Multi-acquisition stacking of five same-geometry Umbra passes over Bingham Canyon, a "
    "known-empty open-pit mine. Left: the per-scene depth profiles (grey) and their stack (crimson) "
    "collapse onto a surface-pinned peak at ~3 m, far above the scattered stacked null (blue dashed). "
    "Right: the five per-scene profiles, which agree by construction. Stacking reinforces the artifact "
    "rather than revealing structure &mdash; the mechanism behind &lsquo;200+ scans agree.&rsquo;",
    width=6.3*inch)

P("3.6 The penetration-vs-aperture physics does not support deep recovery (addresses C1, C4)", h2)
P("The measurement is a passive, single-surface, narrow-aperture observation. The angular/temporal "
  "aperture available from one acquisition is small, deep energy attenuates, and the inversion is "
  "correspondingly ill-conditioned for anything but the very shallow. More acquisitions improve "
  "shallow resolution and conditioning but cannot restore information the geometry never captured. "
  "Compute amplifies an adequate measurement; it cannot manufacture absent information &mdash; "
  "though, as Section 3.3 shows, it can manufacture a confident <i>artifact</i>.")

# ------------------------------------------------------------------ 4 robustness
P("4. Robustness: could a wrong velocity model hide a real signal?", h1)
P("The natural objection to a null is that the depth axis is uncalibrated: with no site-specific "
  "seismic velocity v(z), might a real reflector be mis-placed and missed? Two versions of this "
  "concern must be separated. <b>Axis calibration is not a threat to the verdict.</b> A velocity model "
  "only maps the relative depth index to metres &mdash; a monotonic relabelling of the z-axis, exactly "
  "the operation Section 3.2 shows the investigation frequency already performs &mdash; and cannot "
  "create above-null contrast where none exists. The real tomograms are indistinguishable from their "
  "shuffled nulls across the <i>entire</i> depth axis, so rescaling that axis leaves the contrast-vs-null "
  "unchanged: there is no signal at any depth to relocate.")
P("The legitimate version is <b>search-grid coverage</b>: if the inversion&rsquo;s depth grid does not "
  "span the depths where a true reflector would sit (because the assumed velocity is wrong), a signal "
  "outside the searched range could in principle be missed. The confirmatory test for this is a sweep "
  "of the assumed seismic velocity by &plusmn;20&ndash;50% with the depth grid widened accordingly, "
  "re-running the null and positive-control diagnostics at each setting; the null is robust only if no "
  "plausible velocity produces an above-null, leakage-clean band. This is the more rigorous form of the "
  "velocity check and the one to report in a journal version. The calibration argument above already "
  "shows that no relabelling can rescue the current verdict &mdash; only a genuine above-null feature "
  "could, and there is none to relocate &mdash; so the sweep tests grid coverage rather than the "
  "conclusion.")

# ------------------------------------------------------------------ 5
P("5. What is real, and what would change my conclusion", h1)
P("To be fair to the authors: the surface-vibration front-end is legitimate and well-precedented. "
  "Their peer-reviewed monitoring of ships, bridges, and the Mosul Dam measures real, millimetric "
  "<i>surface</i> deformation, and that work stands. My critique is confined to the extrapolation "
  "of that surface measurement into deep subsurface structure.")
P("I state my falsifiability explicitly. I would withdraw this conclusion if the method, run with "
  "controls on a site of independently documented subsurface structure, produced an above-null, "
  "leakage-clean, depth-stable band that matched the known structure in position and depth (after a "
  "physically defensible velocity model, not a 22 kHz relabelling). I invite exactly that test. "
  "My pipeline, controls, and data are open for it. The cleanest such test would image an intact, "
  "independently documented void in the correct mode &mdash; for example the Derinkuyu/Cappadocia "
  "underground cities &mdash; which the free archives do not cover and which would require commercial "
  "spotlight tasking; I flag it as the decisive next experiment rather than one the free-data regime "
  "permits. Within that regime, Butte (Section 3.3) is the closest available known-target benchmark, "
  "and the method does not recover it.")
P("A limitation follows directly from this design. This study evaluates the published method as "
  "disclosed in the peer-reviewed papers and the patent (WO2024008365A1), with the fidelity of the "
  "reproduction documented block-by-block in Table 1. If unpublished implementation details "
  "materially affect the inversion, those details would need to be independently disclosed and "
  "evaluated before they could be assessed. The reproducibility framing is therefore deliberate: the "
  "conclusion is about the method <i>as published</i>, and any essential step absent from the public "
  "record is precisely what the original authors would need to provide for the claim to be "
  "re-examined.")

# ------------------------------------------------------------------ 6
P("6. Conclusion", h1)
P("Reproduced faithfully from the authors&rsquo; own method and patent &mdash; with each disclosed "
  "step mapped to its implementation (Table 1) &mdash; single-source SAR Doppler micro-motion "
  "tomography yields no reproducible evidence of deep subsurface structure, and the confident outputs "
  "it does produce are reproducible as artifacts. Its &lsquo;steering "
  "matrix&rsquo; is a DFT that returns structure from any input; its reported depths are set by a "
  "physically impossible 22 kHz frequency and are an arbitrary axis relabelling; a faithful run "
  "produces a confident 1720&times; &lsquo;detection&rsquo; that is a surface-pinned artifact "
  "matching no known structure; and every real site across two independent sensors (Umbra and "
  "Capella), including the authors&rsquo; own Vesuvius, is "
  "indistinguishable from its null; and stacking five acquisitions of a known-empty site reinforces "
  "that surface-pinned artifact rather than revealing structure, so the appeal to &lsquo;200+ "
  "scans&rsquo; supplies consistency, not corroboration. The Giza &lsquo;shafts,&rsquo; &lsquo;spirals,&rsquo; and "
  "&lsquo;chambers&rsquo; are the rendered geometry of such artifacts, interpreted as architecture. "
  "The measurement front-end is real and remains valuable for surface-deformation monitoring; only "
  "the deep-subsurface claim fails reproduction and controls. I frame this as a reproducibility "
  "result, openly testable, and welcome the decisive ground-truth experiment.")

P("Data and code availability", h1)
P("All scenes are free Umbra Open Data and Capella Open Data (CC-BY 4.0); the exact scene "
  "identifiers and acquisition parameters are listed in the repository. The full reproduction "
  "pipeline, the controls, the stress tests (including the frequency-relabelling and surface-pinning "
  "demonstrations), and the scripts that regenerate every figure in this paper are openly available at "
  "https://github.com/Hassanforeman/subsurface-sar-tomo (archived at Zenodo, DOI 10.5281/zenodo.21671687, "
  "release v1.1.0, which is the exact code state that produces the results reported here; the concept DOI "
  "10.5281/zenodo.21065674 always resolves to the most recent release), with "
  "the code under an MIT licence. Every analysis stage carries a synthetic self-test, so the pipeline "
  "can be validated against known truth before it is trusted on real data; a reader can reproduce the "
  "nulls, the artifact, the frequency-relabelling, and the stacking result from the scene IDs and the "
  "scripts alone.")

P("Conflict of interest disclosure", h1)
P("The author declares that he complies with the PCI rule of having no financial conflicts of "
  "interest in relation to the content of the article. The author declares no non-financial conflict "
  "of interest.")

P("Funding", h1)
P("This work received no specific funding. All data analysed are free, openly licensed third-party "
  "products (Umbra Open Data and Capella Open Data, CC-BY 4.0).")

P("Use of artificial intelligence", h1)
P("Artificial-intelligence tools (large language models) were used extensively to assist with "
  "software development, data analysis, and the drafting of this manuscript. The author directed the "
  "research, made all scientific decisions, and checked and verified every output &mdash; code, "
  "figures, and text &mdash; against the underlying data and the cited sources, and is solely "
  "accountable for the content. All figures are generated directly by the analysis pipeline from the "
  "source data and are not AI-generated illustrations. No AI system is listed as an author.")

P("References", h1)
refs = [
    "Biondi, F. &amp; Malanga, C. (2022). Synthetic Aperture Radar Doppler Tomography Reveals "
    "Details of Undiscovered High-Resolution Internal Structure of the Great Pyramid of Giza. "
    "Remote Sensing 14(20):5231. arXiv:2208.00811.",
    "Biondi, F. (2022). Scanning Inside Volcanoes with SAR Echography Tomographic Doppler Imaging. "
    "Remote Sensing 14(15):3828.",
    "Patent WO2024008365A1 (PCT/EP2023/064345; status: ceased). Tomographic Doppler imaging.",
    "Khafre Research Project (2025). Press presentations on subsurface structures beneath the "
    "Khafre pyramid (not peer reviewed).",
    "not-JASH, sar-doppler-tomography; mfwarren, Pyramid (independent reproductions). GitHub.",
    "Milillo, P. et al. (2016). Space geodetic monitoring of engineered structures: the Mosul Dam. "
    "Scientific Reports 6:37408.",
    "Umbra Open Data and Capella Open Data, AWS Registry of Open Data (CC-BY 4.0).",
    "National Mine Map Repository (OSMRE); Montana Bureau of Mines &amp; Geology, Butte district mine "
    "maps and 3-D workings model; U.S. Geological Survey I-2050-C (mines and prospects, Butte 1&deg;x2&deg; "
    "quadrangle).",
]
for i, r in enumerate(refs, 1):
    P("[%d] %s" % (i, r), ref)

rule()
P("<i>Preprint, June 2026. Author: Hassan Foreman. A critique of method and mathematics, openly "
  "reproducible and falsifiable; not an allegation of intent.</i>", cap)

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="Refutation — Giza SAR Doppler Tomography", author=AUTHOR)
doc.build(story)
print("wrote", OUT)
