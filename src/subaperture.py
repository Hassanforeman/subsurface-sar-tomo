#!/usr/bin/env python3
"""
subaperture.py — the FRONT-END of the tomography engine.

Two operations, the bridge from a real SLC to the observations that tomo_demo.py's
inverter consumes:

  1. DECOMPOSE   split the azimuth (Doppler) spectrum of one complex SLC into N
                 overlapping sub-apertures = N "looks" at slightly different squint.
  2. TRACK       measure the sub-pixel shift of a patch between looks — this is the
                 micro-motion signal Biondi's method is built on.

Usage
-----
# Prove the shift estimator is correct (synthetic, no data/sarpy needed):
python3.13 src/subaperture.py --selftest

# Run on the real Bingham SICD (needs sarpy; large file -> uses a crop):
python3.13 src/subaperture.py --sicd data/2024-01-12-04-09-18_UMBRA-05_SICD.nitf

Deps: numpy, matplotlib  (sarpy only for the --sicd path)
"""
import argparse, os
import numpy as np


# ---------------------------------------------------------------------------
# 1. Sub-aperture decomposition (azimuth = Doppler axis)
# ---------------------------------------------------------------------------
def decompose_subapertures(slc, n_sub=7, overlap=0.5, axis=1):
    """Return array (n_sub, H, W) of complex sub-aperture images.

    Splits the spectrum along `axis` into n_sub overlapping Hann-windowed bands,
    each band -> one lower-resolution look at a different mean Doppler (squint).
    """
    slc = np.asarray(slc)
    N = slc.shape[axis]
    SP = np.fft.fftshift(np.fft.fft(slc, axis=axis), axes=axis)

    band = N / (n_sub - (n_sub - 1) * overlap)      # width of each sub-band (samples)
    step = band * (1 - overlap)
    looks, centroids = [], []
    for k in range(n_sub):
        c = band / 2 + k * step                     # band centre (sample index)
        lo, hi = int(round(c - band / 2)), int(round(c + band / 2))
        lo, hi = max(0, lo), min(N, hi)
        w = np.zeros(N)
        w[lo:hi] = np.hanning(hi - lo)              # taper -> lower sidelobes
        shape = [1, 1]; shape[axis] = N
        sub_sp = SP * w.reshape(shape)
        sub = np.fft.ifft(np.fft.ifftshift(sub_sp, axes=axis), axis=axis)
        looks.append(sub)
        centroids.append((lo + hi) / 2 - N / 2)     # Doppler centroid (rel. to centre)
    return np.array(looks), np.array(centroids)


# ---------------------------------------------------------------------------
# 2. Sub-pixel shift estimation (phase cross-correlation + parabolic refine)
# ---------------------------------------------------------------------------
def _parabolic(c, i):
    n = len(c)
    a, b, d = c[(i - 1) % n], c[i], c[(i + 1) % n]
    denom = (a - 2 * b + d)
    return 0.0 if denom == 0 else 0.5 * (a - d) / denom


def subpixel_shift(ref, img):
    """Estimate (dy, dx) such that img is shifted by (dy,dx) relative to ref."""
    F = np.fft.fft2(ref)
    G = np.fft.fft2(img)
    R = F * np.conj(G)
    R /= np.abs(R) + 1e-12                           # phase correlation (robust to brightness)
    corr = np.fft.ifft2(R).real
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    H, W = corr.shape
    # 1-D parabolic refinement along each axis through the peak
    dy = py + _parabolic(corr[:, px], py)
    dx = px + _parabolic(corr[py, :], px)
    # wrap to signed shift
    if dy > H / 2: dy -= H
    if dx > W / 2: dx -= W
    return -dy, -dx                                  # convention: shift of img relative to ref


def estimate_micromotion(subaps, ref_idx=0):
    """Azimuth/range shift of every look relative to a reference look."""
    ref = np.abs(subaps[ref_idx])
    out = []
    for s in subaps:
        out.append(subpixel_shift(ref, np.abs(s)))
    return np.array(out)                             # (n_sub, 2) -> [dy(range), dx(azimuth)]


# ---------------------------------------------------------------------------
# 3. Multichromatic analysis (MCA) — range/chirp sub-banding (patent master/slave)
# ---------------------------------------------------------------------------
# Biondi's patent (WO2024008365A1) builds a "range-Doppler sub-apertures large-matrix"
# for a master and slave band — i.e. it splits BOTH the chirp (range, axis=0) and the
# Doppler (azimuth, axis=1) spectra. We currently use Doppler only; MCA adds the range
# diversity axis, giving more independent observations to focus in depth.
def chirp_subbands(slc, n_chirp=3, overlap=0.5):
    """Split the RANGE (chirp) spectrum into n_chirp overlapping sub-bands (axis=0).
    Returns (n_chirp, H, W) complex range-frequency looks + their range centroids."""
    return decompose_subapertures(slc, n_sub=n_chirp, overlap=overlap, axis=0)


def multichromatic_subapertures(slc, n_chirp=3, n_sub=11,
                                overlap_chirp=0.5, overlap_dop=0.8):
    """MCA front-end. For each chirp (range) sub-band, form Doppler sub-apertures.
    Returns:
      looks   (n_chirp, n_sub, H, W) complex
      cents   (n_sub,) Doppler centroids (shared across chirp bands)
    Each (chirp, look) pair is one independent observation channel for the inverter."""
    chirp_looks, _ = chirp_subbands(slc, n_chirp=n_chirp, overlap=overlap_chirp)
    out, cents = [], None
    for cl in chirp_looks:
        looks, cents = decompose_subapertures(cl, n_sub=n_sub, overlap=overlap_dop, axis=1)
        out.append(looks)
    return np.array(out), cents


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fourier_shift(img, sy, sx):
    H, W = img.shape
    ky = np.fft.fftfreq(H)[:, None]
    kx = np.fft.fftfreq(W)[None, :]
    return np.fft.ifft2(np.fft.fft2(img) * np.exp(-2j * np.pi * (ky * sy + kx * sx)))


