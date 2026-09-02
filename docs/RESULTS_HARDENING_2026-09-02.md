# Paper-hardening runs — 2 September 2026

Two cheap runs that close adversarial-review items W13 (window taper) and W7/P1#18
(planted floor vs the paper's own decision rule).

## 1. Four-taper binary grid, all three Giza scenes (closes W13)

C/align (the decision statistic) at n_sub=11, every taper × every Giza scene:

| scene | blackman | hann | hamming | rect | max | detection? |
|---|---|---|---|---|---|---|
| 7 Feb UMBRA-05 | 2.87 | 3.67 | 3.08 | 3.32 | 3.67 | none |
| 8 Feb UMBRA-04 | 1.55 | 2.28 | 2.80 | 2.93 | 2.93 | none |
| 8 Mar UMBRA-04 | 1.79 | 2.51 | 2.55 | 2.11 | 2.55 | none |

**No window taper, on any Giza scene, clears the 5× rule.** Max across all 12 = 3.67.
Peak stays surface-pinned throughout. Two useful facts for the rebuttal:
- Hann is NOT universally the loudest choice: rect is highest on 8 Feb, Hamming on 8 Mar.
  The 7-Feb Hann=6.06 native contrast that missed the pre-registered 3–5 band is a
  scene-specific coincidence, not a systematic "author picked the loudest window."
- The taper moves the number but never the verdict. Report the range, not Hann; and per
  the PCI letter, do NOT use Blackman 4.69 to explain away the 6.06 miss — the miss stands.

## 2. Planted floor vs the paper's OWN 5× rule (closes W7 / P1#18)

E12 plant on the 7 Feb Giza SICD. Alignment null at n=11 is 1.65, so the paper's decision
threshold is 5×1.65 = 8.25. "Found" = peak recovered at the planted depth (3.30 cells).

| planted | ×noise | peak cells | contrast | found by depth | contrast > 8.25 (paper's 5× rule)? |
|---|---|---|---|---|---|
| none | 0 | 1.75 | 6.06 | no | no |
| 0.05 px | 2.1 | 1.75 | 4.69 | no | no |
| 0.10 px | 4.2 | 1.73 | 3.39 | no | no |
| **0.20 px** | **8.4** | **3.16** | 5.40 | **YES** | **NO** |
| 0.50 px | 21.1 | 3.18 | 13.69 | yes | yes |

**The plant is recovered by peak-location at 0.20 px, but does not clear the paper's own
contrast rule until 0.50 px.** At the 0.20 px floor the contrast (5.40) is actually LOWER
than the empty-scene value (6.06) — the contrast statistic cannot separate "real reflector
present" from "nothing," and only peak-depth recovery does. This is a result in its own
right and belongs beside Table 4: the method's detection channel is depth-of-peak, not the
contrast-vs-null figure the published work reports; over the sub-floor range the contrast
statistic is uninformative-to-backwards. (Caveat retained: plant is scene-wide coherent,
one depth, one n_sub — the most favourable case; a localised reflector floors higher.)
