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
OUT = os.path.join(HERE, "Giza_SAR_Doppler_Reproduction_and_Refutation_v5.pdf")

TITLE = ("No Reproducible Evidence for Deep Subsurface Structures Beneath the Giza Plateau: "
         "A Controlled Reproduction of Single-Source SAR Doppler Micro-Motion Tomography")
AUTHOR = "Hassan Foreman"
AFFIL = "Independent researcher"
DATE = "August 2026 — preprint v5 (Giza plateau added; mechanism identified; decision statistic stress-tested; nulls re-based; see §10)"

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

P("<b>Abstract.</b> In 2022&ndash;2025, F. Biondi and C. Malanga reported that Doppler sub-aperture "
  "&lsquo;micro-motion tomography&rsquo; of spaceborne synthetic-aperture-radar (SAR) data reveals "
  "three-dimensional structures hundreds of metres to kilometres beneath the Giza plateau &mdash; "
  "vertical shafts descending ~648 m, spiral stair-like features, and large chambers. The 2022 paper "
  "was retracted by <i>Remote Sensing</i> on 10 August 2026. I do not dispute that the "
  "surface-vibration <i>measurement</i> underlying the method is real and useful; I dispute the deep "
  "<i>inference</i>. Working only from the authors&rsquo; own method and patent, I rebuild the "
  "pipeline, add the controls the original omits, and apply it to free X-band spotlight data from two "
  "independent commercial sensors (Umbra and Capella) over <b>six sites, including the Giza plateau "
  "itself</b> and a site with exhaustively documented underground ground truth (Butte, Montana). "
  "<b>First, the reported depth in metres is exactly proportional to an investigation frequency "
  "chosen by the analyst rather than measured:</b> the frequency never enters the inversion, "
  "appearing only in a final axis relabelling, so &lsquo;648 m&rsquo; is a label, not a measurement. "
  "Second, the method returns the same confident, surface-pinned feature at every site tested: "
  "<b>48 runs, 0 detections, peak confined to 1.2&ndash;1.9 resolution cells</b> across six sites, "
  "two sensors, eight sub-aperture counts and thirteen patch geometries. On the Giza plateau itself &mdash; "
  "run against predictions published before the data were processed &mdash; 8/8 runs are surface-pinned "
  "with 0/8 detections. Third, I identify the mechanism: the per-patch trajectory is a running total "
  "of adjacent-look displacement estimates, which has the spectrum of a random walk; the inversion is "
  "a discrete-time Fourier transform, so the reported depth in resolution cells is the peak of that "
  "transform, and removing a degree-2 polynomial leaves it near 1.7 cells. Accumulated Gaussian noise "
  "with <b>no SAR pipeline at all</b> reproduces both the fixed depth and the contrast scaling; at "
  "128 sub-apertures an input containing nothing returns more contrast than a real scene "
  "(274.85 against 128.64). <b>Fourth, neither of this paper&rsquo;s own decision criteria "
  "survives undisclosed preprocessing:</b> on an input containing no scene, a low-pass filter "
  "applied to each patch independently drives 97% of blocks past the 5&times; contrast threshold, "
  "a high-pass filter moves 100% of them out past the surface guard, and a five-tap kernel found "
  "by direct search does <b>both at once, reporting every one of 200 empty blocks as a detection "
  "under the full rule</b> &mdash; 98% of them even against a 95th-percentile null. A survey of "
  "137 operators found one marginal case at 2%; only optimisation exposed the failure. "
  "The results here are unaffected, because no such filter is applied and the chain is published; "
  "but it follows that a confidence figure attached to a tomogram is uninterpretable unless the "
  "whole preprocessing chain is disclosed, which is an argument against this paper&rsquo;s "
  "statistics as much as anyone&rsquo;s. "
  "Fifth, planting a displacement signature in the image before processing "
  "gives a detection floor of 0.2 pixels, 8.4&times; the pipeline&rsquo;s own noise, below which a "
  "scene containing a genuine reflector reports <i>lower</i> confidence than an empty one. I state "
  "plainly what I have not shown: of four attempts to reproduce the appearance of the published 3-D "
  "figures from empty volumes, three failed outright and the fourth is unresolved (&sect;7), so I do "
  "not claim those images are this artifact. This is a "
  "critique of method and mathematics, not of intent.", absst)
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
  "result (Figure 3) is a striking high-contrast band that <i>passes</i> a naive "
  "contrast-vs-null test as a detection. <b>The numerical contrast at this setting is not "
  "reported here.</b> It is a native, unfixed-window peak-to-median statistic evaluated on a "
  "depth axis whose extent grows with the sub-aperture count while the bin count stays fixed, "
  "so it is not comparable across settings and inflates without bound as that count is raised; "
  "see the withdrawal note in &sect;10.1. What matters is the qualitative outcome, which does not "
  "depend on the number: the entire feature is pinned at "
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
    "Figure 3. Reproduction on Butte, MT. Left: real tomogram &mdash; a confident "
    "band pinned at the surface. Centre: shuffled null. Right: documented workings (100-ft levels to "
    "457 m; water table ~160 m). The &lsquo;detection&rsquo; matches nothing real.", width=6.3*inch)

P("3.4 Every site returns the same artifact, including Giza and the authors&rsquo; own Vesuvius (addresses C4)", h2)
P("With the depth-of-peak and stability guards active, six free X-band sites across two independent "
  "sensors are each indistinguishable from their nulls, while in-data positive controls confirm the "
  "pipeline would surface a genuine signal. Mount Vesuvius is decisive because it is the "
  "authors&rsquo; own peer-reviewed site. The Capella scene matters separately: it reproduces the "
  "null on an <i>independent sensor</i>, so the result is a property of the method and not of one "
  "data provider &mdash; the very cross-sensor agreement cited as confirmation (C5) yields nulls once "
  "controls are applied. <b>The Giza plateau is now included</b>; it is analysed in full in "
  "&sect;4.")
