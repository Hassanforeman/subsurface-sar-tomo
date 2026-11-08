# Biondi / Khafre Project — method nuggets from video transcripts (9 Nov 2026)

**Source set:** Trevor Grassi's playlist "THE BIONDI PROTOCOL (Khafre Project Playlist)" (20 videos), linked from his
9 Nov 2026 X post to G. Tsoukalos. Eight videos were read via YouTube's English transcripts, filtered for method terms:

| Code | Video | ID |
|---|---|---|
| BP | THE BIONDI PROTOCOL: Revealing the Megachambers Below Giza (Grassi, with Biondi & Mei) | OK3bjfxLM9s |
| AU | AMENTI UNVEILED: The whole truth about the Khafre Project (Grassi) | Z4JQaTwJffY |
| LF | Scientists Reveal Hidden World Below the Pyramids — Independent Verification! (Lehto Files, with Biondi) | gDcPBPx0Fv8 |
| PU | EXCLUSIVE: Meet The Scientist Behind The MASSIVE Giza Plateau Discoveries! (Project Unity, Biondi) | b513P5g7XmQ |
| CS | KHAFRE PROJECT at COSMIC SUMMIT: Full Press Conference, Q&A | ioRDPMeOymc |
| AS | Second Sphinx DETAILS and the ArchaeoSAR Project | kO1vzZAFil0 |
| LS | THE LOST SPHINX: New SAR scans … press conference | h4-LIVLrfgo |
| HC | GIZA: THE HIDDEN CITY Final Act (English version, Bologna press conference) | rUl0G7N2iGk |
| MG | Beneath All Three Pyramids and the Sphinx! (Megalithomania, Biondi) | R_DIGdpxXCo |

> **Before quoting anything here publicly:** these are YouTube auto-transcripts of accented English (HC is an English
> voice-over of an Italian conference). Listen to the timestamp and confirm the words first, as for
> BIONDI_PODCAST_2026-07-16.md. The substance is clear; the exact wording is not verified.

## 1. Data and sensors
- **Capella and Umbra are the data sources** (AU 1:17:14; LF 45:49; CS 13:16), plus COSMO-SkyMed Second Generation (CS 13:16; HC 2:14:12) and possibly ICEYE ("ISI", HC 2:14:12). Capella supplied Giza images free of charge (LF 33:13; HC 2:14:12). Our reproduction uses the same two free providers.
- **Biondi says Umbra's "power is a bit insufficient"** and they are not proposing it (LF 45:49). *Expect this as an objection to our Umbra-based Giza runs.* Our only Capella scene is Cairo (null).
- "Cosmo-SkyMed and Capella — two different satellite systems and you have the same results" (spiral feature) (LF 0:29, 45:11).

## 2. Bandwidth, frequency and timing (his own numbers)
- The Doppler bandwidth is treated as **acoustic**: "0 Hz to 20, 30 or 40 kHz, which is acoustic information … the azimuth focusing process is made by sound" (PU 13:36; also PU 16:35, CS 6:17). English corroboration of the Italian podcast (BIONDI_PODCAST §1).
- **Half-bandwidth:** "normally a spotlight data has 22 or 25 kHz of bandwidth. But we are using half bandwidth in order to scan inside" → an average 0–10 kHz (CS 24:34). Consistent with the Vesuvius paper's "half the total length" aperture.
- **Sub-aperture duration:** spotlight acquisitions take 10–15 s; "we need … five, six, seven seconds in order to listen to the acoustic information" (CS 27:01); "not 15 seconds of integration but maybe only five seconds … transform a static image into a small video" (LF 42:03); "we have recorded 20 seconds of acoustic information" (PU 16:35).
- **Depth limit depends on the synthesised bandwidth:** maximum depth "around five kilometres … it depends on the Doppler bandwidth that we are synthesising" (PU 32:09).
- Contrast with the Vesuvius paper (Remote Sens. 14(15):3828), which sets the investigation frequency to **200 Hz** "set by us", while the Giza patent recipe uses ~22 kHz (≈ the Doppler bandwidth). Same method, frequencies differing ~110×.

