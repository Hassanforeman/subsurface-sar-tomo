# Public comment posted on the DeDunking livestream — 15 Nov 2026, 12:58 AEST

Video: "Evaluating the Biondi SAR Method with Trevor Grassi LIVE" (youtube.com/watch?v=chLORnlqB5Y).
Posted as @hassanforeman6119 at Hassan's instruction (detailed; our work, issues with theirs, not a neutral
party, no code or data; stick to the science). 3,628 characters. Sources for each number are in brackets
below; the brackets were not part of the posted text.

---
Dan, you said of Manu's work: "a guy could sit down and do it... do the same work." I did. I'm an independent researcher, not an SAR professional, and everything I did is public: code, data list and a preprint (Zenodo, DOI 10.5281/zenodo.24062309, currently under review). Here is what came out, and where I think this validation falls short.

WHAT I DID
1. Rebuilt the published method and ran it on three free Umbra radar scenes of Giza. No detection below the surface. When I planted an artificial signal in the data, the method found it, so the test was not blind. [paper v6.3]
2. After Trevor's premiere I rebuilt Manu's pipeline as closely as his public posts allow, and wrote the rules down before running it (pre-registered). I tested the Osiris Shaft line against 200 invented "shafts" at random positions and depths. Result: the real shaft's three known levels did not light up together in any of the 315 allowed tunings. Between 5% and 24% of the invented shafts did in at least one tuning. Bare desert and pure random noise gave the same kind of patchy pictures. [RESULTS_FAKE_TARGETS_2026-11-12; runs/test_p_02-07.json, test_p_03-08.json: 4.5-24%]
3. Same test on Butte (USA), Komati (South Africa) and central Cairo: invented shafts "appear" at roughly 4% to 19% of invented locations. A planted signal was found every time. [EXPLORATION_SITES_SLIKE_2026-11-13: 3.5 / 10 / 18.5%]
4. Three passes over Giza: a planted signal repeats from pass to pass. The real patterns do not. [RESULTS_REPEAT_PASS_2026-11-12; caveats there NOT stated in the comment: unblinded, >= ~1 px sensitivity]

WHAT IS IN THEIR OWN RELEASED FILES
5. Western Cemetery 3D model: the largest value in the whole file is an adjusted R-squared of 0.0041. The best fit explains 0.4% of the data. In my simulation, random noise under the same settings scores the same. [ANALYSIS_ARF_RELEASED_DATA_2026-11-12]
6. Great Pyramid model: largest value 0.041, with a much looser filter (P=2). The file itself carries the note: "Face-normal depth is a visualization hypothesis. It does not validate the physical depth direction or identify chambers." [ANALYSIS_ARF_MODELS_2_3_2026-11-13]
7. Osiris Shaft model: a drawing of the known shaft. No radar data in it.

THE "NEGATIVE CONTROL"
8. The blank X13 picture is not a test of "no chambers". It is the same line at the same place on a different recording. One recording shows patches, the other shows nothing. X13 is also the recording behind the Western Cemetery "match". So which is it: can X13 see underground or not?
9. The control that would settle it is still missing: put random noise and bare ground through X33, the recording that does show patches, and publish those pictures next to the pyramid ones.

REPRODUCIBILITY
10. There is no public code repository, no scene IDs and no paper. Manu's own posts say the ICEYE data came through a private foundation, and it has not been released. Nobody outside can re-run any of it. "Do the same work" is not possible until that changes.

INDEPENDENCE
11. This is not a neutral third party, and I say that without questioning anyone's sincerity. Trevor says he was in constant communication with both Manu and Filippo. Manu worked from Filippo's published pictures of the same targets. Filippo himself judged the match. The ARF article says the two may co-author a paper, and Manu co-hosts Trevor's January tour. A blind test means the person running it does not know what the answer is supposed to look like.

LIMITS OF MY OWN WORK
My version of Manu's pipeline is a reconstruction from his descriptions, not his code. I have never run his code or his data, because neither is available. If he releases them I will run them and publish whatever comes out, including if it proves me wrong.

An offer: I will send my list of 200 invented targets to Manu or anyone else. Run them through the real pipeline. If the real shaft beats the fakes, that is evidence. That is all anyone is asking for.
---

## Commitments this makes (track in STATE)
- Send the 200-target list (`runs/test_p_fake_targets.json`) to anyone who asks.
- Run Seyfzadeh's code/data if released and publish the outcome either way.
## Weak points a reply could press
- Item 4 omits the three Test R caveats. Item 2/3 are our reconstruction (stated). Item 8's X13 point may be answered by
  local incidence angle on a sloped face (logged in STATE as a question, not proof).