# ---------------------------------------------------------------------------
# Self-test (synthetic, sandbox-safe)
# ---------------------------------------------------------------------------
def selftest():
    rng = np.random.default_rng(0)
    print("[A] shift estimator vs known sub-pixel shifts:")
    base = (rng.standard_normal((128, 128)) + 1j * rng.standard_normal((128, 128)))
    base = np.fft.ifft2(np.fft.fft2(base) * _lowpass(128, 0.25))   # correlated speckle
    ok_all = True
    for (sy, sx) in [(2.0, -3.0), (0.4, 0.7), (-1.3, 2.6)]:
        shifted = fourier_shift(base, sy, sx)
        ry, rx = subpixel_shift(base, shifted)
        err = max(abs(ry - sy), abs(rx - sx))
        ok = err < 0.15
        ok_all &= ok
        print(f"   true ({sy:+.1f},{sx:+.1f})  est ({ry:+.2f},{rx:+.2f})  err {err:.2f}px  -> {'PASS' if ok else 'FAIL'}")

    print("\n[B] sub-aperture decomposition sanity:")
    slc = np.fft.ifft2(np.fft.fft2(base) * _lowpass(128, 0.35))
    looks, cents = decompose_subapertures(slc, n_sub=7, overlap=0.5, axis=1)
    mono = np.all(np.diff(cents) > 0)
    energy_ratio = np.sum(np.abs(looks)**2) / (np.abs(slc)**2).sum()
    print(f"   produced {len(looks)} looks; Doppler centroids monotonic: {mono}")
    print(f"   centroids (rel. samples): {np.round(cents,1).tolist()}")

    print("\n[C] multichromatic (MCA) range+Doppler decomposition:")
    mca, mca_cents = multichromatic_subapertures(slc, n_chirp=3, n_sub=7,
                                                 overlap_chirp=0.5, overlap_dop=0.8)
    shape_ok = mca.shape[:2] == (3, 7)
    # each chirp sub-band should still yield monotonic Doppler centroids and finite energy
    energy_ok = np.isfinite(np.abs(mca)**2).all() and (np.abs(mca)**2).sum() > 0
    mca_ok = shape_ok and energy_ok and np.all(np.diff(mca_cents) > 0)
    print(f"   MCA looks shape {mca.shape} (n_chirp,n_sub,H,W); shape_ok={shape_ok}, "
          f"energy_ok={energy_ok}  -> {'PASS' if mca_ok else 'FAIL'}")

    print("\n" + "="*56)
    print("FRONT-END SELF-TEST:", "PASS" if (ok_all and mono and mca_ok) else "FAIL")
    print("="*56)


def _lowpass(N, frac):
    f = np.fft.fftfreq(N)
    m = (np.abs(f)[:, None] < frac) & (np.abs(f)[None, :] < frac)
    return m.astype(float)


# ---------------------------------------------------------------------------
# Real-data path (his Mac: needs sarpy + the SICD)
# ---------------------------------------------------------------------------
def run_on_sicd(path, crop=1024, n_sub=7):
    from sarpy.io.complex.converter import open_complex
    reader = open_complex(path)
    R, C = reader.data_size
    r0, c0 = R // 2 - crop // 2, C // 2 - crop // 2
    print(f"Loading {crop}x{crop} crop from scene centre ({R}x{C}) ...")
    slc = reader[r0:r0 + crop, c0:c0 + crop]
    looks, cents = decompose_subapertures(slc, n_sub=n_sub, overlap=0.5, axis=1)
    shifts = estimate_micromotion(looks)
    print(f"  {n_sub} sub-apertures formed; azimuth shifts across looks (px):")
    print("   ", np.round(shifts[:, 1], 3).tolist())
    _plot_real(slc, looks, cents, shifts, os.path.basename(path))


def _plot_real(slc, looks, cents, shifts, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    az_spec = np.abs(np.fft.fftshift(np.fft.fft(slc, axis=1), axes=1)).mean(0)
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    ax[0, 0].plot(az_spec); ax[0, 0].set_title("Azimuth (Doppler) spectrum"); ax[0, 0].set_xlabel("sample")
    def show(a, im, t):
        m = np.abs(im); v = np.log1p(m); lo, hi = np.percentile(v, [5, 99])
        a.imshow(np.clip((v - lo) / (hi - lo + 1e-9), 0, 1), cmap="gray"); a.set_title(t); a.axis("off")
    show(ax[0, 1], looks[0], "Sub-aperture 1 (low Doppler)")
    show(ax[1, 0], looks[-1], "Sub-aperture N (high Doppler)")
    ax[1, 1].plot(cents, shifts[:, 1], "o-")
    ax[1, 1].set_title("Azimuth shift across looks (micro-motion signal)")
    ax[1, 1].set_xlabel("Doppler centroid"); ax[1, 1].set_ylabel("shift (px)")
    os.makedirs("runs", exist_ok=True)
    out = f"runs/subaperture_{name}.png"
    fig.tight_layout(); fig.savefig(out, dpi=120); print(f"  figure -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sicd", help="path to a SICD .nitf to process")
    ap.add_argument("--crop", type=int, default=1024)
    ap.add_argument("--n-sub", type=int, default=7)
    args = ap.parse_args()
    if args.sicd:
        run_on_sicd(args.sicd, crop=args.crop, n_sub=args.n_sub)
    else:
        selftest()
