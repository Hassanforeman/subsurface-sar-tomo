# Review: "THE BIONDI VALIDATION" (Grassi, premiere 12 Nov 2026)

Video: youtube.com/watch?v=SjJTRVgr9Mw (~140 min; premiere 09:11 Brisbane). Watched live from ~21 min to ~87 min (the end
of the substantive call) via auto-captions plus frames. The first 20 min and the last minutes were not watched.
Frames: docs/img/validation_video_2026-11-12/. Judged against prebuttal #17 (PREBUTTAL_KHAFRE_2026-11-09.md).

## What was shown
- Seyfzadeh (dermatologist, says so on camera, ~66 min) re-implemented the method from Biondi's published papers
  (Vesuvius + the retracted pyramid paper): "completely independent effort", "no communications with Filippo"; Biondi:
  "this is the first time that I am speaking with Manu" (~59 min). Pipeline = "Biondi Protocol v1.9" (BiondiProtocol
  GitHub, v1.7 in Sep): 128x128 coarse + 24x32 fine co-registration patches, test-vector insertion to check registration.
- Data: an early low-resolution Capella scene "for free" (~39 min); later results unstated scene. "Atlantos"(?) image source mentioned ~53 min.
- Depth: Biondi's lambda replaced (not 0.24 m); limestone velocity from Dobecki & Schoch 1992; "adjusted ... to match it
  more closely with the Giza plateau"; calibrated on Campbell's Tomb and a shaft near Khufu, then applied to Osiris.
- Key result: Osiris shaft placement probe (149-position line, ~1 m spacing, 0-50 m "nominal depth", adjusted R^2 heat map,
  K=295, W=175). Blobs claimed at the three surveyed levels 10/22/33 m (Hawass survey). Hand-drawn ovals in Photoshop;
  four-panel comparison with Biondi's scan (frame four_panel_comparison_61m.png). Also Khafre east/west base lines.

## Against prebuttal #17
| Test | Result |
|---|---|
| (a) Released inputs/code | NO. No scene IDs, code or paper; description still "Links will added at premiere". Steps "on my Facebook page". Offered to share the 3-D model of the known shaft only. |
| (b) Controls | Positive: Campbell's Tomb and nearby shafts (known, used for calibration). Parallel-offset tomogram near the King's Chamber. Negative (desert/noise): NONE. |
| (c) Blindness | NO. Shaft model built first "so I know what to expect"; depth law tuned to known shafts; overlay "flipped backwards" (Grassi) and "you can stretch it a bit" (Biondi). |
| (d) Independence | Plausible for the build (no contact claimed, confirmed by Biondi). Not for the evaluation: Biondi judges the match; Biondi offers to co-author an MDPI paper; Seyfzadeh co-hosts Grassi's Feb 2027 Egypt tour ($1,300, "a great selling point for the tour"). |
| (e) Ground truth | Only known features. Both proposed real tests themselves: Biondi = known mine + geophones; Seyfzadeh = predict an undiscovered Valley of the Kings tomb ("that's endgame"). |
| (f) Retraction | Unchanged. |

## Self-reported uncertainty (quotes)
"more than 50% confident ... maybe not 100%" (~45 min); signal "is busy" / Biondi "normal ... crowdy of targets" (~44 min);
nearby shafts "may also bleed into the detection" (~54 min); "replicate it in some limited way" (~72 min); journals
"will most likely reject anything I submit because I don't have the credentials" (~76 min).

## Our assessment
A partial re-implementation of the published recipe, evaluated by eye against known targets with a tuned depth scale and
no negative control. Agreement between two implementations of the same recipe is expected if the recipe generates the
patterns (our noise-only result, paper v6.3). Caveat on our side: our noise mechanism (cumsum random walk + DFT) is
shown for Biondi's published accumulation route; v1.9 uses "window fits / adjusted R^2", which we have not run. A noise
control on v1.9 itself is the decisive check; ask for it rather than assert the result.

