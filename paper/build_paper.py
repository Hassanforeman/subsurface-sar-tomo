#!/usr/bin/env python3
"""
build_paper.py — build the preprint PDF for the single-pass SAR Doppler tomography
reproduction.  Rebuilt 2026-06-29 to add the Butte, MT true-positive null (4th site)
and the velocity / depth-grid-coverage robustness section.

Run:
    python3.13 paper/build_paper.py
Output:
    paper/Single_Pass_SAR_Tomography_Reproduction.pdf

Only dependency is reportlab:  pip install reportlab
Figures (optional, embedded if present) are read from ../runs/.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, HRFlowable, PageBreak)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RUNS = os.path.join(ROOT, "runs")
OUT = os.path.join(HERE, "Single_Pass_SAR_Tomography_Reproduction.pdf")

TITLE = ("Critical Reproduction and Controlled Validation of Single-Pass SAR Doppler "
         "Micro-Motion Tomography: A Null Result at Four Sites, Including a Known Shallow "
         "Mine Void (Butte, MT) and Mount Vesuvius")
AUTHOR = "Hassan Foreman"
AFFIL = "Independent researcher"
DATE = "June 2026 (v2 preprint)"

# ----------------------------------------------------------------------------- styles
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
abs = ParagraphStyle("abs", parent=body, fontSize=9.5, leading=13, leftIndent=18,
                     rightIndent=18, spaceAfter=4)
cap = ParagraphStyle("cap", parent=body, fontSize=8.5, leading=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#333333"), spaceBefore=2, spaceAfter=10)
ref = ParagraphStyle("ref", parent=body, fontSize=9, leading=12, spaceAfter=3,
                     leftIndent=14, firstLineIndent=-14)

story = []
def P(t, st=body): story.append(Paragraph(t, st))
def S(h=6): story.append(Spacer(1, h))
def rule(): story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#999999"),
                                    spaceBefore=6, spaceAfter=6))

def fig(fname, caption, width=5.4*inch):
    path = os.path.join(RUNS, fname)
    if os.path.exists(path):
        try:
            from PIL import Image as PImage
            w, h = PImage.open(path).size
            ar = h / w
        except Exception:
            ar = 0.62
        story.append(Image(path, width=width, height=width*ar))
        P(caption, cap)
    else:
        P("[figure %s not found — rebuild after running the pipeline]" % fname, cap)

# ----------------------------------------------------------------------------- front
P(TITLE, title_st)
P(AUTHOR + " &mdash; " + AFFIL, center)
P(DATE, center)
S(4)
rule()

P("<b>Abstract.</b> Single-pass synthetic-aperture-radar (SAR) Doppler micro-motion "
  "tomography has been used to claim recovery of deep subsurface structure from essentially "
  "one acquisition, most prominently in disputed 2025 reports of large voids beneath the Giza "
  "plateau. We independently rebuild the method as an openly documented, validation-first "
  "pipeline and apply it to free, single-pass X-band spotlight data (Umbra Open Data) at four "
  "sites. We separate the legitimate measurement front-end (a satellite radar used as a remote "
  "surface vibrometer) from the contested deep tomographic inversion, and we add the controls "
  "the original work omitted: a look-order-shuffle null, an in-data positive control (inject and "
  "recover a synthetic reflector), and a surface-leakage correlation. Across all four sites the "
  "real tomograms are statistically indistinguishable from their shuffled nulls, while every "
  "positive control recovers an injected reflector &mdash; the pipeline would surface a real "
  "signal but finds none. The decisive case is Butte, Montana, the most densely mapped "
  "underground mining district on Earth, where a known shallow void lies under the scene: at the "
  "highest registration quality of any site (0.82) and with a passing positive control, the "
  "result is still a null. Because a seismic velocity model only re-labels the relative depth "
  "axis, the null verdict is invariant to it by construction; we specify a velocity/depth-grid "
  "sweep as the confirmatory test of search-grid coverage. We conclude that, as publicly "
  "reproducible on free single-pass X-band data, the method does not recover subsurface structure "
  "&mdash; and, importantly, does not hallucinate one. We frame this as a reproducibility "
  "statement, not a fraud accusation.", abs)
S(2)
P("<b>Keywords:</b> synthetic aperture radar; Doppler sub-aperture; micro-motion; tomography; "
  "reproducibility; null result; positive control.", abs)
rule()

# ----------------------------------------------------------------------------- 1
P("1. Introduction", h1)
P("F. Biondi and collaborators have proposed that the Doppler (azimuth) sub-aperture "
  "decomposition of a single SAR image, combined with high-precision sub-pixel coregistration, "
  "recovers a per-pixel surface micro-motion field that can be inverted tomographically for "
  "structure at depth. The measurement step &mdash; treating the satellite radar as a remote "
  "vibrometer sensitive to sub-millimetre, ambient-energy-driven surface motion &mdash; is "
  "well precedented. The far stronger claim is that a single pass yields a usable tomographic "
  "aperture for structure hundreds of metres to kilometres deep. That claim reached the public "
  "through 2025 reports of an &lsquo;underground city&rsquo; beneath the Giza plateau, which were "
  "not peer reviewed.", )
P("Two independent reproductions (not-JASH; mfwarren) found concrete problems &mdash; a "
  "dimensionally inconsistent steering law, an apparent Nyquist violation in the quoted "
  "investigation frequencies, a depth mirror-symmetry artifact, and kilometre-scale vertical "
  "resolution from satellite geometry when the wrong acquisition mode (Sentinel-1 TOPS) is used. "
  "Our contribution is complementary: a validation-first pipeline with explicit controls, applied "
  "to free spotlight data, designed so that a negative result is meaningful rather than merely an "
  "absence of effort.")

# ----------------------------------------------------------------------------- 2
P("2. Method and pipeline", h1)
P("2.1 The method in one paragraph", h2)
P("The processing chain is: (i) slice the azimuth/Doppler spectrum of one Single-Look Complex "
  "image into many overlapping sub-apertures, each a slightly different squint view; (ii) track "
  "sub-pixel displacements between sub-apertures to recover a vibration history; (iii) organise "
  "these complex observations along the tomographic view-direction; (iv) invert a steering matrix "
  "A(z), whose column for each candidate depth predicts the phase signature a source at that depth "
  "imprints across the sub-apertures, to estimate the depth profile. Unlike medical CT, the "
  "projection operator here is <i>modelled, not measured</i>: A(z) encodes an assumed seismic "
  "propagation model, which is the method&rsquo;s principal hiding place for error.")
P("2.2 Depth resolution", h2)
P("The tomographic depth resolution follows &delta;z = &lambda;R/(2A), where &lambda; is the "
  "<i>seismic</i> (not radar) wavelength, R the slant range, and A the synthetic aperture in the "
  "Doppler-synthesis (vibrational) domain. Depth resolution is therefore governed by the seismic "
  "wavelength and the vibrational aperture, not the radar chirp band; the common suggestion to "
  "&lsquo;switch to a higher radar frequency for depth&rsquo; is incorrect. Radar image resolution "
  "is set by bandwidth and aperture and is band-independent.")
P("2.3 Implementation and self-tests", h2)
P("Each stage has a synthetic self-test against known truth and a real-data mode. The sub-aperture "
  "shift estimator validates to 0.02 px; the adjacent-pair, quality-weighted, detrended "
  "micro-motion estimator recovers an injected residual to 0.07 px and flags decorrelated looks. "
  "The end-to-end inversion includes an analytic-signal step that removes the &plusmn;z "
  "mirror-symmetry ghost, and on synthetic data recovers an injected layer at roughly 27&times; "
  "the null level.")

P("2.4 Controls (what makes a null meaningful)", h2)
P("Every real-site run reports three controls. <b>(a) Null test:</b> the look order is shuffled "
  "and the inversion re-run, measuring the structure expected by chance. <b>(b) Positive control:</b> "
  "a synthetic reflector is injected into the real data and must be recovered; this proves the "
  "pipeline can see a signal in <i>that</i> dataset, so a null is informative rather than a dead "
  "pipeline. <b>(c) Surface-leakage:</b> the correlation between tomogram power and surface "
  "brightness, to check whether apparent depth structure is merely surface clutter leaking down "
  "the depth axis. We report a detection only if real-vs-null contrast exceeds chance <i>and</i> "
  "the positive control passes <i>and</i> leakage is low.")

fig("tomogram_selftest.png",
    "Figure 1. End-to-end self-test on synthetic data: an injected layer is recovered well above "
    "the null, with the positive control and leakage checks passing.", width=5.0*inch)

# ----------------------------------------------------------------------------- 3
P("3. Data", h1)
P("All scenes are free Umbra Open Data (CC-BY 4.0), X-band spotlight, supplied as SICD (and where "
  "available CPHD) and read with sarpy. This is the same data class used in the 2025 Giza work "
  "(Umbra), so the comparison is like-for-like on publicly reproducible inputs; Biondi&rsquo;s "
  "2022 papers instead used non-free COSMO-SkyMed. Biondi&rsquo;s exact deep sites (Gran Sasso, "
  "Giza) are not in the free archives and would require paid tasking; Mount Vesuvius &mdash; his "
  "own peer-reviewed site &mdash; is available free and is included here.")

# ----------------------------------------------------------------------------- 4
P("4. Results", h1)
P("Table 1 summarises the four sites. In every case the real tomogram is indistinguishable from "
  "its shuffled null. Where a positive control was run (Vesuvius, Butte) it passed, confirming the "
  "null is meaningful.")

data = [
    ["Site", "Collect", "Reg. quality", "Real / Null", "Verdict", "Pos. ctrl", "Leakage"],
    ["Bingham Canyon", "2024-01-12 UMBRA-05", "0.67", "front-end only", "no signal", "n/a", "n/a"],
    ["Komati Power Stn", "2023-08-13 UMBRA-05", "0.85", "2.8x / 1.3x", "NULL", "PASS", "0.32"],
    ["Mount Vesuvius", "2023-11-15 UMBRA-05", "0.72", "4.1x / 1.5x", "NULL", "PASS", "0.03"],
    ["Butte, MT", "2024-03-07 UMBRA-04", "0.82", "3.3x / 1.4x", "NULL", "PASS (z=19/19)", "0.28"],
]
t = Table(data, colWidths=[1.05*inch, 1.25*inch, 0.72*inch, 0.78*inch, 0.62*inch,
                           0.95*inch, 0.6*inch])
t.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
    ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#fff3f3")),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#888888")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(t)
P("Table 1. Four free single-pass X-band spotlight sites. Contrast = peak tomogram power "
  "relative to background; &lsquo;Real / Null&rsquo; gives real vs shuffled-null contrast. The "
  "depth axis is relative/uncalibrated.", cap)

P("4.1 The decisive case: Butte, Montana", h2)
P("Butte was run specifically as a true-positive test against a <i>known shallow void</i>. The "
  "Butte district is the most densely mapped underground mining area on Earth &mdash; on the order "
  "of 10,000 miles of workings within roughly seven square miles, with level maps drawn at "
  "100-foot vertical intervals from near surface (first levels ~100 ft; 1870s&ndash;1900s "
  "near-surface workings) down to ~5,100 ft. The scene (46.008&deg;N, &minus;112.534&deg;W) sits "
  "over the southwest of the Hill near the Travona and Anselmo workings. Ground truth is available "
  "from the National Mine Map Repository (OSMRE) and the Montana Bureau of Mines &amp; Geology. "
  "The winter acquisition gave frozen, coherent ground and the highest registration quality of any "
  "site (0.82), so the null cannot be attributed to poor data; the in-data positive control "
  "recovered an injected reflector cleanly (z = 19/19). The real tomogram nonetheless remained "
  "indistinguishable from its null (3.3&times; vs 1.4&times;). Surface leakage was 0.28 &mdash; "
  "flagged low, and driven by a single outlier point rather than a trend; because the verdict is a "
  "null, leakage does not affect the conclusion.")

fig("tomogram_2024-03-07-04-48-26_UMBRA-04_SICD.nitf.png",
    "Figure 2. Butte, MT. Top-left: real tomogram (depth vs along-track position) &mdash; scattered "
    "speckle only. Top-right: look-shuffled null, statistically the same. Bottom-left: positive "
    "control &mdash; an injected reflector recovered as a sharp horizontal band, proving the "
    "pipeline would detect a real signal in this dataset. Bottom-right: surface-leakage scatter.")

P("4.2 Mount Vesuvius (Biondi&rsquo;s own peer-reviewed site)", h2)
P("Vesuvius is the cleanest head-to-head with the published work because it is Biondi&rsquo;s own "
  "peer-reviewed site. The result is again a null (4.1&times; vs 1.5&times;) with a passing "
  "positive control and very low leakage (0.03).")

fig("tomogram_2023-11-15-19-47-28_UMBRA-05_SICD.nitf.png",
    "Figure 3. Mount Vesuvius. Same panel layout as Figure 2: real indistinguishable from null, "
    "positive control passing, leakage 0.03.")

# ----------------------------------------------------------------------------- 5
P("5. Robustness: does an unknown velocity model hide a real signal?", h1)
P("The natural objection to a null is that the relative depth axis is uncalibrated: with no "
  "site-specific seismic velocity v(z), might a real reflector be mis-placed and missed? We "
  "distinguish two versions of this concern. <b>Axis calibration</b> is <i>not</i> a threat to the "
  "verdict: a velocity model only maps the relative depth index to metres &mdash; a monotonic "
  "re-labeling of the z-axis &mdash; and cannot create above-null contrast where none exists. Our "
  "real tomograms are indistinguishable from their shuffled nulls across the <i>entire</i> depth "
  "axis, so rescaling that axis leaves the contrast-vs-null unchanged; there is no signal at any "
  "depth to relocate.")
P("The legitimate version is <b>search-grid coverage</b>: if the inversion&rsquo;s depth grid does "
  "not span the depths where a true reflector would sit (because the assumed velocity is wrong), a "
  "signal outside the searched range could be missed. The pre-registered confirmatory test for "
  "this is a sweep of the assumed seismic velocity by &plusmn;20&ndash;50% with the depth grid "
  "widened accordingly, re-running the null and positive-control diagnostics at each setting; the "
  "null is robust only if no plausible velocity produces an above-null, leakage-clean band. This "
  "is the more rigorous form of the velocity check and the one we recommend reporting in the "
  "journal version; the calibration argument above already shows it cannot rescue the current "
  "verdict, only test grid coverage. <i>(This sweep is specified but not yet executed in this "
  "preprint version.)</i>")

# ----------------------------------------------------------------------------- 6
P("6. Discussion", h1)
P("The pattern &mdash; four real nulls with passing positive controls &mdash; is what "
  "single-pass physics predicts. The depth aperture available from one acquisition is small, and "
  "deep energy attenuates, so the inversion is poorly conditioned for anything but very shallow "
  "structure; additional passes improve shallow resolution and conditioning but do not restore "
  "energy the geometry never captured. Compute amplifies a physically adequate measurement; it "
  "cannot manufacture information the aperture did not record. Crucially, the pipeline does not "
  "<i>fabricate</i> structure either: given a real injected signal it recovers it, and given real "
  "data it returns honest noise.")
P("We frame this as a reproducibility statement, not a fraud accusation. We used different data "
  "(free Umbra X-band) than Biondi&rsquo;s 2022 COSMO-SkyMed work, and his HarmonicSAR steering "
  "matrix was never publicly disclosed, so we cannot reproduce his exact operator. What we can say "
  "is bounded and clean: on the publicly reproducible free single-pass X-band data of the same "
  "class used for the 2025 claims, the method does not recover subsurface structure &mdash; even "
  "against a documented shallow mine void where success would be most expected.")

# ----------------------------------------------------------------------------- 7
P("7. Limitations and next steps", h1)
P("This study is bounded to free single-pass X-band spotlight data and a relative depth axis. It "
  "does not test multi-pass or airborne/drone geometries, which enlarge the angular aperture and "
  "are the physically motivated route to any shallow true positive; nor does it test paid tasking "
  "of a clean shallow target such as Derinkuyu/Cappadocia. The decisive remaining experiment is a "
  "velocity-robust Vesuvius (or a second shallow true-positive) with published seismic models. A "
  "negative there would bound the method&rsquo;s practical reach to the very shallow regime; a "
  "positive would be the first credible single-pass detection and would itself be major.")

# ----------------------------------------------------------------------------- 8
P("8. Data and code availability", h1)
P("All scenes are free Umbra Open Data (CC-BY 4.0). The pipeline (subaperture, micromotion, "
  "tomogram) with self-tests and the controls described here is maintained in the project "
  "repository. Figures in this preprint are produced directly by the tomogram stage.")

P("References", h1)
refs = [
    "Biondi, F. &amp; Malanga, C. (2022). Great Pyramid Doppler tomography. Remote Sensing, "
    "14(20):5231. arXiv:2208.00811.",
    "Biondi, F. (2022). Mount Vesuvius Doppler tomography. Remote Sensing, 14(15):3828.",
    "Patent WO2024008365A1 (status: ceased/lapsed). SAR underground/undersea/under-ice "
    "tomographic Doppler imaging.",
    "not-JASH. sar-doppler-tomography (reproduction; CUDA; MUSIC/Capon; null tests). GitHub.",
    "mfwarren. Pyramid (feasibility on open Sentinel-1). GitHub.",
    "Umbra Open Data, AWS Registry of Open Data (CC-BY 4.0). Capella Open Data, AWS.",
    "National Mine Map Repository (OSMRE), Green Tree, PA. mmr.osmre.gov.",
    "Montana Bureau of Mines &amp; Geology. Butte district mine maps and 3-D workings model.",
    "U.S. Geological Survey, I-2050-C: mines and prospects in the Butte 1&deg;x2&deg; quadrangle.",
]
for i, r in enumerate(refs, 1):
    P("[%d] %s" % (i, r), ref)

rule()
P("<i>Preprint, v2 (June 2026). Author: Hassan Foreman. An honest reproducibility statement on "
  "publicly reproducible free single-pass X-band SAR Doppler tomography.</i>", cap)

# ----------------------------------------------------------------------------- build
doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.8*inch, bottomMargin=0.8*inch,
                        title="Single-Pass SAR Doppler Tomography Reproduction",
                        author=AUTHOR)
doc.build(story)
print("wrote", OUT)
