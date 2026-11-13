# Exploration: the S-like pipeline on Butte, Komati and central Cairo — 13 Nov 2026

**Status: EXPLORATION, not pre-registered. Single passes. Our reconstruction, not Seyfzadeh's code.**
Script `src/explore_sites_slike.py` (imports the unchanged Test P code, `src/test_p_fake_targets.py`).
Numbers: `runs/explore_sites_{komati,butte,cairo}.json`; pictures `runs/explore_sites_*.png`.
Crops: 1024 x 1024 at each scene centre, five parallel lines of 149 positions (made on the Mac by
`runs/_sites_extract.py`).

**Question.** On ground with no pyramid claim attached, how often does the pipeline show a "three-level
shaft" at an INVENTED place (the 200 fake targets fixed for Test P), for at least one of the 315 allowed
tunings? Each scene has a pure-noise twin and a planted-signal control.

| Scene (pass) | real scene | pure noise | planted control (share of tunings; p) |
|---|---|---|---|
| Komati power station, 13 Aug 2023 (3.3 s) | 10% | 13% | 0.28; p 0.005, passed |
| Butte, 7 Mar 2024 (10.7 s) | 18.5% | 3.5% | 0.35; p 0.005, passed |
| Central Cairo, Capella 23 Nov 2024 (35 s) | 3.5% | 2% | 0.27; p 0.005, passed |
| *Giza desert, 7 Feb 2023 (Test P)* | *15%* | *24%* | *0.18; passed* |
| *Giza desert, 8 Mar 2023 (Test P)* | *6%* | *4.5%* | *0.26; passed* |

**Reading.**
- The control passed everywhere: a real planted three-level signal is found, so the pipeline can see one.
- An invented shaft "appears" for 3.5-18.5% of invented targets on real scenes and 2-24% on pure noise.
  The rate depends on the scene and pass, not on whether anything is claimed there.
- Butte is the one scene where the real image gives clearly more false shafts than its noise twin
  (18.5% against 3.5%). Butte is also the scene that misbehaved before (rectangular-window leakage, STATE
  s1). Scene content can add false structure beyond what noise gives.

**Limits.**
- Butte is not empty ground: the scene centre (46.008 N, 112.534 W) is the old mining district, with real
  underground workings. The fake targets are invented positions and depths, so hits on them are not
  evidence about those workings either way, but Butte must not be described as a place with nothing below.
- Position spacing differs by scene (Komati 1.0 m, Butte 0.55 m, Cairo 0.21 m) because the step was capped
  at 5 pixels; Test P used about 1 m. Depth scale (CYC50) is arbitrary, as in Test P.
- The `adjR2` block in the JSON files is dominated by near-zero frequencies (shallow rows that the hit rule
  excludes) and must not be compared with Seyfzadeh's published adjusted R^2 values. Do not cite it.
- Single passes: nothing here bears on repeatability. Giza x3 (Test R) remains the only repeat-pass result.