## Full transcript reviewed (12 Nov, 11:40; YouTube transcript, 923 segments, 1:54:49)
Video is 1:55, not 80 min. Opening (0:00-5:10) and post-interview segment (1:26:54-1:54:49) are Grassi narration.

**Independence (Grassi's own words).** "On the very first day this paper was released ... I was already in conversation with
Dr. Manu" (0:37); "several years of hard work throughout which I was in constant conversation with him" (1:19); "I've been
offering and even pressuring him to consider speaking with Filippo" (2:04). Seyfzadeh co-hosts Grassi's Egypt tour, on which
Biondi presents remotely (1:53-1:54). Independent of Biondi's code: plausible. Independent of the Grassi/Biondi circle: no.
A Rice University geophysicist (former Shell) helped him (20:40), unnamed.

**Framing.** Sceptics: "not a single one of them had the first clue of how the technology works" (0:53); scientific community
"has become a political party" (3:20); "flood the feeds of those rudest haters" ... "they owe Biondi a public apology" (3:39);
"hammering the final nail in the skeptic's coffin" (5:03); "a skeptic's argument just means nothing to me" (1:53:06).
Biondi: "the retraction of the paper is politic" (6:35). Nobody named; our work is not mentioned.

**Retraction/litigation.** Biondi asks MDPI to retract his Vesuvius paper too ("same science") (7:32-8:46) - the same
consistency point as our 9 Nov letter of concern. Malanga suing MDPI's executive board, asking "1 billion" plus criminal
complaints (11:05-12:52); Biondi says he is "out of this litigation". MDPI's stated reason, read on screen (1:42:03): requires
"rigorous experimental validation and independent confirmation", comparison with "an established reference method", and
"simultaneous measurements obtained using seismic sensors".

**Tuning after the interview (1:27:17-1:27:42).** Low-res scan shown on the call; then a higher-res scan "with some noise";
then "another one ... with more filtering, and he got this beautiful image that picks them up perfectly". Iterating the filter
until the image matches the known target is tuning to match. Ovals placed in Photoshop at fixed points over all scans.

**New claims beyond known features.** "at least six levels beneath the third level ... something very big on the bottom"
of the Osiris shaft (1:29:22); a lateral tunnel; "deeper chambers which Biondi had showed". None tested.

**GPR/ERT "clincher" (1:34:47-1:44:42).** (a) Khafre east face: "broad correlation", "it's possible if we shift the line a
tiny bit, we could get a lot closer". (b) Western Cemetery (Japanese GPR/ERT team, published 2024): GPR imagery is 0.5-5 m
deep ("only about 6 ft deep"); SAR shows "a whole mess of anomalies" there plus "two huge voids ... between 25 to 48 m" that
no GPR saw. Comparing a cluttered SAR image with a cluttered shallow area is not a validation; no blind comparison, no
statistics, no negative area. Does not meet MDPI's criterion (simultaneous seismic sensors).

**King's/Queen's Chamber control (1:45:22-1:50:38).** Pink spots "at least roughly lining up ... in terms of height, not
horizontally"; "He hasn't adjusted it perfectly ... could be a little slightly off"; extra anomaly offered as possible
confirmation of the Coffer Project ramp. Excuse given: "Manu's a dermatologist, so we can cut some slack".

**"Four companies" claim:** not made or supported in the video.

**Overall reading (agreed with Hassan 12 Nov):** Seyfzadeh put real effort into a sincere amateur attempt; Grassi then oversold it as final proof.

**Follow-up:** Test P pre-registered 12 Nov (PREREGISTRATION_FAKE_TARGETS_2026-11-12.md). Note: the BiondiProtocol repo is no longer public (404, 12 Nov).

## Science-meter rating (Claude, for Hassan)
2/10. Credit: re-implementation from public text, planted-shift test of co-registration, calibration on known shafts, an
on-camera statement that positive controls should come first. Against: no negative control, no blinding, depth law and
filters tuned on the targets, hand overlays, every blob counted as a hit or new discovery, nothing released, evaluator =
Biondi, presenter = long-time collaborator with a commercial tour.
