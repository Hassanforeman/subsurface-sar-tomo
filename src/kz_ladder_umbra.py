#!/usr/bin/env python3
"""
kz_ladder_umbra.py — Q2 (COMPARISON_EJHONG §6): the paper's steering wavenumbers for OUR sub-aperture
bank on the three Umbra Giza SICDs, from each product's own orbit polynomial. Descriptive geometry only
(no hypothesis, no tuning, no pixels read) — so no pre-registration is needed; stated here for the record.

Paper's steering form (as implemented by ejhong/sar): Kz_i = 4*pi*Bperp_i / (lambda_s * r * sin(theta)),
Bperp_i = platform offset at sub-aperture centre i, projected perpendicular to the line of sight to the SCP.
Our bank: n_sub 11, overlap 0.8 -> sub-aperture width = 1/3 of the processed time, centres uniformly
spaced over the remaining 2/3. (Assumes processed Doppler maps linearly to processed slow time.)

Reports: uniformity of the ladder (CV of dKz) — if ~0, the steering matrix is a DFT to that precision —
and the depth repeat per metre of the free "sound wavelength" lambda_s (repeat = lambda_s*r*sin(theta)/(2*dBperp)).

  python3 src/kz_ladder_umbra.py   -> runs/kz_ladder_umbra.json   (reads only the SICD XML at file end)
"""
import glob, json, os, re
import numpy as np

NSUB, OVERLAP = 11, 0.8


def sicd_xml(path, tail=400000):
    with open(path, "rb") as fh:
        fh.seek(0, 2); n = fh.tell(); fh.seek(max(0, n - tail)); b = fh.read()
    x = b.replace(b"\x00", b"").decode("latin1")
    x = x[x.find("<SICD"): x.find("</SICD>") + 7]
    return re.sub(r"<(/?)\w+:", r"<\1", x)


def num(tag, s):
    m = re.search(rf"<{tag}[^>]*>([^<]*)<", s)
    return float(m.group(1)) if m else None


def block(tag, s):
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", s, re.S)
    return m.group(1) if m else ""


def ladder(path):
    x = sicd_xml(path)
    arp = block("ARPPoly", x)
    P = []
    for ax in ("X", "Y", "Z"):
        cs = re.findall(r'<Coef exponent1="(\d+)"[^>]*>([^<]*)<', block(ax, arp))
        c = np.zeros(max(int(e) for e, _ in cs) + 1)
        for e, v in cs:
            c[int(e)] = float(v)
        P.append(c)
    pos = lambda t: np.array([np.polyval(c[::-1], t) for c in P])
    t0, t1 = num("TStartProc", x), num("TEndProc", x)
    tx = block("TxFrequency", x)
    lam = 299792458.0 / ((num("Min", tx) + num("Max", tx)) / 2)
    ecf = block("ECF", block("SCP", x))
    S = np.array([num("X", ecf), num("Y", ecf), num("Z", ecf)])
    theta = np.radians(90 - num("GrazeAng", x))
    T = t1 - t0
    w = T / (1 + (NSUB - 1) * (1 - OVERLAP))
    cen = t0 + w / 2 + np.arange(NSUB) * (T - w) / (NSUB - 1)
    pc = pos((t0 + t1) / 2)
    r = np.linalg.norm(S - pc); los = (S - pc) / r
    along = pos(t1) - pos(t0)
    B = []
    for t in cen:
        d = pos(t) - pc
        dp = d - (d @ los) * los
        B.append(np.linalg.norm(dp) * np.sign(d @ along))
    B = np.array(B); dB = np.diff(B)
    geom = r * np.sin(theta)
    return dict(t_proc_s=T, subaperture_s=w, centre_spacing_s=float(cen[1] - cen[0]),
                lambda_em_m=lam, slant_range_m=float(r), incidence_deg=float(90 - num("GrazeAng", x)),
                bperp_span_m=float(B.max() - B.min()), dBperp_mean_m=float(dB.mean()),
                dKz_cv=float(dB.std() / dB.mean()),
                repeat_m_per_m_of_lambda_s=float(geom / (2 * dB.mean())),
                unambiguous_m_per_m_of_lambda_s=float(geom / (4 * dB.mean())),
                repeat_m_if_lambda_s_equals_em=float(lam * geom / (2 * dB.mean())))


def main():
    out = {}
    for p in sorted(glob.glob("data/giza_*_SICD.nitf")):
        name = os.path.basename(p).split("_SICD")[0]
        out[name] = ladder(p)
        d = out[name]
        print(f"{name}: T {d['t_proc_s']:.2f}s  Bperp span {d['bperp_span_m']:.0f} m  CV(dKz) {d['dKz_cv']:.1e}  "
              f"repeat {d['repeat_m_per_m_of_lambda_s']:.1f} m per m of lambda_s")
    os.makedirs("runs", exist_ok=True)
    json.dump(dict(script="src/kz_ladder_umbra.py", bank=dict(n_sub=NSUB, overlap=OVERLAP), scenes=out),
              open("runs/kz_ladder_umbra.json", "w"), indent=1)
    print("-> runs/kz_ladder_umbra.json")


if __name__ == "__main__":
    main()