## 3. Inversion and display
- **The inversion is a Fourier transform:** "we use methods based on fast Fourier transform … a global operation, not a local operation" (LF 17:24); "because of the nature of the fast Fourier transform, which is a global operator, it is necessary to have a very powerful computer" (MG 40:32); "between acoustic and electromagnetic there is a Fourier transform" (CS 6:17). Supports the settled result that the steering matrix is a DFT.
- Processing is fully coherent (complex numbers) (LF 24:19); tomograms are "energetic reflectivities … phase and module"; the displayed image is the **modulus** (HC 2:22:02).
- Colour SAR images are **three Doppler bandwidths** in RGB (LF 33:13), which he also calls a "Pauli" (polarimetric) reconstruction (MG 38:52).
- Tomogram axes: horizontal = tomographic line, vertical = depth (CS 9:15). Pixel tracking retrieves the surface vibrations (CS 6:17).

## 4. Tuning and analyst choices (most useful for the paper)
- **"We tuned the software to say: okay software, go where you can arrive, as deep as you can, and so things changed"** (PU 29:54). Earlier the software was tuned to "find things that are a bit on the top".
- Moving to the whole plateau "was just adjusting the software … in order to promote vibration" (MG 22:56).
- Second Sphinx 3-D: **"We kept on changing the parameters on the software to try to do things better. But here in the end the reconstruction mesh … it's a sphinx"** (HC 2:54:39). Malanga: "at the beginning … it looks bad and then we have to change some parameters" (HC 1:58:25).
- First month the shafts were thought to be noise; then "we have changed the radar, we have changed images" (PU 0:29, 32:09).
- All four are consistent with v6.3's finding that the depth scale is a free parameter and with the "researcher degrees of freedom" concern; none is a disclosure of the actual settings.

## 5. 3-D models, AI and recognition tools
- The 3-D model came from "one year of tomographies, maybe 200" (PU 34:18; AU 1:28:58 "200 scans").
- The 3-D reconstructions are "a human reconstruction by observing the objective measurements" (MG 36:09), i.e. hand-built (consistent with v6.3 §7 CAD finding).
- Face-recognition "software that can be downloaded on GitHub", Fibonacci spiral, "harmonious facial ratio … Greek and Renaissance canons" (HC 2:55:41–2:59:11); AI "entrusted with the task of interpreting the Doppler maps, 96.1%" (HC 3:08:14); Gemini "blind test" (HC 3:10:37; LS 18:16); Grok 94% (LS 19:55). Already covered by v6.3 §7.
- Grassi: AI was used "to validate their own interpretations" against pareidolia (AU 36:33, 2:32:14).

## 6. Software, compute, disclosure
- Software ported **MATLAB → C++ → CUDA**; one month of processing now 3–4 hours (HC 2:18:32–2:19:01); one slice on a 45-core machine (CS 1:07:39); "the algorithm is the same" as 2022, kernel changed (PU 26:44); "only two computers" (AS 8:41).
- **"We are not anymore explaining people how the method works"** (BP 7:38); peer review "not mandatory" (BP 6:00).
- Grassi says the method is "never fully revealed … patent pending" (AU 10:47) and that critics cannot disprove "a patent that's not even publicly disclosed" (BP 1:26:55). In fact WO2024008365A1 is published (and lapsed).
- Proposed validators: Howard Zebker, Stanford (LF 31:00; CS 47:33) — no public Zebker result as of 27 Sep (STATE); Gran Sasso scan offered as proof (AU 1:09:50).

## 7. What this suggests doing (not yet pre-registered)
1. **Capella Giza scene.** Pre-empts "Umbra power is insufficient". Check Capella Open Data for any Giza/Cairo-plateau acquisition; if none, note the limit explicitly.
2. **His disclosed timing/bandwidth as a configuration.** Half the Doppler bandwidth (~0–10 kHz) and 5–7 s sub-apertures within a 10–15 s collect. Pre-register, then run on the three Giza scenes; it closes part of the "you didn't use his settings" gap from his own words.
3. **Cross-paper frequency inconsistency** (Vesuvius 200 Hz vs Giza ~22 kHz) and the four "tuning" quotes → candidate text for the PCI revision (§3.2 / §9), once quotes are verified against audio.
