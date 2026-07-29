# Note to the PCI Archaeo recommender

**Submission:** ArticleID #1130 — "No Reproducible Evidence for Deep Subsurface Structures
Beneath the Giza Plateau: A Controlled Reproduction of Single-Source SAR Doppler
Micro-Motion Tomography"
**Recommender:** Dr Francesca Di Palma (took charge 8 July 2026)
**Status at time of writing:** Round 1, reviewers needed — 9 invited, 6 declined/cancelled, 0 agreed
**Send to:** the recommender, cc `contact@archaeo.peercommunityin.org`

---

**Subject:** ArticleID #1130 — corrected preprint version posted (erratum, one table row)

Dear Dr Di Palma,

Thank you for taking charge of my submission (ArticleID #1130).

I am writing because I have found and corrected an error in my own manuscript, and I would
rather tell you now — while reviewers are still being sought — than have a referee find it.

While stress-testing the pipeline against a methodological objection raised publicly by
Dr Filippo Biondi, whose work the manuscript examines, I ran a 96-configuration sensitivity
sweep across the processing choices the paper had not varied. Two of the four Umbra rows in
Table 2 reproduced exactly (Butte 3.33× against a published 3.3×; Vesuvius 4.11× against 4.1×).
The Komati Power Station row did not. Tracing it, that row had been produced at a different
sub-aperture count from every other row — `n_sub = 128` rather than the pipeline default of 11 —
and its verdict label is wrong for that setting.

| | reg. quality | real / null contrast | ratio | verdict |
|---|---|---|---|---|
| As published | 0.85 | 50× / 10× | 5.00 | null |
| Corrected (`n_sub = 11`) | 0.85 | **2.8× / 1.3×** | **2.15** | indistinguishable from null |

The site remains a null result on either reading, and the correction *increases* the margin:
50/10 is a ratio of exactly 5.0, sitting precisely on the manuscript's own `> 5×` decision rule
and qualifying as null only marginally. It was the most attackable row in the table. At 2.15 it
is comfortably below threshold. Taking the published numbers at face value as an `n_sub = 128`
run, the pipeline's correct label there is *surface-pinned artifact* — also not a detection.
No claim in the abstract, discussion or conclusion changes.

I have posted a corrected version of the preprint on Zenodo:

- **v3 (corrected): https://doi.org/10.5281/zenodo.21668674**
- concept DOI on the submission record, `10.5281/zenodo.21066657`, now resolves to this version
- v2 as submitted remains published and untouched at `10.5281/zenodo.21067830`

v3 corrects the Komati row, adds a methods sentence stating the sub-aperture count for *every*
row so no row can silently differ again, and adds a "Changes in v3" section. If it would help
the record, I am happy for the submission to be updated to cite the v3 version DOI explicitly
rather than the concept DOI — please let me know whether that is something you or the managing
board would prefer to do.

The same exercise identified two further methodological weaknesses. I am flagging them rather
than patching them mid-review, because unlike the Komati row they affect every row:

1. the surface-pinning guard used a threshold of 5% *of the depth axis*, whose physical meaning
   changes with the sub-aperture count; it should be an absolute depth in resolution cells;
2. the null test shuffled sub-aperture order, which destroys the look-to-look smoothness that
   80% spectral overlap guarantees even under pure noise, making it anti-conservative; it should
   be an alignment null that preserves each patch's depth profile and randomises only cross-patch
   agreement.

Both changes strengthen the negative result — under the corrected pair, the sweep returns zero
detections where the original pair returned some. I propose to implement them at revision, once
the referees have had their say, rather than moving the manuscript underneath them. They are
implemented, validated and documented now, should the referees wish to see them:
`docs/SENSITIVITY_RESPONSE_BIONDI.md` and `src/followup_experiments.py` in the open repository
linked from the manuscript.

I appreciate that reviewers have been difficult to secure for this submission, and I am glad the
correction has come before rather than after they start reading.

With thanks for your time,

Hassan Foreman
