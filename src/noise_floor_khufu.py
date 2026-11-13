"""Noise floor for the settings printed in the released Great Pyramid model (K=3360, W=1300).
Same method as src/noise_floor_adjr2.py (his ellipse gate and P run filter are NOT simulated).
Usage: python src/noise_floor_khufu.py -> runs/noise_floor_khufu.json
"""
import json, os
import numpy as np
from noise_floor_adjr2 import best_window_adjr2, ar1

if __name__ == "__main__":
    rng = np.random.default_rng(11)
    K, W, T = 3360, 1300, 40
    cyc = rng.uniform(3, min(W / 4, 400), size=60)
    res = {}
    for rho in (0.0, 0.5, 0.9):
        q = ar1(rng, (T, K, 2), rho) if rho else rng.standard_normal((T, K, 2))
        a = best_window_adjr2(q, W, cyc).ravel()
        res[f"K3360_W1300 rho={rho}"] = dict(cells=int(a.size), median=float(np.median(a)),
            p90=float(np.percentile(a, 90)), p99=float(np.percentile(a, 99)), max=float(a.max()))
        print(rho, res[f"K3360_W1300 rho={rho}"], flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "noise_floor_khufu.json"), "w"), indent=1)
