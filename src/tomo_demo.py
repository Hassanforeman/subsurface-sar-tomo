#!/usr/bin/env python3
"""
tomo_demo.py — Phase-0 engine validation: the tomographic INVERSION core,
tested against a KNOWN answer before we ever trust it on real data.

This is the heart of Biondi-style tomography in its purest form. Across the
sub-apertures (here abstracted as `k` "looks" with vertical wavenumbers Kz), a
reflector at depth z imprints the phase signature  a_i(z) = exp(j * Kz_i * z).
Stacking those signatures into a STEERING MATRIX A(z) and inverting the
observations Y = A(z) h(z) recovers a reflectivity-vs-depth profile h(z).

What this script proves (or disproves), with no hand-waving:
  1. PRINCIPLE  — three estimators (Bartlett/matched-filter, Capon/MVDR, MUSIC)
                  recover sources placed at KNOWN depths, within ~one resolution cell.
  2. FAILURE    — if the per-look observable is REAL-valued, the tomogram is
                  mirror-symmetric in depth (the ghost-twin artifact the critiques flag).
  3. FIX        — an analytic-signal step along the aperture removes the ghosts.
  4. NULL TEST  — shuffling the data destroys the peaks, so what we detect is signal,
                  not pareidolia.

Run:  python3.13 src/tomo_demo.py
Deps: numpy, scipy, matplotlib   (all installed already)
Output: console PASS/FAIL + figure runs/tomo_demo.png
"""
import os
import numpy as np

# ----------------------------------------------------------------------------
# Model setup
# ----------------------------------------------------------------------------
rng = np.random.default_rng(42)

K          = 48           # number of sub-apertures / "looks"
DZ_TARGET  = 5.0          # design Rayleigh depth resolution (metres)
dKz        = 2*np.pi / (K * DZ_TARGET)     # wavenumber step -> sets resolution
Kz         = np.arange(K) * dKz            # vertical wavenumbers across the aperture
Z_MAX      = 2*np.pi / dKz                  # unambiguous depth span = K*DZ_TARGET
L          = 200          # snapshots (independent range cells) for covariance
NOISE_VAR  = 0.05         # additive noise power

# Ground truth: three reflectors at KNOWN depths with KNOWN powers.
# (Kept within Z_MAX/2 so the real-valued case is fold-free and the analytic fix is clean.)
D_TRUE     = np.array([30.0, 65.0, 100.0])      # metres
P_TRUE     = np.array([1.0, 0.6, 0.4])          # powers
S          = len(D_TRUE)

def steer(z):
    """Steering matrix A(z): column per depth, row per look. Shape (K, len(z))."""
    z = np.atleast_1d(z)
    return np.exp(1j * np.outer(Kz, z))         # (K, Z)

# ----------------------------------------------------------------------------
# Synthesise observations  Y = A(d_true) x + noise   (classic source model)
# ----------------------------------------------------------------------------
def make_observations(real_only=False):
    A_true = steer(D_TRUE)                        # (K, S)
    x = (rng.standard_normal((S, L)) + 1j*rng.standard_normal((S, L))) / np.sqrt(2)
    x *= np.sqrt(P_TRUE)[:, None]                 # per-source amplitude
    n = np.sqrt(NOISE_VAR/2) * (rng.standard_normal((K, L)) + 1j*rng.standard_normal((K, L)))
    Y = A_true @ x + n                            # (K, L)
    if real_only:
        Y = Y.real.astype(complex)                # drop the imaginary part -> real observable
    return Y

def covariance(Y):
    return (Y @ Y.conj().T) / Y.shape[1]          # (K, K) sample covariance

# ----------------------------------------------------------------------------
# Estimators (spectral, scanned over a depth grid)
# ----------------------------------------------------------------------------
def bartlett(R, zgrid):
    A = steer(zgrid)                              # (K, G)
    return np.real(np.einsum('kg,kj,jg->g', A.conj(), R, A))

