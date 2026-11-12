"""Test P (pre-registered 12 Nov 2026): fixed list of FAKE three-level shaft targets.

Written and committed BEFORE any Test P tomogram exists. Deterministic (seed below).
Each fake target = a position on a 149-position line (1 m spacing) and three depths in metres.
Usage: python src/test_p_targets.py  ->  runs/test_p_fake_targets.json
"""
import json, os
import numpy as np

SEED = 20261112
N = 200
LINE_LEN = 149          # positions, ~1 m spacing (same as the line shown in the video)
EDGE = 10               # keep targets this far from the line ends
DEPTH_RANGE = (5.0, 40.0)
MIN_SEP = 6.0           # metres between levels
REAL = {"name": "Osiris Shaft (Hawass survey levels quoted in the video)", "depths_m": [10.0, 22.0, 33.0]}

def make():
    rng = np.random.default_rng(SEED)
    out = []
    while len(out) < N:
        d = np.sort(rng.uniform(*DEPTH_RANGE, size=3))
        if np.min(np.diff(d)) < MIN_SEP:
            continue
        out.append({"id": len(out), "position": int(rng.integers(EDGE, LINE_LEN - EDGE)),
                    "depths_m": [round(float(x), 1) for x in d]})
    return out

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "runs", "test_p_fake_targets.json")
    json.dump({"seed": SEED, "n": N, "line_len": LINE_LEN, "edge": EDGE, "depth_range_m": DEPTH_RANGE,
               "min_sep_m": MIN_SEP, "real_target": REAL, "fake_targets": make()}, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path))
