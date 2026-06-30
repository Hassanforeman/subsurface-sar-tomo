#!/usr/bin/env python3
"""
steering_stress_test.py — stress-test the tomogram inversion against signature
model-mismatch and grid coverage. Pure NumPy; no sarpy/data needed.

WHY THIS EXISTS
---------------
tomogram.py's positive control injects cos(Kz*z) — exactly the tone the matched
filter is built to recover. That proves SNR/conditioning but NOT robustness to a
real signal whose *shape* differs from the steering assumption. This script probes
that boundary directly, and documents three demonstrated blind spots:

  (1) heavy sub-cycle damping (lossy cavity ring-down)  -> MISSED (contrast < gate)
  (2) reflector beyond the searched depth grid          -> CONFIDENT FALSE PEAK at the
      wrong shallow depth (high contrast), and the look-shuffle null does NOT catch it
  (3) very shallow / sub-resolution low frequency       -> mislocated to the surface edge

Finding (2) is a real hole in the current pipeline: a true reflector outside the
modeled depth range can alias into a confident, high-contrast band that passes the
null test. The fix is a GRID-STABILITY guard (see assess_grid_stability): a real peak
is stable as the depth grid is widened/shifted; an aliased one moves.

Run:
    python3 src/steering_stress_test.py
"""
import numpy as np

DZ = 5.0  # must match tomogram.py


def steering(n, zg):
    dKz = 2 * np.pi / (n * DZ)
    Kz = np.arange(n) * dKz
    return np.exp(1j * np.outer(Kz, zg)), Kz