tbl = [["Site", "Sensor", "Reg.", "Contrast", "Peak depth", "Pinned", "Detections"],
       ["Bingham Canyon", "Umbra", "0.67", "3.87", "2.5 - 3.7 m", "8/8", "0/8"],
       ["Komati Power Stn", "Umbra", "0.85", "2.76", "3.2 - 3.7 m", "8/8", "0/8"],
       ["Mount Vesuvius", "Umbra", "0.72", "4.11", "3.2 - 3.7 m", "8/8", "0/8"],
       ["Butte, MT", "Umbra", "0.82", "3.33", "3.2 - 3.9 m", "8/8", "0/8"],
       ["Cairo (central)", "Capella", "0.62", "2.75", "3.4 - 3.6 m", "8/8", "0/8"],
       ["<b>Giza plateau</b>", "Umbra", "0.68", "<b>6.06</b>", "<b>3.2 - 3.7 m</b>", "<b>8/8</b>", "<b>0/8</b>"]]
tbl = [[Paragraph(c, ParagraphStyle("tc", parent=body, fontSize=8.5, leading=10,
        alignment=TA_CENTER, spaceAfter=0)) for c in row] for row in tbl]
t = Table(tbl, colWidths=[1.25*inch, 0.72*inch, 0.55*inch, 0.72*inch, 1.0*inch, 0.68*inch, 0.85*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTNAME", (0,1), (-1,-1), "Times-Roman"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("BACKGROUND", (0,6), (-1,6), colors.HexColor("#f4f4f4")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(t)
P("Table 2. Six free single-pass X-band sites across two independent sensors. <i>Contrast</i> is the "
  "peak-to-median statistic at the pipeline default of 11 Doppler sub-apertures (512&times;512 centre "
  "crop, 64-pixel patches, 24 patches, 0.8 sub-band overlap, Hann taper, float64). <i>Peak depth</i> "
  "and <i>Pinned</i> span the full eight-point sub-aperture ladder (11 to 128) at each site; "
  "<i>Pinned</i> uses the absolute two-cell guard defined in &sect;5.5. <i>Detections</i> counts runs exceeding "
  "the 5&times; decision rule. <b>48 runs, 0 detections, every run surface-pinned.</b> Expressed in "
  "resolution cells the peak occupies 1.2&ndash;1.9 throughout.", cap)

P("<b>Two changes from earlier versions of this table, both of which strengthen the negative "
  "result.</b> The surface-pinning guard is now an absolute distance in resolution cells rather than "
  "a percentage of a depth axis whose length varies with the sub-aperture count; under the old rule "
  "14 of 40 runs were flagged, under the corrected rule 40 of 40 were, and every row of the "
  "originally published table sat in the regime where the old rule passed a ~1.5-cell peak as clear "
  "subsurface structure. And the <b>look-order shuffle null used in earlier versions is superseded</b>. "
  "Shuffling look order destroys the very look-to-look smoothness that the processing chain generates "
  "(&sect;5), so it is anti-conservative: it flatters this paper&rsquo;s own ratios. Against a null "
  "derived from the pipeline rather than shuffled, the excess at the default setting is approximately "
  "2%, and at 128 sub-apertures noise <i>exceeds</i> real data. The ratios printed in versions 1&ndash;4 "
  "(2.8&times;, 3.3&times;, 4.1&times;) should not be quoted as detection margins. The binary "
  "verdicts &mdash; no detection at any site &mdash; are unchanged, and are now measured against the "
  "harsher standard. <b>Both criteria have a limitation established in &sect;5.5</b>: on an input "
  "containing no scene, filters applied to each patch independently can drive the ratio past "
  "5&times;, move the peak out past the surface guard, or &mdash; for one kernel found by direct "
  "search &mdash; do both at once. The ratios and verdicts reported here stand because no such "
  "filter is applied and the chain is published in full, but they are conditional on that chain "
  "rather than robust to arbitrary preprocessing.")

P("<b>Corrections to individual rows.</b> The Bingham Canyon row read &ldquo;front-end only / no "
  "signal&rdquo; in versions 1&ndash;4; that is wrong, and the site produces a full surface-pinned "
  "tomogram at every sub-aperture count tested. The Komati ratio was stated as 2.15, computed from "
  "rounded inputs; unrounded it is 1.99. The Cairo (Capella) row previously carried an "
  "&ldquo;outstanding verification&rdquo; note; it has since been reproduced (2.75 against a "
  "published 2.8) and the note is withdrawn.")

P("<b>One parameter moves this table by a third, and no published source states it.</b> The "
  "sub-aperture window taper is given nowhere in the 2022 paper, the patent, or any presentation. On "
  "the Giza scene the contrast at the default setting is 6.06 under a Hann taper, 5.03 under a "
  "rectangular taper, 4.69 under Blackman and 4.52 under Hamming &mdash; a 34% spread from a choice "
  "the reader cannot audit. It joins the sub-aperture count, the sub-band overlap and the entire "
  "visualisation pipeline (&sect;7) on the list of undisclosed settings that move the headline number.")

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
P("4. The Giza plateau", h1)
P("The five sites in Table 2&rsquo;s first version were proxies, chosen for ground truth or sensor "
  "diversity. A reader was entitled to object that the site the claim is actually about had not been "
  "tested. It has now been. The scene is free Umbra Open Data over the Giza plateau, "
  "acquisition <font face=\"Courier\">2023-02-07-07-58-27_UMBRA-05</font>, collect "
  "<font face=\"Courier\">7e7cd796-3842-4923-8b48-4c0950ece945</font>, a 5674&times;5351 array with "
  "azimuth and range sample spacing of 0.827 m and 0.472 m, X-band, collect duration 1.27 s, scene "
  "centre 29.9793&deg;N 31.1340&deg;E.")

P("4.1 Predictions were published before the data were processed", h2)
P("To remove any suspicion that the analysis was tuned until it agreed with the other five sites, "
  "eight numerical predictions and four falsification conditions were committed to the public "
  "repository (commit <font face=\"Courier\">e4476d7</font>) while the scene was still downloading. "
  "They are reproduced here <i>with their misses</i>. The pre-registration nominated "
  "acquisition <font face=\"Courier\">2023-03-08-07-57-53_UMBRA-04</font> as primary and listed "
  "<font face=\"Courier\">2023-02-07-07-58-27_UMBRA-05</font> as the first of two within-site "
  "repeats. <b>The scene analysed here is that first repeat, not the nominated primary.</b> The "
  "reason is mundane and is recorded because the discrepancy would otherwise look unexplained: the "
  "predictions were committed <i>while the data were still downloading</i>, and the nominated "
  "primary is a <b>1.70 GB</b> product against <b>240 MB</b> for the repeat, so the repeat "
  "completed first and was analysed first. Both were subsequently downloaded. The pre-registration "
  "text was never edited &mdash; its result section was left deliberately empty at commit "
  "<font face=\"Courier\">e4476d7</font> and appended at <font face=\"Courier\">f6c1a90</font> "
  "&mdash; so the predictions were fixed before <i>any</i> Giza scene had finished arriving, which "
  "is a stronger condition than the protocol required.")
tbl = [["Prediction", "Result", "Outcome"],
       ["Peak depth 1.6 - 1.8 cells", "1.52 - 1.75", "<b>partial miss</b>"],
       ["Surface-pinned at every count", "8/8", "hit"],
       ["Detections above 5x", "0/8", "hit"],
       ["Contrast at n_sub = 11, order 3 - 5", "<b>6.06</b>", "<b>miss, high</b>"],
       ["Contrast at 128, order 10^2, at or below ~275", "108.90", "hit"],
       ["Fixed-window spread like other sites", "1.9x", "hit"]]
tbl = [[Paragraph(c, ParagraphStyle("tc2", parent=body, fontSize=8.5, leading=10, spaceAfter=0))
        for c in row] for row in tbl]
t = Table(tbl, colWidths=[3.0*inch, 1.5*inch, 1.3*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(t)
P("Table 3. The Giza run scored against predictions published before the data were processed. Two of "
  "six missed. <b>None of the four pre-registered falsification conditions was met</b>, but the "
  "misses are reported rather than absorbed: at 64 and 90 sub-apertures the peak sits at 1.52 cells, "
  "below the predicted floor, and the contrast at the default setting is the highest of any site in "
  "this study.", cap)

P("<b>Giza returns the highest raw contrast of the six sites, and it is still not a detection.</b> "
  "6.06 against Komati 2.76, Cairo 2.75, Butte 3.33, Bingham 3.87 and Vesuvius 4.11. Its "
  "alignment-referenced ratio, 3.67, is also the highest recorded here. It does not clear the "
  "5&times; rule against either null, the peak it produces is 1.75 cells beneath the surface, and it "
  "is surface-pinned &mdash; the same artifact, slightly louder. As &sect;3.4 notes, roughly a third "
  "of that excess is a window-taper choice: under Blackman the same scene gives 4.69.")

fig("tomogram_giza_2023-02-07_UMBRA-05_SICD.nitf.png",
    "Figure 5. Giza plateau, 11 sub-apertures. <b>Top left:</b> the real tomogram. <b>Top right:</b> "
    "the same data with look order shuffled &mdash; pure noise. The two are visually "
    "indistinguishable. <b>Bottom left:</b> the positive control, a synthetic reflector injected at "
    "relative depth 20, which produces a <i>continuous horizontal band across every patch at one "
    "depth</i> &mdash; what a coherent subsurface reflector looks like. The real panel contains "
    "nothing of the kind. <b>Bottom right:</b> tomogram power against surface brightness, correlation "
    "0.07 &mdash; the depth product is not surface-driven.", width=6.2*inch)

P("4.2 The surface is recovered; the depth is not", h2)
P("A natural objection to the figures in this paper is that they are cross-sections over 24 patches, "
  "whereas the published imagery is rendered in plan view over whole scenes, so the comparison is not "
  "like for like. To close that gap the pipeline was run in plan view over the entire 5674&times;5351 "
  "array &mdash; 462 tiles covering the plateau, the pyramid field and Giza city.")
fig("planview_giza_2023-02-07_UMBRA-05.png",
    "Figure 6. Plan view over the whole Giza scene, 462 tiles. <b>Top left:</b> surface brightness &mdash; "
    "the plateau, the city and the linear features are plainly visible; the front end sees Giza "
    "perfectly well. <b>Top centre and right:</b> tomogram power at the artifact depth and at a "
    "deeper slice. Both are salt-and-pepper with no morphology whatsoever. Correlation between "
    "surface brightness and depth power is &minus;0.180 and &minus;0.162 &mdash; slightly negative, "
    "not merely absent.", width=6.3*inch)
P("The consequence is narrow and worth stating precisely. A faithful reproduction of the published "
  "method produces depth products containing <i>zero</i> surface morphology. Whatever the published "
  "3-D figures are showing, this pipeline does not generate recognisable structure in a depth slice.")

P("5. The mechanism", h1)
P("<b>This section is the present account, not a settled result.</b> Two earlier mechanism "
  "explanations were proposed and withdrawn (&sect;10). This one rests on matched controls and a "
  "reproduction that removes the SAR front end entirely, which is a different class of evidence, but "
  "one of its own predictions fails at Giza and that failure is reported in &sect;5.4.")

P("5.1 The trajectory is a running total, and a running total of noise is a random walk", h2)
P("The per-patch trajectory is built by estimating displacement between <i>adjacent</i> looks and "
  "accumulating the increments &mdash; in the reference implementation, literally "
  "<font face=\"Courier\">np.cumsum(inc)</font>. A running total of noisy increments has the "
  "spectrum of a random walk: smooth by construction, strongly autocorrelated, irrespective of scene "
  "content. This holds at <i>any</i> sub-band overlap, including zero: at overlap 0.00 the trajectory "
  "still shows lag-1 autocorrelation of 0.447 and the peak still lands at 1.73 cells. Overlap "
  "amplifies the contrast but does not create the feature.")

P("5.2 The inversion is a Fourier transform, so the reported depth is a frequency", h2)
P("The steering matrix builds <font face=\"Courier\">Kz[j] = j &middot; 2&pi;/(L &middot; "
  "&Delta;z)</font> and the inverter computes <font face=\"Courier\">|A&#7448; &middot; "
  "analytic(r)|&sup2;</font>. That inner product is a discrete-time Fourier transform of the analytic "
  "residual, evaluated on the depth grid; direct evaluation agrees with the reference implementation "
  "to one part in 10&sup1;&#8309;, measured over 80 trials at four sub-aperture counts "
  "(<font face=\"Courier\">src/verify_claims.py</font>). The reported depth in resolution cells is therefore the peak of "
  "that transform in cycles per record. <b>This is a coordinate identity, not a recovery theorem.</b> "
  "It explains why a fixed feature occupies a fixed fraction of an axis whose extent is proportional "
  "to the number of looks, with no assumption about the ground.")

P("5.3 The depth is set by the detrending order, and can be reproduced with no satellite data", h2)
P("Removing a degree-2 polynomial from a series with the spectrum of a random walk leaves the peak at "
  "a position fixed by the polynomial order. On pure synthetic walks &mdash; no image, no "
  "sub-apertures, no overlap, no coregistration &mdash; the peak sits at <b>1.69 &plusmn; 0.02 "
  "resolution cells at every series length from 11 to 128</b>, a twelvefold range, and moves to 0.88 "
  "cells at degree 0 and 2.5 cells at degree 4. Real sites land in a 1.2&ndash;1.9 band. <b>The "
  "algebra that yields 1.69 rather than the textbook 1.5 predicted by a polynomial high-pass rule of "
  "thumb is not closed</b>, and is reported here as an open problem rather than a derivation.")
P("The same construction reproduces the second signature of the method. Contrast rises "
  "<b>72.9&times;</b> as the accumulated series lengthens from 11 to 128 samples, while the "
  "increments of the same series stay flat at 1.1&times;. Pushed through the full SAR pipeline, an "
  "image containing nothing returns a contrast of <b>274.85</b> at 128 sub-apertures against "
  "<b>128.64</b> for the Bingham Canyon scene &mdash; and the most dramatic figure in this study, "
  "Cairo at 272.52, is reproduced to within 1% by an input with no scene in it. Substituting the "
  "white synthetic image for speckle carrying the correct resolution-cell correlation, measured from "
  "the real scene, does not change the picture at the default setting: the synthetic returns 4.14 "
  "against the real scene&rsquo;s 3.87.")

P("5.4 A prediction of this account fails at Giza, and is reported as open", h2)
P("The decisive control removes only the running total, leaving series length and the steering matrix "
  "identical, so the sole difference between arms is the accumulation. At Bingham Canyon it moves the "
  "peak off the surface (1.66 &rarr; 2.83 cells) and at Cairo/Capella likewise (1.69 &rarr; 4.76), "
  "collapsing contrast in both. <b>At Giza it does not.</b> Contrast collapses as expected "
  "(6.06 &rarr; 1.86) and the look-to-look correlation collapses (0.547 &rarr; 0.087), but the peak "
  "moves only 1.75 &rarr; 1.88 cells and remains inside the guard. Giza&rsquo;s increments retain a "
  "weak positive autocorrelation, +0.087, where noise increments give &minus;0.041.")
P("Two candidate explanations were tested and both failed: coregistration quality at Giza is "
  "unremarkable (0.68, against 0.62 to 0.85 elsewhere), and surface-brightness leakage is 0.07 within "
  "the analysis crop and &minus;0.180 across the full scene. <b>I do not have a third explanation and "
  "am not offering one.</b> The accumulation is therefore <i>sufficient</i> to generate the artifact "
  "&mdash; the synthetic-walk reproduction stands independently &mdash; but is <b>not shown to be "
  "necessary</b> for the surface-pinning at the site in this paper&rsquo;s title. The published "
  "operator remains surface-pinned at Giza with no detection.")

P("5.5 Neither decision criterion survives undisclosed per-patch filtering", h2)
P("Every verdict in this paper rests on two criteria applied together: <b>(a)</b> contrast above "
  "five times the alignment null, and <b>(b)</b> a peak within two resolution cells of the surface. "
  "Criterion (a) is the kind of confidence figure the published work reports; criterion (b) is this "
  "paper&rsquo;s addition. This subsection reports that <b>neither is safe</b>, and what does and "
  "does not follow from that.")
P("The alignment null preserves each patch&rsquo;s depth profile exactly and randomises only whether "
  "patches <i>agree</i> on a depth (&sect;3.4), so it is invariant to <i>where</i> each patch peaks. "
  "The inversion is a discrete-time Fourier transform (&sect;5.2), so reported depth in cells <i>is</i> "
  "a frequency. Those two facts together make the criteria attackable in opposite directions by "
  "filters acting on each patch <b>independently</b>, transferring no information between patches.")

P("The tests below use an input containing <b>no scene</b> &mdash; band-limited complex noise, no "
  "satellite data &mdash; tiled through the identical pipeline and drawn into independent 24-patch "
  "blocks, the analysis geometry used for every site in Table 2.")

tbl = [["Per-patch operator, empty input", "Ratio", "Peak (cells)", "Clears 5&times;", "Unpinned", "<b>False detections</b>"],
       ["None &mdash; the pipeline as run everywhere in this paper", "2.45", "1.73", "0%", "0%", "<b>0%</b>"],
       ["The authors&rsquo; low-rank denoising step", "3.49", "1.71", "9%", "0%", "<b>0%</b>"],
       ["<b>Low-pass</b> [1,2,1]/4 &mdash; defeats (a) only", "7.71", "1.67", "<b>97%</b>", "0%", "<b>0%</b>"],
       ["<b>High-pass</b> [1,&minus;2,1]/4 &mdash; defeats (b) only", "1.28", "<b>4.21</b>", "0%", "<b>100%</b>", "<b>0%</b>"],
       ["<b>Searched kernel [&minus;0.169, +0.159, &minus;0.312, +0.182, &minus;0.178]</b>",
        "<b>12.52</b>", "<b>4.97</b>", "<b>100%</b>", "<b>100%</b>", "<b>100%</b>"]]
tbl = [[Paragraph(c, ParagraphStyle("tc5", parent=body, fontSize=8.5, leading=10, spaceAfter=0))
        for c in row] for row in tbl]
t = Table(tbl, colWidths=[2.5*inch, 0.6*inch, 0.85*inch, 0.75*inch, 0.7*inch, 0.85*inch])
t.repeatRows = 1
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("BACKGROUND", (0,5), (-1,5), colors.HexColor("#f4f4f4")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(t)
P("Table 4. Per-patch operators against this paper&rsquo;s own decision rule, on an input containing "
  "no scene. All rows from one run: 200 blocks of 24 patches, 64 null permutations, guard 2.0 cells, "
  "seed 4242 (<font face=\"Courier\">src/guard_confirm.py</font>). A "
  "low-pass filter defeats criterion (a) while pinning the peak harder; a high-pass filter defeats "
  "criterion (b) while the ratio collapses; <b>a five-tap kernel found by direct search defeats "
  "both at once, reporting every one of 200 empty blocks as a detection under the full rule.</b>", cap)

fig("guard_confirm.png",
    "Figure 7. Both decision criteria on an input containing no scene. <b>Left:</b> the contrast "
    "rule &mdash; a low-pass filter clears it, a high-pass filter does not. <b>Right:</b> the depth "
    "guard &mdash; the high-pass filter escapes it, the low-pass filter does not. The outlined bar "
    "is the kernel found by direct search, which clears both in 200 of 200 blocks.", width=6.3*inch)

P("<b>The two criteria are in tension, which is why a survey nearly missed this.</b> Because depth "
  "in cells is a frequency, moving the peak past the guard requires shifting spectral energy upward, "
  "and high-frequency content in accumulated noise is patch-specific &mdash; so patches stop agreeing "
  "and the ratio collapses. Conversely, raising the ratio requires concentrating energy in the "
  "low-frequency mode patches <i>share</i>, which pins the peak harder. Across 137 hand-chosen and "
  "randomly drawn operators the median ratio and median peak depth correlate at <b>&minus;0.379</b>; "
  "the 17 operators that clear 5&times; have mean peak depth 1.58 cells against 2.19 for the 120 that "
  "do not. <b>The survey found exactly one operator producing any false detection, at 2%</b>, which "
  "reads as noise. Only a direct optimisation against the joint objective &mdash; 4,000 screened "
  "kernels followed by hill-climbing &mdash; found the region where the rule fails completely. "
  "<b>A broad survey returning nothing is therefore not evidence of safety</b>, and this paper very "
  "nearly drew that conclusion from one.")
P("A more conservative null does not repair it. Scoring against the <b>95th percentile</b> of the "
  "alignment null rather than its median takes the low-pass filter from 97% of empty blocks above "
  "threshold to 50%, and leaves the searched kernel at <b>98% false detections</b>. Hardening the "
  "threshold does not help against an operator selected to beat it.")
P("<b>What follows, and what does not.</b> The results reported in this paper are unaffected: no "
  "per-patch filter of any kind is applied anywhere in this pipeline, the processing chain is fully "
  "specified, and every setting is published and re-runnable. Tables 2 and 3 stand <i>for the "
  "disclosed chain</i>. What cannot be claimed &mdash; and was claimed in an earlier draft of this "
  "section &mdash; is that the depth guard makes the rule robust. It does not.")
P("The general conclusion is the one that matters, and it cuts against this paper as much as against "
  "the work it examines: <b>a confidence figure attached to a tomogram is uninterpretable unless the "
  "entire preprocessing chain is disclosed.</b> Four taps applied to each patch independently, adding "
  "no information whatever, are enough to manufacture detections from an empty input under both "
  "criteria simultaneously. No decision procedure of this form can be validated against an "
  "undocumented pipeline &mdash; not this paper&rsquo;s, and not any other&rsquo;s. That is the "
  "strongest available argument for disclosure, and it is why the sub-aperture count, sub-band "
  "overlap, window taper, denoising parameter and rendering settings of the published work are "
  "requested in &sect;9 as a precondition for evaluating it rather than as a courtesy.")

P("Two limitations of this experiment are stated plainly. It uses <b>synthetic input only</b>; real "
  "scenes carry surface texture and residual phase that may interact with these operators differently, "
  "and no real-scene arm has been run. And the operator family searched is <b>linear, per-patch and "
  "finite-impulse-response of length at most five</b> &mdash; no claim is made about nonlinear or "
  "longer operators, which may be worse.")
P("<b>Correction.</b> The first version of this experiment applied its filters with an off-centre "
  "edge-padding convention that delayed the output by one sample on an eleven-sample record. Two "
  "nominally identical [1,2,1]/4 arms consequently disagreed (median ratio 5.97 against 7.70). The "
  "convention was corrected to a centred one, every arm re-run, and the numbers above are the "
  "corrected values. The correction made the result <i>stronger</i> &mdash; the searched kernel moved "
  "from 36% false detections to 100% &mdash; which is recorded here because it would have been "
  "convenient not to check.")
P("Separately, and reported for completeness rather than as evidence: forcing the retained rank of "
  "the patch-by-look matrix down concentrates the depths patches report &mdash; 79 to 80 distinct "
  "depth bins of 300 at rank 3 against 155 to 209 untruncated, and at rank 1 every patch returns the "
  "same depth, which is an algebraic identity. Pure synthetic random walks with no image, no "
  "sub-apertures and no pipeline of any kind reproduce the sweep to within a few bins in 300 at every "
  "rank (1, 19, 78, 141, 208 against 1, 19, 80, 145, 209), so it is a property of "
  "accumulate-and-detrend and extends &sect;5.3 rather than adding independent evidence.")

P("6. How large a real signal would have to be", h1)
P("A control that injects a signal into the trajectory <i>after</i> accumulation and detrending "
  "demonstrates only that the inverter can recover a tone written in its own coordinates. A stronger "
  "test plants the displacement in the image itself, before sub-aperture decomposition, so that the "
  "signature must be recovered by the pipeline&rsquo;s own estimator, from speckle, through the "
  "window taper, before it is accumulated and inverted.")
tbl = [["Planted displacement", "x pipeline noise", "Peak (cells)", "Contrast", "Target found"],
       ["none", "0", "1.75", "<b>6.06</b>", "0%"],
       ["0.02 px", "0.8", "1.75", "6.06", "0%"],
       ["0.05 px", "2.1", "1.75", "4.69", "0%"],
       ["0.10 px", "4.2", "1.73", "<b>3.39</b>", "0%"],
       ["<b>0.20 px</b>", "<b>8.4</b>", "<b>3.16</b>", "5.40", "<b>100%</b>"],
       ["0.50 px", "21.1", "3.18", "13.69", "100%"]]
tbl = [[Paragraph(c, ParagraphStyle("tc3", parent=body, fontSize=8.5, leading=10,
        alignment=TA_CENTER, spaceAfter=0)) for c in row] for row in tbl]
t = Table(tbl, colWidths=[1.5*inch, 1.15*inch, 1.0*inch, 0.95*inch, 1.05*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Times-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8e8e8")),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#888888")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 2.5), ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)]))
story.append(t)
P("Table 5. A reflector planted at 3.30 cells in the Giza scene before processing. The "
  "pipeline&rsquo;s own unplanted trajectory RMS is 0.02372 px, and amplitudes are given as multiples "
  "of it. The detection floor is 0.2 px, 8.4&times; the noise.", cap)
P("<b>Below the floor the statistic runs backwards.</b> A scene containing a genuine reflector at "
  "4.2&times; the noise floor reports a contrast of 3.39 &mdash; <i>lower</i> than the 6.06 reported "
  "for a scene containing nothing at all. Over precisely the range in which a real archaeological "
  "feature would sit, the method is not merely blind: its confidence is anti-correlated with truth. "
  "A separate measurement shows the front end passes only about 12% of a sub-pixel displacement "
  "through to the trajectory, so a real signal is attenuated roughly eightfold before it competes "
  "with an artifact generated at full strength.")
P("Converting 0.2 px into physical ground motion is <b>not</b> a multiplication by the 0.827 m "
  "azimuth spacing. In SAR a target moving during the collect is displaced in azimuth by "
  "approximately (R/V)&middot;v, so the image shift maps to a line-of-sight <i>velocity</i>, not a "
  "displacement. That conversion is not attempted here and no figure in metres of ground motion is "
  "claimed.")

P("7. What could not be reproduced", h1)
P("The public impact of this work is visual: renderings in which shaft-like and chamber-like forms "
  "appear beneath the plateau. Four attempts were made to reproduce that <i>appearance</i> from "
  "volumes containing no scene at all &mdash; a voxel scatter and an isosurface rendering at 11 "
  "sub-apertures, and an isosurface at 128. They produce, respectively, vertical needles at a "
  "single depth, discrete solid bodies in a shallow slab, and a continuous planar sheet spanning "
  "the whole site. None resembles the published figures: no shafts, no vertical extent, no spirals, "
  "no architecture. <b>A fourth treatment, added after those three, does change this picture and "
  "is reported here unresolved.</b> Subtracting the depth profile common to every tile &mdash; the "
  "natural operation for seeing past a surface return, and one an analyst would plausibly apply "
  "&mdash; produces discrete, vertically elongated bodies spread over 60% of the depth axis, with "
  "a median vertical run of 36 bins in 300, from a volume built entirely from random numbers. "
  "<b>Whether those resemble the published figures is at present an aesthetic judgement, and this "
  "paper declines to make it.</b> A shape statistic has now been fixed in advance, and the first "
  "attempt at it failed in a way worth recording. An <i>absolute</i> threshold, calibrated on "
  "synthetic controls &mdash; isotropically smoothed noise as the negative, synthetic shafts and "
  "chambers as the positive &mdash; separated those two perfectly, then classified <b>9 of 12 "
  "renderings of an empty volume as architecture-like, including the raw volume with no rendering "
  "applied at all</b>. The calibration was against the wrong null: the depth axis is a "
  "discrete-time Fourier transform of a smooth accumulated trajectory (&sect;5.2), so every "
  "profile is smooth in depth <i>by construction</i> and above-threshold voxels form long vertical "
  "runs whether or not anything is there. <b>This is the finding of &sect;5.5 turned on this paper "
  "a second time: an absolute threshold is not a detection rule.</b> Corrected to a matched "
  "design &mdash; median vertical run and connected-component count scored against a "
  "pipeline-matched volume from an input containing no scene, under the identical treatment "
  "&mdash; the statistic separates a volume with planted shafts from an empty one in 8 of 12 "
  "treatments, by 4 to 5&times; on vertical run and 7 to 13&times; on component count; the four "
  "that do not separate are excluded in advance. The rule and its calibration are committed at "
  "<font face=\"Courier\">docs/PREREGISTRATION_MINES_AND_GRANSASSO.md</font> &sect;C. Applying "
  "it to the real Giza volume requires that scene and has not yet been run, so the negative claim "
  "in this section remains <b>provisional</b>. Parameter "
  "tuning was stopped at that point because continuing would have been fitting.")
fig("volume_noise_iso.png",
    "Figure 8. Three-dimensional isosurface rendering of a volume built from band-limited complex "
    "noise &mdash; no satellite data, no scene, no ground &mdash; through the identical pipeline, at "
    "three thresholds. Discrete solid bodies in a shallow slab. This is what the artifact looks like "
    "rendered in three dimensions, and it is <i>not</i> what the published figures look like.",
    width=6.3*inch)
P("<b>I therefore do not claim that the published imagery is nothing but this artifact.</b> That "
  "claim appeared in versions 1&ndash;3 of this preprint and was withdrawn in v4 precisely because "
  "the test of it failed. What is supported is narrower and independent: the 2022 paper documents no "
  "part of its visualisation pipeline &mdash; no renderer, isosurface, threshold, dynamic range, "
  "colour scale, denoising step or stacking count. Its 3-D figures carry a single repeated caption "
  "pairing a CAD model with a tomographic magnitude. Those figures are not reproducible even in "
  "principle, which places them alongside the undisclosed sub-aperture count, sub-band overlap and "
  "window taper.")

P("8. Robustness: could a wrong velocity model hide a real signal?", h1)
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
P("9. What is real, and what would change my conclusion", h1)
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
P("10. Revision history, corrections and withdrawals", h1)
P("This preprint has been revised four times, and three of those revisions corrected errors in it. "
  "That history is set out in full here rather than left for a reader to reconstruct. Disclosed, it "
  "is a record of process; discovered, it would be a liability.")

P("10.1 Errors found and corrected", h2)
P("<b>The Komati row (v3, July 2026).</b> The row read &ldquo;50&times; / 10&times;, null&rdquo; in "
  "v2. It had been computed at 128 sub-apertures rather than the default 11 used for every other row, "
  "and its verdict label was wrong for that setting. Re-run at the default it gives 2.76 / 1.39. The "
  "correction <i>increases</i> the margin, because 50/10 is a ratio of exactly 5.0 and sat precisely "
  "on this paper&rsquo;s own decision rule. The error was found while stress-testing against an "
  "external methodological objection, and was reported to the recommender unprompted. The corrected "
  "ratio was then stated as 2.15 from rounded inputs; the recorded value is 2.05.")
P("<b>The 1720&times; figure (v4, August 2026).</b> Versions 1&ndash;3 quoted the Butte reproduction "
  "as a &ldquo;1720&times; detection&rdquo; in the abstract, &sect;3.3 and the conclusion. "
  "<b>Withdrawn.</b> It is a native, unfixed-window peak-to-median contrast computed at 256 "
  "sub-apertures; because the depth axis is built as "
  "<font face=\"Courier\">linspace(0, n_sub&middot;&Delta;z/2, 300)</font> its extent grows with the "
  "sub-aperture count while the bin count stays fixed, so the statistic is not comparable across "
  "settings. An earlier &ldquo;194&times;&rdquo; claim had already been withdrawn on exactly this "
  "ground and the correction was not carried through. The qualitative result is unchanged.")
P("<b>The rendered-geometry claim (v4).</b> Versions 1&ndash;3 concluded that the Giza "
  "&ldquo;shafts&rdquo;, &ldquo;spirals&rdquo; and &ldquo;chambers&rdquo; <i>are</i> the rendered "
  "geometry of this artifact. <b>Withdrawn</b>, for the reason given in &sect;7: the test of it "
  "failed.")
P("<b>The look-shuffle null (v5).</b> Every ratio in Table 2 in versions 1&ndash;4 was measured "
  "against a null this paper now regards as anti-conservative, in a direction that flattered its own "
  "conclusion. See &sect;3.4.")

P("10.2 Explanations proposed and abandoned", h2)
P("Three accounts of the mechanism have been advanced. The first &mdash; that the inverter produces "
  "the peak from nothing &mdash; was asserted before any null existed and was withdrawn once one was "
  "built. The second &mdash; that 80% sub-aperture overlap manufactures the peak &mdash; survived one "
  "experiment and died on the next, which found the peak present at <i>zero</i> overlap. The third is "
  "the account in &sect;5, and it differs from its predecessors in resting on matched controls and a "
  "reproduction with the SAR front end removed, rather than on inference from invariance. It also has "
  "a failed prediction of its own, at Giza, reported in &sect;5.4. Both abandoned accounts died "
  "because the null was built more carefully, which is the same failure this paper identifies in the "
  "work it examines.")

P("10.3 Defects in this paper&rsquo;s own analysis code", h2)
P("Three automated verdict messages in the research code printed conclusions their own data did not "
  "support: one hard-coded the overlap explanation and never examined the zero-overlap row; one "
  "described a peak <i>bin</i> as independent of series length when the bins span 4 to 48 and the "
  "invariant is the depth in resolution cells; and one announced that removing the cumulative sum "
  "moves the peak off the surface, which is false at Giza. All three have been corrected to read the "
  "data before printing, and are recorded here because a reader who runs this code should know that "
  "its console output was, in three places, written to state the preferred answer.")

P("10.4 What remains open", h2)
P("The constant that fixes the artifact depth at 1.69 rather than the textbook 1.5 cells is not "
  "derived. The contrast statistic has not been characterised analytically under strongly "
  "autocorrelated inputs; its behaviour is measured across a twelvefold range of series lengths, "
  "which is weaker than a derivation. The Giza increments anomaly of &sect;5.4 has no explanation. "
  "Two further Giza acquisitions have been obtained and not yet analysed, so the pre-registered "
  "within-site repeatability test is untested. The &sect;5.5 attack was obtained on "
  "synthetic input only and searched only linear per-patch filters of length at most five; longer "
  "or nonlinear operators are not characterised and may be worse. <b>No filter-invariant "
  "replacement for either criterion is proposed here, and finding one is the single most useful "
  "thing a reader could contribute.</b> The &sect;7 imagery question is open and its negative claim "
  "provisional. All sites are X-band spotlight; nothing here bears on "
  "C-band or L-band. And this preprint has not been peer reviewed.")

P("11. Conclusion", h1)
P("Reproduced from the authors&rsquo; own method and patent, with each disclosed step mapped to its "
  "implementation, single-source SAR Doppler micro-motion tomography yields no reproducible evidence "
  "of deep subsurface structure, and the confident outputs it does produce are reproducible as "
  "artifacts.")
P("The reported depth in metres is exactly proportional to an investigation frequency chosen by the "
  "analyst rather than measured; the frequency never enters the inversion. Across six sites, two "
  "independent sensors, eight sub-aperture counts and thirteen patch geometries &mdash; 48 runs "
  "&mdash; the method returns the same surface-pinned feature at 1.2 to 1.9 resolution cells and not "
  "one detection. That includes the Giza plateau itself, run against predictions published before the "
  "data were processed, and the authors&rsquo; own Vesuvius. The mechanism is identified: the "
  "trajectory is a running total, which has the spectrum of a random walk; the inversion is a Fourier "
  "transform, so the reported depth is a frequency; and a degree-2 detrend fixes that frequency near "
  "1.7 cells. Accumulated Gaussian noise with no SAR pipeline at all reproduces both signatures, and "
  "at 128 sub-apertures an input containing nothing returns more contrast than a real scene. Planting "
  "a signal in the image before processing shows that below 8.4 times the pipeline&rsquo;s own noise "
  "a scene containing a real reflector reports <i>lower</i> confidence than an empty one.")
P("I do not claim the published three-dimensional imagery is nothing but this artifact. Four "
  "attempts to reproduce its appearance from empty volumes did not settle the question, and "
  "&sect;7 reports the fourth as unresolved rather than closed. Nor do I offer the statistics "
  "here as detection margins: &sect;5.5 shows that both of this paper&rsquo;s decision criteria "
  "can be defeated on empty data by filters that carry no information, one kernel defeating both "
  "at once. The verdicts stand for the chain actually run and published, and are conditional on "
  "it. That conditionality is general, and it is the reason the undisclosed settings of the work "
  "examined here matter: a confidence figure cannot be evaluated against a pipeline nobody can "
  "see. I do not claim that accumulating displacements is the wrong operation, nor that nothing "
  "lies beneath any of these sites. The measurement front end is real and remains valuable for "
  "surface-deformation monitoring. What fails reproduction and controls is the deep inference, and "
  "the specific defect is located, testable, and reproducible from the repository in minutes.")
P("The 2022 article was retracted by <i>Remote Sensing</i> on 10 August 2026 for &ldquo;serious "
  "methodological flaws and statistical errors&rdquo;, without specifying them. I did not contact the "
  "journal and make no claim to have prompted that decision. This paper is offered as a "
  "reproducibility result &mdash; openly testable, falsifiable from the repository, and framed as a "
  "critique of method and mathematics, not of intent. I continue to welcome the decisive ground-truth "
  "experiment.")

P("Data and code availability", h1)
P("All scenes are free Umbra Open Data and Capella Open Data (CC-BY 4.0); the exact scene "
  "identifiers and acquisition parameters are listed in the repository. The full reproduction "
  "pipeline, the controls, the stress tests (including the frequency-relabelling and surface-pinning "
  "demonstrations), and the scripts that regenerate every figure in this paper are openly available at "
  "https://github.com/Hassanforeman/subsurface-sar-tomo (archived at Zenodo, DOI 10.5281/zenodo.21065675), with "
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
    "Remote Sensing 14(20):5231. arXiv:2208.00811. "
    "<b>RETRACTED 10 August 2026</b> &mdash; retraction notice Remote Sensing (2026) 18, 2679, "
    "doi.org/10.3390/rs18162679, citing &ldquo;serious methodological flaws and statistical "
    "errors&rdquo; without specifying them.",
    "Pomposi, S. (2026). Independent Reproduction Attempt of SAR Doppler Tomography for Subsurface "
    "Imaging of the Great Pyramid of Giza. Zenodo, 10.5281/zenodo.19574701, 14 April 2026. "
    "An independent critique reaching a negative conclusion by a different route &mdash; a geometric "
    "argument that single-pass Doppler sub-apertures give an elevation resolution of order 285 m, "
    "with a Giza-versus-desert parameter sweep finding no target-specific discrimination. It "
    "predates this work and is cited here as independent corroboration.",
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
P("<i>Preprint, August 2026. Author: Hassan Foreman. A critique of method and mathematics, openly "
  "reproducible and falsifiable; not an allegation of intent.</i>", cap)

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="Refutation — Giza SAR Doppler Tomography", author=AUTHOR)
doc.build(story)
print("wrote", OUT)
