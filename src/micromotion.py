#!/usr/bin/env python3
"""
micromotion.py — turn raw sub-aperture looks into a TRUSTWORTHY residual-motion
observable. This is the refinement that fixes the noisy global-shift curve we saw
on real Bingham data.

Three upgrades over a naive global cross-correlation:
  1. ADJACENT-PAIR   measure shift between consecutive looks (high spectral overlap
                     -> reliable), then cumulatively sum to an absolute trajectory.
  2. COHERENCE       score every look-pair; low coherence = untrustworthy, flag it.
  3. DETREND         remove the expected geometric ramp (azimuth-Doppler coupling),
                     leaving only the genuine residual motion the inverter wants.

Usage
-----
python3.13 src/micromotion.py --selftest
python3.13 src/micromotion.py --sicd data/2024-01-12-04-09-18_UMBRA-05_SICD.nitf

Deps: numpy, matplotlib  (sarpy only for --sicd)
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subaperture import decompose_subapertures, subpixel_shift, fourier_shift


# ---------------------------------------------------------------------------
def match_score(s1, s2):
    """Registration quality in [0,1]: normalised cross-correlation of the (aligned)
    look MAGNITUDES. High = the two looks image the same structure reliably; low =
    decorrelated / untrustworthy. (Honest name: this is magnitude match quality, not
    interferometric phase coherence, which is ill-defined across Doppler sub-bands.)"""
    x = np.abs(s1).ravel().astype(float)
    y = np.abs(s2).ravel().astype(float)
    x -= x.mean(); y -= y.mean()
    return float(abs((x @ y) / (np.sqrt((x @ x) * (y @ y)) + 1e-12)))


def adjacent_trajectory(looks):
    """looks: (N, h, w) complex patches. Returns absolute azimuth trajectory and
    per-pair registration quality using consecutive (high-overlap) look pairs."""
    N = len(looks)
    inc = np.zeros(N)
    coh = np.ones(N)
    for k in range(1, N):
        dy, dx = subpixel_shift(np.abs(looks[k - 1]), np.abs(looks[k]))
        inc[k] = dx
        aligned = fourier_shift(looks[k], -dy, -dx)   # align before scoring
        coh[k] = match_score(looks[k - 1], aligned)
    return np.cumsum(inc), coh                       # absolute trajectory, match quality


def detrend(traj, deg=1):
    x = np.arange(len(traj))
    return traj - np.polyval(np.polyfit(x, traj, deg), x)


# ---------------------------------------------------------------------------
# LRSD denoising — Biondi's low-rank + sparse decomposition (ship/dam papers).
# Robust PCA via Principal Component Pursuit (inexact ALM). Dependency-free
# (no cvxpy): separates a coherent low-rank vibration component L from sparse
# decorrelation spikes/outliers S, given a stack of per-patch trajectories M.
# ---------------------------------------------------------------------------
def lrsd_denoise(M, lam=None, mu=None, n_iter=500, tol=1e-7):
    """M (n_patch, n_look) real -> (L, S) with M ≈ L + S, L low-rank, S sparse.
    Returns the cleaned low-rank coherent component L and the sparse residual S."""
    M = np.asarray(M, float)
    if M.ndim != 2 or min(M.shape) < 2:
        return M.copy(), np.zeros_like(M)
    m, n = M.shape
    if lam is None:
        lam = 1.0 / np.sqrt(max(m, n))
    norm2 = np.linalg.norm(M, 2)                       # spectral norm
    if mu is None:
        mu = 1.25 / (norm2 + 1e-12)
    mu_bar, rho = mu * 1e7, 1.5
    Y = M / max(norm2, np.abs(M).max() / lam + 1e-12)  # dual init
    L = np.zeros_like(M); S = np.zeros_like(M)
    Mfro = np.linalg.norm(M, "fro") + 1e-12
    for _ in range(n_iter):
        U, sig, Vt = np.linalg.svd(M - S + Y / mu, full_matrices=False)
        sig = np.maximum(sig - 1.0 / mu, 0.0)          # singular-value threshold -> low rank
        L = (U * sig) @ Vt
        T = M - L + Y / mu
        S = np.sign(T) * np.maximum(np.abs(T) - lam / mu, 0.0)   # soft threshold -> sparse
        Z = M - L - S
        Y = Y + mu * Z
        mu = min(mu * rho, mu_bar)
        if np.linalg.norm(Z, "fro") / Mfro < tol:
            break
    return L, S


# ---------------------------------------------------------------------------
def selftest():
    rng = np.random.default_rng(1)
    N, P = 9, 96
    base = np.fft.ifft2(np.fft.fft2(
        rng.standard_normal((P, P)) + 1j*rng.standard_normal((P, P))) * _lp(P, 0.3))

    # Known truth: a geometric linear RAMP + a small sinusoidal RESIDUAL motion
    ramp = 1.5 * np.arange(N)
    resid_true = 0.35 * np.sin(2*np.pi*2*np.arange(N)/N)
    total = ramp + resid_true
    looks = np.array([fourier_shift(base, 0, total[k]) for k in range(N)])

    print("[A] recover residual motion after detrending the ramp:")
    traj, coh = adjacent_trajectory(looks)
    resid_est = detrend(traj, deg=1)
    resid_ref = detrend(total - total[0], deg=1)      # truth, same detrend
    rms = np.sqrt(np.mean((resid_est - resid_ref)**2))
    okA = rms < 0.08
    print(f"   residual RMS error = {rms:.3f} px  -> {'PASS' if okA else 'FAIL'}")
    print(f"   est  {np.round(resid_est,2).tolist()}")
    print(f"   true {np.round(resid_ref,2).tolist()}")

    print("\n[B] registration quality flags a decorrelated look:")
    bad = looks.copy()
    bad[4] = (rng.standard_normal((P, P)) + 1j*rng.standard_normal((P, P)))  # destroy look 4
    _, coh_b = adjacent_trajectory(bad)
    clean_min = coh_b[[1, 2, 3, 6, 7, 8]].min()       # pairs not touching look 4
    bad_max = coh_b[[4, 5]].max()                      # pairs touching look 4
    okB = clean_min > 0.8 and bad_max < 0.4
    print(f"   clean-pair quality min = {clean_min:.2f}; "
          f"decorrelated-pair quality max = {bad_max:.2f}  -> {'PASS' if okB else 'FAIL'}")

    print("\n[C] LRSD separates coherent vibration from sparse spikes:")
    # Physical model: a dominant shared ambient vibration mode = rank-1 coherent field
    # across patches, contaminated by sparse decorrelation spikes.
    nP, nL = 24, 11
    U = rng.standard_normal((nP, 1)); V = rng.standard_normal((1, nL))
    L_true = U @ V
    S_true = np.zeros((nP, nL))
    idx = rng.choice(nP * nL, size=nP, replace=False)        # ~1 spike per patch
    S_true.flat[idx] = rng.standard_normal(nP) * 6 * L_true.std()
    M = L_true + S_true
    L_est, S_est = lrsd_denoise(M)
    err_L = np.linalg.norm(L_est - L_true) / np.linalg.norm(L_true)
    caught = np.mean((np.abs(S_est) > 1e-3)[S_true != 0])     # fraction of true spikes flagged
    okC = err_L < 0.20 and caught > 0.8
    print(f"   low-rank recovery err = {err_L:.3f}; spikes caught = {caught:.0%}  -> {'PASS' if okC else 'FAIL'}")

    print("\n" + "="*56)
    print("RESIDUAL-MOTION SELF-TEST:", "PASS" if (okA and okB and okC) else "FAIL")
    print("="*56)


def _lp(N, frac):
    f = np.fft.fftfreq(N)
    return ((np.abs(f)[:, None] < frac) & (np.abs(f)[None, :] < frac)).astype(float)


# ---------------------------------------------------------------------------
def run_on_sicd(path, crop=512, n_sub=9, patch=128, overlap=0.8):
    from sarpy.io.complex.converter import open_complex
    reader = open_complex(path)
    R, C = reader.data_size
    r0, c0 = R//2 - crop//2, C//2 - crop//2
    print(f"Loading {crop}x{crop} crop, decomposing into {n_sub} looks (overlap {overlap}) ...")
    slc = reader[r0:r0+crop, c0:c0+crop]
    looks, cents = decompose_subapertures(slc, n_sub=n_sub, overlap=overlap, axis=1)

    h0 = crop//2 - patch//2
    looks_patch = looks[:, h0:h0+patch, h0:h0+patch]
    traj, coh = adjacent_trajectory(looks_patch)
    resid = detrend(traj, deg=2)

    print(f"  registration quality per adjacent pair: {np.round(coh,2).tolist()}")
    print(f"  raw absolute trajectory (px): {np.round(traj,2).tolist()}")
    print(f"  residual motion after detrend (px): {np.round(resid,3).tolist()}")
    print(f"  residual RMS = {np.sqrt(np.mean(resid**2)):.3f} px  "
          f"(stable rock -> expect small)")
    _plot(cents, traj, coh, resid, os.path.basename(path))


def _plot(cents, traj, coh, resid, name):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(cents, traj, "o-"); ax[0].set_title("Raw absolute trajectory")
    ax[0].set_xlabel("Doppler centroid"); ax[0].set_ylabel("shift (px)")
    ax[1].plot(cents, coh, "o-"); ax[1].axhline(0.5, color='r', ls='--', alpha=.5)
    ax[1].set_title("Registration quality per look-pair (red=floor)"); ax[1].set_ylim(0, 1)
    ax[1].set_xlabel("Doppler centroid")
    ax[2].plot(cents, resid, "o-"); ax[2].axhline(0, color='k', alpha=.3)
    ax[2].set_title("Residual motion (detrended) = the observable")
    ax[2].set_xlabel("Doppler centroid"); ax[2].set_ylabel("residual (px)")
    os.makedirs("runs", exist_ok=True)
    out = f"runs/micromotion_{name}.png"
    fig.tight_layout(); fig.savefig(out, dpi=120); print(f"  figure -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicd")
    ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--n-sub", type=int, default=9)
    args = ap.parse_args()
    if args.sicd:
        run_on_sicd(args.sicd, crop=args.crop, n_sub=args.n_sub)
    else:
        selftest()