def analytic1d(v):
    N = len(v); V = np.fft.fft(v); h = np.zeros(N)
    if N % 2 == 0:
        h[0] = 1; h[N // 2] = 1; h[1:N // 2] = 2
    else:
        h[0] = 1; h[1:(N + 1) // 2] = 2
    return np.fft.ifft(V * h)


def invert(resid, A):
    return np.abs(A.conj().T @ analytic1d(resid)) ** 2


def contrast(T):
    p = T.sum(0)
    return p.max() / np.median(p)


def null(obs, zg, rng):
    A, _ = steering(obs.shape[1], zg)
    sh = np.array([r[rng.permutation(len(r))] for r in obs])
    return np.array([invert(r, A) for r in sh])


def _run(signal_fn, z_true, zg, A, Kz, nP, rng, label, gate=5.0):
    obs = 0.02 * rng.standard_normal((nP, len(Kz)))
    for p in range(nP):
        obs[p] += signal_fn(Kz, z_true)
    T = np.array([invert(r, A) for r in obs])
    Tn = null(obs, zg, rng)
    zrec = zg[np.argmax(T.sum(0))]
    cr, cn = contrast(T), contrast(Tn)
    ok = abs(zrec - z_true) <= 2 * DZ and cr > gate * cn
    flag = "RECOVERED" if ok else "MISSED/ALIASED"
    print(f"  {label:46s} z_rec={zrec:5.1f} (true {z_true:5.1f})  "
          f"contrast {cr:5.1f}x / {cn:4.1f}x  -> {flag}")
    return zrec, cr, cn


def assess_gridwidth_stability(z_true, nL, nP, rng, widths=(1.0, 1.5, 2.5)):
    """NEGATIVE RESULT (kept on purpose): widening the depth-search grid does NOT
    discriminate a real reflector from an off-grid alias — the alias is fixed by the
    look-index sampling, not the grid extent, so both look 'stable'. Do not use this
    as a guard."""
    zrecs = []
    for w in widths:
        zg = np.linspace(0, w * nL * DZ / 2, 400)
        A, Kz = steering(nL, zg)
        obs = 0.02 * rng.standard_normal((nP, nL))
        for p in range(nP):
            obs[p] += np.cos(Kz * z_true)
        T = np.array([invert(r, A) for r in obs])
        zrecs.append(zg[np.argmax(T.sum(0))])
    return zrecs, float(np.std(zrecs))


def assess_look_stability(z_true, nP, rng, look_counts=(9, 11, 15, 21, 31)):
    """THE WORKING GUARD: vary the number of sub-apertures. A real, in-range reflector
    holds its recovered depth; an out-of-range/aliased one jumps around until the
    valid range (0, nL*DZ/2) finally covers it. Large spread => artifact/out-of-range."""
    zrecs = []
    for nL in look_counts:
        zg = np.linspace(0, nL * DZ / 2, 400)
        A, Kz = steering(nL, zg)
        obs = 0.02 * rng.standard_normal((nP, nL))
        for p in range(nP):
            obs[p] += np.cos(Kz * z_true)
        T = np.array([invert(r, A) for r in obs])
        zrecs.append(round(float(zg[np.argmax(T.sum(0))]), 1))
    return zrecs, float(np.std(zrecs))


def main():
    rng = np.random.default_rng(0)
    nP, nL = 24, 11
    zg = np.linspace(0, nL * DZ / 2, 300)
    A, Kz = steering(nL, zg)
    z = 0.7 * zg[-1]

    print("A. Signature model-mismatch (true reflector ON-grid at z=%.1f):" % z)
    _run(lambda K, z: np.cos(K * z), z, zg, A, Kz, nP, rng, "1. matched tone [current positive control]")
    _run(lambda K, z: np.cos(K * z) * np.exp(-1.5 * np.arange(len(K)) / len(K)), z, zg, A, Kz, nP, rng, "2. moderately damped resonance")
    _run(lambda K, z: np.cos(K * z * (1 + 0.6 * np.arange(len(K)) / len(K))), z, zg, A, Kz, nP, rng, "3. chirped / dispersive")
    _run(lambda K, z: np.cos(K * z + 4.0 * (np.arange(len(K)) / len(K)) ** 2), z, zg, A, Kz, nP, rng, "4. quadratic-phase")
    _run(lambda K, z: np.cos(K * z) * np.exp(-4.0 * np.arange(len(K)) / len(K)), z, zg, A, Kz, nP, rng, "5. HEAVY sub-cycle damping")
    _run(lambda K, z: np.cos(K * z * 0.15), z, zg, A, Kz, nP, rng, "6. very shallow / sub-resolution")

    print("\nB. Grid-coverage failure (true reflector OFF-grid, beyond searched depth):")
    z_off = 1.8 * zg[-1]
    obs = 0.02 * rng.standard_normal((nP, nL))
    for p in range(nP):
        obs[p] += np.cos(Kz * z_off)
    T = np.array([invert(r, A) for r in obs]); Tn = null(obs, zg, rng)
    print(f"  off-grid reflector (true z={z_off:.1f}): pipeline reports z_rec="
          f"{zg[np.argmax(T.sum(0))]:.1f} at contrast {contrast(T):.1f}x / null {contrast(Tn):.1f}x")
    print("  -> CONFIDENT FALSE PEAK at wrong depth; the null test does NOT catch it.")

    print("\nC. Grid-WIDTH stability — the OBVIOUS guard that FAILS (negative result):")
    zr_real, sp_real = assess_gridwidth_stability(z, nL, nP, rng)
    zr_alias, sp_alias = assess_gridwidth_stability(1.8 * zg[-1], nL, nP, rng)
    print(f"  real on-grid reflector across grid widths:  {np.round(zr_real,1).tolist()}  spread={sp_real:.2f}")
    print(f"  off-grid (aliased) reflector across widths: {np.round(zr_alias,1).tolist()}  spread={sp_alias:.2f}")
    print("  -> UNRELIABLE: the matched filter is periodic in z, so widening the grid just")
    print("     lets argmax jump between replicas — depth may stay put OR leap, depending on")
    print("     incidental grid extent. Not a dependable discriminator.")

    print("\nD. Sub-aperture-COUNT stability — the guard that WORKS:")
    zr_in, sp_in = assess_look_stability(19.0, nP, rng)
    zr_deep, sp_deep = assess_look_stability(70.0, nP, rng)
    print(f"  in-range reflector (z=19) vs look count:    {zr_in}  spread={sp_in:.1f}")
    print(f"  deep reflector (z=70, out of range small N): {zr_deep}  spread={sp_deep:.1f}")
    print("  -> a peak whose depth JUMPS as you change the number of looks is an")
    print("     artifact / out-of-range; a real in-range reflector holds its depth.")


if __name__ == "__main__":
    main()