def capon(R, zgrid, load=1e-2):
    Rinv = np.linalg.inv(R + load*np.trace(R)/K*np.eye(K))
    A = steer(zgrid)
    denom = np.real(np.einsum('kg,kj,jg->g', A.conj(), Rinv, A))
    return 1.0 / np.maximum(denom, 1e-12)

def music(R, zgrid, n_src=S):
    w, V = np.linalg.eigh(R)                      # ascending eigenvalues
    En = V[:, :K - n_src]                         # noise subspace
    A = steer(zgrid)
    proj = np.sum(np.abs(En.conj().T @ A)**2, axis=0)
    return 1.0 / np.maximum(proj, 1e-12)

# ----------------------------------------------------------------------------
# Scoring against ground truth
# ----------------------------------------------------------------------------
def analytic_signal(x):
    """Hilbert/analytic signal along axis 0 (FFT-based, numpy only)."""
    N = x.shape[0]
    X = np.fft.fft(x, axis=0)
    h = np.zeros(N)
    if N % 2 == 0:
        h[0] = 1; h[N//2] = 1; h[1:N//2] = 2
    else:
        h[0] = 1; h[1:(N+1)//2] = 2
    return np.fft.ifft(X * h[:, None], axis=0)

def _find_peaks(s, height, min_dist):
    """Simple local-maxima finder with a min-distance rule (numpy only)."""
    interior = np.where((s[1:-1] > s[:-2]) & (s[1:-1] >= s[2:]) & (s[1:-1] > height))[0] + 1
    if interior.size == 0:
        return np.array([], dtype=int), np.array([])
    order = interior[np.argsort(s[interior])[::-1]]
    chosen = []
    for c in order:
        if all(abs(c - ch) >= min_dist for ch in chosen):
            chosen.append(c)
    chosen = np.array(sorted(chosen), dtype=int)
    return chosen, s[chosen]

def top_peaks(spec, zgrid, n=S):
    s = spec / spec.max()
    idx, heights = _find_peaks(s, height=0.15, min_dist=int(2*DZ_TARGET/(zgrid[1]-zgrid[0])))
    if len(idx) == 0:
        return np.array([])
    order = np.argsort(heights)[::-1][:n]
    return np.sort(zgrid[idx[order]])

def score(name, spec, zgrid, tol=2*DZ_TARGET):
    peaks = top_peaks(spec, zgrid)
    ok = (len(peaks) == S) and np.all(np.abs(peaks - D_TRUE) <= tol)
    err = np.abs(peaks - D_TRUE).max() if len(peaks) == S else float('nan')
    print(f"  {name:9s}: peaks at {np.round(peaks,1).tolist()} m  "
          f"(truth {D_TRUE.tolist()})  max err {err:.1f} m  -> {'PASS' if ok else 'FAIL'}")
    return ok

# ----------------------------------------------------------------------------
# Run the four experiments
# ----------------------------------------------------------------------------
def main():
    os.makedirs("runs", exist_ok=True)
    zc = np.linspace(0, Z_MAX, 1500)              # one-sided depth grid
    zm = np.linspace(-Z_MAX/2, Z_MAX/2, 3000)     # symmetric half-span grid (mirror ghosts, no periodic replicas)

    print(f"Design resolution dz = {DZ_TARGET:.1f} m, unambiguous span = {Z_MAX:.0f} m, "
          f"K={K} looks, {L} snapshots, noise var {NOISE_VAR}\n")

    # 1) Proper complex data -> all three estimators should PASS
    print("[1] PRINCIPLE  (proper complex observations):")
    R = covariance(make_observations(real_only=False))
    p_bart, p_cap, p_mus = bartlett(R, zc), capon(R, zc), music(R, zc)
    ok1 = score("Bartlett", p_bart, zc) & score("Capon", p_cap, zc) & score("MUSIC", p_mus, zc)

    neg = zm < -2*DZ_TARGET
    pos = zm >  2*DZ_TARGET

    # 2) Real-only observable -> mirror-symmetry ghosts appear
    print("\n[2] FAILURE MODE  (real-valued observable -> mirror ghosts expected):")
    Rr = covariance(make_observations(real_only=True))
    p_mirror = bartlett(Rr, zm)
    ratio_before = p_mirror[neg].max() / p_mirror[pos].max()
    has_ghost = ratio_before > 0.7              # symmetric -> negative side ~ as strong as positive
    print(f"  negative/positive power ratio = {ratio_before:.2f}  "
          f"-> mirror ghosts present: {has_ghost} ({'as expected' if has_ghost else 'NOT reproduced'})")

    # 3) Analytic-signal fix along the aperture -> ghosts removed
    print("\n[3] FIX  (analytic signal along aperture removes ghosts):")
    Yr = make_observations(real_only=True)
    Ya = analytic_signal(Yr.real)                 # restore analytic (one-sided) signal
    p_fixed = bartlett(covariance(Ya), zm)
    ratio_after = p_fixed[neg].max() / p_fixed[pos].max()
    ghost_gone = ratio_after < 0.3                # negative side strongly suppressed
    pos_peaks = top_peaks(p_fixed[zm >= 0], zm[zm >= 0])
    print(f"  negative/positive power ratio = {ratio_after:.2f} (was {ratio_before:.2f}) "
          f"-> ghosts removed: {ghost_gone}")
    print(f"  positive-side peaks now at {np.round(pos_peaks,1).tolist()} m  (truth {D_TRUE.tolist()})")

    # 4) Null test -> shuffled data should have no coherent peaks
    print("\n[4] NULL TEST  (phase-randomised data -> no real structure):")
    Yn = make_observations(real_only=False)
    Yn = np.abs(Yn) * np.exp(1j*rng.uniform(-np.pi, np.pi, Yn.shape))  # destroy phase relations
    p_null = bartlett(covariance(Yn), zc)
    signal_contrast = p_bart.max() / np.median(p_bart)
    null_contrast = p_null.max() / np.median(p_null)
    print(f"  signal peak/median contrast = {signal_contrast:.1f}x ; "
          f"null = {null_contrast:.1f}x  -> "
          f"{'PASS (signal >> null)' if signal_contrast > 5*null_contrast else 'CHECK'}")

    _plot(zc, p_bart, p_cap, p_mus, zm, p_mirror, p_fixed, p_null)

    print("\n" + ("="*60))
    print("PHASE-0 GATE:", "PASS — inversion core validated, build on it."
          if ok1 and has_ghost and ghost_gone else
          "REVIEW — inspect runs/tomo_demo.png")
    print("="*60)


def _plot(zc, bart, cap, mus, zm, mirror, fixed, null):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))

    def norm(x): return x/np.max(x)
    a = ax[0, 0]
    a.plot(zc, norm(bart), label="Bartlett"); a.plot(zc, norm(cap), label="Capon")
    a.plot(zc, norm(mus), label="MUSIC")
    for d in D_TRUE: a.axvline(d, color='k', ls='--', alpha=.4)
    a.set_title("[1] Inversion recovers known depths"); a.set_xlabel("depth (m)")
    a.legend(); a.set_ylabel("norm. power")

    a = ax[0, 1]
    a.plot(zm, norm(mirror));
    for d in D_TRUE: a.axvline(d, color='g', ls='--', alpha=.5)
    for d in D_TRUE: a.axvline(-d, color='r', ls=':', alpha=.6)
    a.set_title("[2] Real observable -> mirror ghosts (red)"); a.set_xlabel("depth (m)")

    a = ax[1, 0]
    a.plot(zm, norm(fixed))
    for d in D_TRUE: a.axvline(d, color='g', ls='--', alpha=.5)
    a.set_title("[3] Analytic-signal fix -> ghosts gone"); a.set_xlabel("depth (m)")

    a = ax[1, 1]
    a.plot(zc, norm(bart), label="signal"); a.plot(zc, norm(null), label="null (shuffled)")
    a.set_title("[4] Null test: signal vs shuffled"); a.set_xlabel("depth (m)"); a.legend()

    fig.tight_layout(); fig.savefig("runs/tomo_demo.png", dpi=120)
    print("\n  figure -> runs/tomo_demo.png")


if __name__ == "__main__":
    main()
