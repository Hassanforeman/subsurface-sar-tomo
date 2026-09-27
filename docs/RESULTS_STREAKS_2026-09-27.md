# Are the vertical streaks surface-driven? — pre-registered test F — 27 Sep 2026

**Pre-registration:** `docs/PREREGISTRATION_STREAKS_2026-09-27.md`, committed `603ca70` before the run.
**Script:** `src/streak_surface.py` (run at `603ca70`). **Output:** `runs/streak_surface.json`.
Same three Umbra Giza centre crops and identical volume build as C.4 step 1; nothing re-tuned.

## 1. Primary result: H-surface REJECTED (our own hypothesis failed)

| Volume | ρ(S,Q) registration | ρ(S,M) brightness | ρ(S,K) texture | ρ(S,E) identity | Control (in displacement) | Verdict |
|---|---|---|---|---|---|---|
| empty noise (seed 0) | +0.01 | −0.02 | +0.05 | +1.00 | — | reference |
| 02-07 U05 | −0.02 | −0.02 | −0.02 | +1.00 | 4/4 | NOT LINKED |
| 02-08 U04 | +0.15 | +0.05 | +0.16 | +1.00 | 4/4 | NOT LINKED |
| 03-08 U04 (prereg primary) | −0.12 | −0.14 | −0.13 | +1.00 | 4/4 | NOT LINKED |

By the rule fixed in advance, the primary scene and all three scenes are NOT LINKED → **H-surface
REJECTED.** The hypothesis we formed from the 2026 press images — that streaks sit under tiles with poor
registration or distinctive backscatter — is wrong at the 0.3 effect-size bar. The positive control,
planted in displacement before tracking (0.5 px, 4 tiles), was recovered 4/4 in every scene, so the
statistic could see trajectory structure; this is a real negative, not a blind test.

## 2. Near-miss split (02-08): MIXED by the rule

N1 = 0.14 (< 0.3: blob mask not correlated with surface brightness or registration). N2 (median blob
elongation over the 8 treatments) = 26.0 for 02-08, vs 26.0 and 28.0 for the other two scenes, **26.0 for
the empty-noise volume**, and 74-82 for the same volumes with painted shafts. Rule outcome: MIXED
(neither surface-correlated nor taller). Stated plainly without adding a story: the 02-08 blobs are exactly
as squat as those of pure noise; the near-miss is not explained by surface content, and nothing in it
is shaft-shaped. It remains reported, not explained.

## 3. What this means (honest reading)

- The identity check confirms the mechanism already on record: a tomogram column is its tile's
  trajectory energy (ρ = 1.00 everywhere). A streak = a tile with a large random-walk excursion.
- What we have now learned is that, at Giza, **which tiles get large excursions is not predicted by
  surface brightness, texture or registration quality** — and the real scenes' ρ values sit in the same
  ~0 band as the empty-noise volume. That is what scatter from the random walk itself would look like.
  That reading is an interpretation, not tested here (see §4).
- A REJECTED outcome was pre-declared as *not* evidence of buried structure: it leaves the streaks
  unexplained by these three surface properties, nothing more. We withdraw the "surface-driven"
  wording used in RESULTS_PRESS_IMAGES §5 and the chat.
- The C.4 step-1 verdict (0/8, 4/8, 0/8) is unchanged (F.6).

## 4. Candidate next test (not run; would need its own pre-registration)
"Streak statistics indistinguishable from the empty-noise volume": compare the distribution of S (e.g.
top-decile/median ratio, spatial autocorrelation length) between each real crop and matched nulls. It is
post hoc relative to this result, so it must be pre-registered before it is computed.

## 5. Limitation noticed after the run (not acted on)
N2 is nearly saturated across real and null volumes (26-28), so the elongation arm mainly separates
"painted shaft" from "not"; it could not have distinguished subtler shape differences. Recorded, rule
unchanged.
