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

Not yet checked: the first 20 min; Grassi's "four companies" claim (not discussed in the watched part).
