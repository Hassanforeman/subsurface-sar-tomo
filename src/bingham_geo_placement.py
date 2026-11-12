"""Test R, Bingham placement by image matching (R.2 steps 1-3). Amplitude and geometry only.
usage: python _bingham_geo.py PASS_FILE OUT.npz [REF_CHIPS.npz]   (no REF -> this pass is the reference)
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_p_fake_targets as T
from sarpy.io.complex.converter import open_complex
from sarpy.geometry.point_projection import ground_to_image_geo

SCP = (40.5224, -112.1461); SP = 300.0; CH = 256

def m2ll(lat0, lon0, north, east):
    return lat0 + north / 111050.0, lon0 + east / (111320.0 * np.cos(np.deg2rad(lat0)))

def centres():
    return [m2ll(SCP[0], SCP[1], (i - 1.5) * SP, (j - 1.5) * SP) for i in range(4) for j in range(4)]

def chip(rd, s, c):
    R, C = s.ImageData.NumRows, s.ImageData.NumCols
    n = (np.arange(CH) - CH / 2)[:, None] * np.ones((1, CH)); e = np.ones((CH, 1)) * (np.arange(CH) - CH / 2)[None, :]
    lat, lon = m2ll(c[0], c[1], n.ravel(), e.ravel())
    ip = np.asarray(ground_to_image_geo(np.c_[lat, lon, np.full(lat.size, s.GeoData.SCP.LLH.HAE)], s)[0]).reshape(-1, 2)
    r0, r1, c0, c1 = int(ip[:, 0].min()) - 2, int(ip[:, 0].max()) + 3, int(ip[:, 1].min()) - 2, int(ip[:, 1].max()) + 3
    if r0 < 0 or c0 < 0 or r1 > R or c1 > C:
        return None
    a = np.abs(np.asarray(rd[r0:r1, c0:c1]))
    v = a[np.round(ip[:, 0]).astype(int) - r0, np.round(ip[:, 1]).astype(int) - c0].reshape(CH, CH)
    return np.log(v + 1e-3 * np.median(a[a > 0]))

def offset(a, ref):
    from scipy.ndimage import uniform_filter
    a = uniform_filter(a, 7); ref = uniform_filter(ref, 7)      # amendment R-a: 7 m multilook before matching
    A = (a - a.mean()) / a.std(); B = (ref - ref.mean()) / ref.std()
    Cc = np.fft.ifft2(np.fft.fft2(A) * np.conj(np.fft.fft2(B))).real / A.size
    i, j = np.unravel_index(np.argmax(Cc), Cc.shape)
    dn = i if i < CH / 2 else i - CH; de = j if j < CH / 2 else j - CH
    return float(dn), float(de), float(Cc.max())

path, out = sys.argv[1], sys.argv[2]
ref = np.load(sys.argv[3]) if len(sys.argv) > 3 else None
rd = open_complex(path); s = rd.sicd_meta
R, C = s.ImageData.NumRows, s.ImageData.NumCols
hae = s.GeoData.SCP.LLH.HAE
NL = 16
chips = np.zeros((NL, CH, CH), np.float32); off = np.zeros((NL, 3), np.float32)
crops = np.zeros((NL, T.CROP, T.CROP), np.complex64); px = np.zeros((NL, T.NPOS, 2), np.float32); ok = np.zeros(NL, bool)
for k, c in enumerate(centres()):
    ch = chip(rd, s, c)
    if ch is None:
        continue
    chips[k] = ch
    dn = de = 0.0; pk = 1.0
    if ref is not None:
        if not ref["ok"][k]:
            continue
        dn, de, pk = offset(ch, ref["chips"][k])
        off[k] = (dn, de, pk)
        if pk < 0.15 or np.hypot(dn, de) > 60:
            continue
    cc = m2ll(c[0], c[1], dn, de)
    lat, lon = T.line_latlon(cc, T.NPOS // 2, 0.0)
    ip = np.asarray(ground_to_image_geo(np.c_[lat, lon, np.full(T.NPOS, hae)], s)[0]).reshape(-1, 2)
    if ip[:, 0].min() < 90 or ip[:, 1].min() < 90 or ip[:, 0].max() > R - 90 or ip[:, 1].max() > C - 90:
        continue
    ctr = ip.mean(axis=0)
    r0 = int(np.clip(round(ctr[0]) - T.CROP // 2, 0, R - T.CROP)); c0 = int(np.clip(round(ctr[1]) - T.CROP // 2, 0, C - T.CROP))
    img = np.asarray(rd[r0:r0 + T.CROP, c0:c0 + T.CROP], dtype=np.complex64)
    p = ip - np.array([r0, c0])
    amp = np.abs(img)
    if np.mean(amp == 0) > 0.01:
        continue
    crops[k], px[k], ok[k] = img, p, True
np.savez(out, crops=crops, px=px, ok=ok, chips=chips, offsets=off, row_ss=float(s.Grid.Row.SS), col_ss=float(s.Grid.Col.SS))
print(os.path.basename(path), "ok:", np.where(ok)[0].tolist())
print("offsets (north m, east m, peak):", np.round(off, 2).tolist())
