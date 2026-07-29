# Erratum — Komati Power Station row, results table

*Applies to Zenodo preprint record 10.5281/zenodo.21066657 (v2 → v3). The code/data archive 10.5281/zenodo.21065675 is a separate record and is updated by cutting a GitHub release, not by manual upload.*

*Prepared 29 July 2026 for the preprint under evaluation at PCI Archaeo:
"No Reproducible Evidence for Deep Subsurface Structures Beneath the Giza Plateau:
A Controlled Reproduction of Single-Source SAR Doppler Micro-Motion Tomography."*

---

## 1. What is wrong

The results table reports, for Komati Power Station (Umbra collect
`2023-08-13-07-03-04_UMBRA-05`):

| | reg. quality | real / null contrast | verdict |
|---|---|---|---|
| **As published** | 0.85 | **50× / 10×** | null |

Two errors.

**(a) The row was produced at a different sub-aperture count from the others.** Re-running the
pipeline at its default `n_sub = 11` — the setting that reproduces the Butte and Vesuvius rows
exactly — gives **2.8× / 1.3×**. The published 50× / 10× is reproduced at **`n_sub = 128`**
(49.0× / 7.4×). The table therefore mixes configurations across rows without stating it.

**(b) The verdict label is wrong for the setting that produced the numbers.** At `n_sub = 128` the
pipeline does not return "null". It returns *"ABOVE NULL but SURFACE-PINNED at 3 m → detrend/surface
ARTIFACT, NOT subsurface structure"*.

## 2. Corrected row

| | reg. quality | real / null contrast | ratio | verdict | pos. ctrl | leakage |
|---|---|---|---|---|---|---|
| **Corrected (`n_sub = 11`)** | 0.85 | **2.8× / 1.3×** | **2.15** | indistinguishable from null | PASS | 0.32 |

## 3. How it was found

While running a configuration-sensitivity study prompted by an external methodological objection
(28 July 2026), the Hann/phase-correlation baseline was re-run on all four Umbra sites. Butte
(3.33× vs published 3.3×) and Vesuvius (4.11× vs published 4.1×) reproduced to two decimal places;
Komati did not. A sweep over `n_sub` on the same scene located the published figure at `n_sub = 128`.
Two independent code paths — `src/tomogram.py` and `src/sensitivity_sweep.py` — agree on the
corrected value.

## 4. Effect on the paper's conclusions

**None, and the correction increases the margin.**

- 50× / 10× is a ratio of exactly **5.0**, sitting precisely on the manuscript's `> 5×` decision
  rule and qualifying as "null" only marginally. It was the most attackable row in the table.
- The corrected ratio is **2.15**, comfortably below threshold.
- Under the alternative reading — taking the published numbers at face value as an `n_sub = 128`
  run — the correct label is *surface-pinned artifact*, which is also not a detection.
- Every other row is unaffected.

The site remains a null result on either reading. No claim in the abstract, discussion or conclusion
changes.

## 5. Corrective actions taken

1. The Komati row is corrected as above.
2. A methods sentence now states the sub-aperture count used for **every** row, so no row can
   silently differ again.
3. Two further methodological weaknesses were identified during the same work and are being
   addressed in the revision rather than here, since they alter every row rather than one:
   - the surface-pinning guard used a threshold of 5% *of the depth axis*, whose meaning changes
     with `n_sub`; it is replaced by an absolute-depth criterion in resolution cells;
   - the null test shuffled sub-aperture order, which destroys the look-to-look smoothness that 80%
     spectral overlap guarantees even under pure noise; it is replaced by an alignment null that
     preserves each patch's depth profile and randomises only cross-patch agreement.

   Both changes strengthen the negative result. Full detail, code and validation:
   `docs/SENSITIVITY_RESPONSE_BIONDI.md` and `src/followup_experiments.py` in the project repository.

---

## Suggested note to the recommender

> Dear [recommender],
>
> While stress-testing my pipeline against a methodological objection raised publicly last week, I
> identified an error in one row of the results table of the preprint currently under evaluation.
>
> The Komati Power Station row was produced at a different sub-aperture count from the other rows
> (`n_sub = 128` rather than the default 11), and its verdict label is incorrect for that setting.
> The corrected values are 2.8× / 1.3× against the published 50× / 10×. The site remains a null
> result on either reading, and the correction increases the margin below the detection threshold
> — the published figure sat exactly on it. No conclusion changes.
>
> I have posted a corrected version of the preprint and attach a short erratum note. I would rather
> the referees read the corrected table than find this themselves.
>
> The same exercise identified two methodological improvements — a scale-stable surface-pinning
> guard and a better-specified null test — which affect every row and which I propose to implement
> at revision rather than mid-review. Both strengthen the negative result. They are documented and
> validated in the open repository if the referees wish to see them now.
>
> With thanks,
> Hassan Foreman
