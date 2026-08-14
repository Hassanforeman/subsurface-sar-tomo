#!/usr/bin/env python3
"""
guard_attack.py — adversarial search for a filter that defeats BOTH criteria.

`guard_robustness.py` screened 137 per-patch operators and none produced a false
detection. That is a survey, not a proof. This script does what a determined
referee would do: optimise directly for the failure.

Objective: find a per-patch FIR kernel that simultaneously
    (1) drives the contrast ratio above 5, AND
    (2) pushes the reported peak beyond the 2-cell surface guard,
on an input containing no scene. Either condition alone is already known to be
achievable. The paper's position requires that they cannot be achieved together.

Three stages: broad random screen, refine the survivors, then hill-climb the best
candidates. If a kernel exists in this family, this should find it.
"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tomogram import (DZ_TARGET, tomogram_from_observations, contrast, alignment_null)
from guard_robustness import fir

ap = argparse.ArgumentParser()
ap.add_argument("--obs", default="runs/obs_noise_c768_p64_s12_n11.npy")
ap.add_argument("--n-patch", type=int, default=24)
ap.add_argument("--screen-blocks", type=int, default=12)
ap.add_argument("--screen-perm", type=int, default=8)
ap.add_argument("--final-blocks", type=int, default=60)
ap.add_argument("--final-perm", type=int, default=32)
ap.add_argument("--n-screen", type=int, default=4000)
ap.add_argument("--klen", type=int, default=5)
ap.add_argument("--guard-cells", type=float, default=2.0)
ap.add_argument("--hill-iters", type=int, default=400)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--out", default="runs/guard_attack.json")
a = ap.parse_args()

OBS = np.load(a.obs)
n_look = OBS.shape[1]
zgrid = np.linspace(0, n_look * DZ_TARGET / 2, 300)
cells = zgrid / DZ_TARGET
rng = np.random.default_rng(a.seed)

SCREEN = [OBS[rng.choice(len(OBS), a.n_patch, replace=False)] for _ in range(a.screen_blocks)]
FINAL = [OBS[rng.choice(len(OBS), a.n_patch, replace=False)] for _ in range(a.final_blocks)]


def score(k, blocks, n_perm):
    R, P = [], []
    for b, blk in enumerate(blocks):
        o = fir(blk, k)
        if not np.all(np.isfinite(o)) or np.allclose(o, 0):
            return None
        T = tomogram_from_observations(o, zgrid)
        ca = float(np.median(alignment_null(o, zgrid, np.random.default_rng(500 + b),
                                            n_perm=n_perm)))
        R.append(float(contrast(T)) / (ca + 1e-12))
        P.append(float(cells[int(np.argmax(T.sum(0)))]))
    R, P = np.array(R), np.array(P)
    return dict(ratio=float(np.median(R)), peak=float(np.median(P)),
                frac_false=float(np.mean((R > 5) & (P > a.guard_cells))),
                frac5=float(np.mean(R > 5)), fracunp=float(np.mean(P > a.guard_cells)))


def objective(s):
    """Reward getting BOTH. Positive only if both thresholds are cleared."""
    if s is None:
        return -9e9
    return min(s["ratio"] / 5.0, s["peak"] / a.guard_cells)


print(f"stage 1: screening {a.n_screen} random kernels (length <= {a.klen})", flush=True)
cands = []
for i in range(a.n_screen):
    L = int(rng.integers(2, a.klen + 1))
    k = rng.normal(0, 1, L)
    k /= (np.abs(k).sum() + 1e-12)
    s = score(k, SCREEN, a.screen_perm)
    if s is not None:
        cands.append((objective(s), k, s))
    if (i + 1) % 1000 == 0:
        best = max(c[0] for c in cands) if cands else -9
        print(f"  {i+1}/{a.n_screen}  best objective so far {best:.3f} "
              f"(needs >= 1.0 on BOTH to break the rule)", flush=True)

cands.sort(key=lambda t: -t[0])
print(f"\nstage 2: re-scoring top 40 at {a.final_blocks} blocks", flush=True)
ref = []
for obj, k, _ in cands[:40]:
    s = score(k, FINAL, a.final_perm)
    if s:
        ref.append((objective(s), k, s))
ref.sort(key=lambda t: -t[0])

print(f"\nstage 3: hill-climbing the top 3 for {a.hill_iters} iterations each", flush=True)
best = []
for obj0, k0, s0 in ref[:3]:
    k, s, obj = k0.copy(), s0, obj0
    step = 0.20
    for it in range(a.hill_iters):
        kk = k + rng.normal(0, step, len(k))
        kk /= (np.abs(kk).sum() + 1e-12)
        ss = score(kk, SCREEN, a.screen_perm)
        oo = objective(ss)
        if oo > obj:
            k, s, obj = kk, ss, oo
        if (it + 1) % 100 == 0:
            step *= 0.6
    s = score(k, FINAL, a.final_perm)
    best.append((objective(s), k, s))
    print(f"  climbed to objective {objective(s):.3f}  ratio {s['ratio']:.2f}  "
          f"peak {s['peak']:.2f}", flush=True)

best.sort(key=lambda t: -t[0])
allc = best + ref[:10]
allc.sort(key=lambda t: -t[0])

print("\n" + "=" * 84)
print("ADVERSARIAL SEARCH FOR A FILTER THAT DEFEATS BOTH CRITERIA")
print(f"input: no scene. {a.n_screen} screened + hill-climbing. guard = {a.guard_cells} cells")
print("=" * 84)
print(f"{'kernel':<44}{'ratio':>8}{'peak':>8}{'>5x':>7}{'unpin':>8}{'FALSE':>8}")
print("-" * 84)
for obj, k, s in allc[:12]:
    ks = "[" + ", ".join(f"{x:+.3f}" for x in k) + "]"
    print(f"{ks:<44}{s['ratio']:>8.2f}{s['peak']:>8.2f}{100*s['frac5']:>6.0f}%"
          f"{100*s['fracunp']:>7.0f}%{100*s['frac_false']:>7.0f}%")
print("-" * 84)
win = [t for t in allc if t[2]["frac_false"] > 0]
if win:
    print(f"*** GUARD DEFEATED *** best kernel gives "
          f"{100*win[0][2]['frac_false']:.0f}% false detections on empty data")
else:
    bo = allc[0]
    print(f"No kernel achieved both. Best joint objective {bo[0]:.3f} (needs 1.0):")
    print(f"  ratio {bo[2]['ratio']:.2f} (needs >5) and peak {bo[2]['peak']:.2f} "
          f"cells (needs >{a.guard_cells})")
    print("  The two requirements appear to be in tension rather than independent.")

json.dump(dict(n_screen=a.n_screen, klen=a.klen, guard_cells=a.guard_cells,
               final_blocks=a.final_blocks, final_perm=a.final_perm,
               defeated=bool(win),
               best=[dict(kernel=[float(x) for x in k], **s) for _, k, s in allc[:12]]),
          open(a.out, "w"), indent=1)
print(f"\nsummary -> {a.out}")
