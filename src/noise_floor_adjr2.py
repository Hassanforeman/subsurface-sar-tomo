"""What adjusted R^2 does pure noise give under Seyfzadeh's published settings?
(K vectors, every window of W consecutive vectors, elliptical sin/cos fit with intercept on two
components, best window kept.)  White noise and AR(1) noise.  No radar data involved.
Usage: python src/noise_floor_adjr2.py  ->  runs/noise_floor_adjr2.json
"""
import json, os
import numpy as np

def best_window_adjr2(q, W, cycles):
    """q[T, K, 2]; cycles = array of frequencies in cycles per window. Returns [T, len(cycles)]."""
    T, K, _ = q.shape
    n = np.arange(K)
    def wsum(x):
        cs = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(x, axis=-1)], axis=-1)
        return cs[..., W:] - cs[..., :-W]
    q64 = q.transpose(0, 2, 1).astype(np.float64)
    S0 = wsum(q64)
    SST = (wsum(q64 ** 2) - S0 ** 2 / W).sum(axis=1)
    out = np.zeros((T, len(cycles)))
    for j, c in enumerate(cycles):
        th = 2 * np.pi * c * n / W
        co, si = np.cos(th), np.sin(th)
        nw = K - W + 1
        G = np.empty((nw, 3, 3))
        G[:, 0, 0] = W
        G[:, 0, 1] = G[:, 1, 0] = wsum(co); G[:, 0, 2] = G[:, 2, 0] = wsum(si)
        G[:, 1, 1] = wsum(co * co); G[:, 2, 2] = wsum(si * si); G[:, 1, 2] = G[:, 2, 1] = wsum(co * si)
        Gi = np.linalg.inv(G)
        b = np.stack([S0, wsum(q64 * co), wsum(q64 * si)], axis=-1)
        beta = np.einsum("wij,tcwj->tcwi", Gi, b)
        ssfit = (b * beta).sum(-1).sum(1) - (S0 ** 2 / W).sum(1)
        adj = 1 - (1 - ssfit / SST) * (2 * W - 1) / (2 * W - 6)
        out[:, j] = adj.max(axis=1)
    return out

def ar1(rng, shape, rho):
    e = rng.standard_normal(shape)
    x = np.empty(shape)
    x[:, 0] = e[:, 0]
    for k in range(1, shape[1]):
        x[:, k] = rho * x[:, k - 1] + np.sqrt(1 - rho ** 2) * e[:, k]
    return x

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    res = {}
    for name, K, W in (("K3208_W1900 (Western Cemetery model)", 3208, 1900), ("K3360_W1990 (Osiris scan 3)", 3360, 1990),
                       ("K295_W175 (Osiris scan 1)", 295, 175)):
        T = 40 if K > 1000 else 300
        cyc = rng.uniform(3, min(W / 4, 400), size=60 if K > 1000 else 200)
        for rho in (0.0, 0.9):
            q = ar1(rng, (T, K, 2), rho) if rho else rng.standard_normal((T, K, 2))
            a = best_window_adjr2(q, W, cyc).ravel()
            res[f"{name} rho={rho}"] = dict(cells=int(a.size), share_positive=float((a > 0).mean()),
                                            median=float(np.median(a)), p90=float(np.percentile(a, 90)),
                                            p99=float(np.percentile(a, 99)), max=float(a.max()))
            print(name, rho, res[f"{name} rho={rho}"], flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "noise_floor_adjr2.json"), "w"), indent=1)
