#!/usr/bin/env python3
"""
inspect_scene.py — open an Umbra/Capella SICD (.nitf) or CPHD (.cphd), print key
parameters, and save a downsampled magnitude quicklook PNG.

Install:  pip install sarpy numpy matplotlib

Examples
--------
python src/inspect_scene.py data/2024-01-12-04-09-18_UMBRA-05_SICD.nitf
python src/inspect_scene.py data/2024-01-12-04-09-18_UMBRA-05_CPHD.cphd
"""
import argparse, os, sys
import numpy as np


def inspect_sicd(path):
    from sarpy.io.complex.converter import open_complex
    reader = open_complex(path)
    sicd = reader.get_sicds_as_tuple()[0]
    rows, cols = reader.data_size
    print(f"SICD: {os.path.basename(path)}")
    print(f"  pixels: {rows} x {cols}")
    try:
        print(f"  center freq (Hz): {sicd.RadarCollection.TxFrequency.Min:.3e} – "
              f"{sicd.RadarCollection.TxFrequency.Max:.3e}")
    except Exception:
        pass
    try:
        print(f"  slant res (az,rg) m: {sicd.Grid.Col.SS:.3f}, {sicd.Grid.Row.SS:.3f}")
    except Exception:
        pass
    try:
        print(f"  collect duration (s): {sicd.Timeline.CollectDuration:.2f}")
        print(f"  scene center LLA: {sicd.GeoData.SCP.LLH.Lat:.5f}, "
              f"{sicd.GeoData.SCP.LLH.Lon:.5f}, {sicd.GeoData.SCP.LLH.HAE:.1f} m")
    except Exception:
        pass

    # decimated magnitude quicklook
    step = max(1, max(rows, cols) // 1500)
    chip = reader[0:rows:step, 0:cols:step]
    mag = np.abs(chip).astype(np.float32)
    _save_png(mag, os.path.splitext(path)[0] + "_quicklook.png")


def inspect_cphd(path):
    from sarpy.io.phase_history.converter import open_phase_history
    reader = open_phase_history(path)
    print(f"CPHD: {os.path.basename(path)}")
    try:
        cphd = reader.cphd_meta
        ch = cphd.Data.Channels[0]
        print(f"  vectors x samples: {ch.NumVectors} x {ch.NumSamples}")
        print(f"  collect: {cphd.Global.Timeline.CollectionStart}")
    except Exception as e:
        print("  (metadata read partial:", e, ")")
    print("  CPHD = phase history; feed to the sub-aperture stage, not imaged directly here.")


def _save_png(mag, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    v = np.log1p(mag)
    lo, hi = np.percentile(v, [5, 99])
    plt.figure(figsize=(8, 8))
    plt.imshow(np.clip((v - lo) / (hi - lo + 1e-9), 0, 1), cmap="gray")
    plt.axis("off"); plt.tight_layout()
    plt.savefig(out, dpi=120, bbox_inches="tight"); plt.close()
    print(f"  quicklook → {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="path to a .nitf (SICD) or .cphd file")
    args = ap.parse_args()
    if not os.path.exists(args.path):
        sys.exit("File not found: " + args.path)
    try:
        if args.path.lower().endswith(".cphd"):
            inspect_cphd(args.path)
        else:
            inspect_sicd(args.path)
    except ImportError:
        sys.exit("Need sarpy:  pip install sarpy numpy matplotlib")

if __name__ == "__main__":
    main()
