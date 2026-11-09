#!/usr/bin/env python3
"""
Tool check (10 Nov 2026): does the adjacent-look tracker recover a TRUE rigid shift, per look count?

The repo's planted controls shift a 64-px look patch with a Fourier (circular) shift. A circular shift is a pure
linear phase in every FFT bin, so whitened phase correlation recovers it exactly whatever the look bandwidth.
A real displacement is not circular: content moves across the patch edge. This script applies the same shift
both ways to the pipeline's own looks (decompose_subapertures_w, overlap 0.8, Hann) and reports what the
pipeline's estimators return.

  python3 src/check_tracker_bias.py                 # synthetic speckle
  python3 src/check_tracker_bias.py --sicd X.nitf   # centre crop of a real scene
"""
import argparse, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sensitivity_sweep import decompose_subapertures_w, fourier_shift_p, ESTIMATORS

COUNTS = [11, 16, 21, 32, 48, 64, 96, 128]
SHIFTS = [0.0, 0.25, 0.5, 1.0, 2.0]


def run(slc, label, patch=64, overlap=0.8):
    N = slc.shape[0]
    out = dict(label=label, overlap=overlap, patch=patch, rows=[])
    for n in COUNTS:
        looks, _ = decompose_subapertures_w(slc, n_sub=n, overlap=overlap, axis=1, window="hann")
        k = n // 2                                            # one mid-aperture adjacent pair
        A, B = looks[k - 1], looks[k]
        for d in SHIFTS:
            Bn = fourier_shift_p(B, 0.0, d)                   # shift the whole crop: non-circular at patch level
            rec = dict(n_sub=n, true_shift=d)
            for est in ("phasecorr", "ncc"):
                circ, real = [], []
                for r in range(patch, N - patch, patch):      # skip the crop border (wrap-around of the big shift)
                    for c in range(patch, N - patch, patch):
                        a = np.abs(A[r:r + patch, c:c + patch])
                        real.append(ESTIMATORS[est](a, np.abs(Bn[r:r + patch, c:c + patch]), np.float64)[1])
                        bc = fourier_shift_p(B[r:r + patch, c:c + patch], 0.0, d)   # the repo's plant
                        circ.append(ESTIMATORS[est](a, np.abs(bc), np.float64)[1])
                rec[est] = dict(real_median=float(np.median(real)), real_iqr=float(np.subtract(*np.percentile(real, [75, 25]))),
                                circular_median=float(np.median(circ)))
            out["rows"].append(rec)
            if d in (0.0, 0.5, 2.0):
                print(f"  n_sub={n:3d} true={d:4.2f}px | phasecorr real {rec['phasecorr']['real_median']:6.3f} (IQR {rec['phasecorr']['real_iqr']:.2f}) "
                      f"circular-plant {rec['phasecorr']['circular_median']:6.3f} | ncc real {rec['ncc']['real_median']:6.3f} circular-plant {rec['ncc']['circular_median']:6.3f}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sicd"); ap.add_argument("--crop", type=int, default=512)
    ap.add_argument("--out"); a = ap.parse_args()
    if a.sicd:
        from sarpy.io.complex.converter import open_complex
        rd = open_complex(a.sicd); R, C = rd.data_size; c = a.crop
        slc = np.asarray(rd[R // 2 - c // 2:R // 2 + c // 2, C // 2 - c // 2:C // 2 + c // 2])
        label = os.path.basename(a.sicd)
    else:
        rng = np.random.default_rng(0); c = a.crop
        s = (rng.standard_normal((c, c)) + 1j * rng.standard_normal((c, c))) / np.sqrt(2)
        f = np.fft.fftfreq(c)
        slc = np.fft.ifft(np.fft.fft(s, axis=1) * (np.abs(f) <= 0.4)[None, :], axis=1)   # 0.8 processed band
        label = "synthetic_speckle"
    print(label)
    res = run(slc, label)
    out = a.out or f"runs/tracker_bias_{os.path.splitext(label)[0]}.json"
    os.makedirs("runs", exist_ok=True); json.dump(res, open(out, "w"), indent=1); print("->", out)
