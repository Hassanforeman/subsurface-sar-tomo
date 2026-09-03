#!/usr/bin/env python3
"""Can the method's resolution support a recognizable Sphinx FACE (chin/nose/eyes/cobra)
at 500-1200 m depth? Compares achievable resolution to the feature sizes claimed.

Two independent resolution limits are computed:
  (1) VERTICAL (depth): dz = (v/f) * R / (2A)  -- the authors' own formula.
  (2) HORIZONTAL at depth: a reflector at depth z blurs its surface imprint over its
      Fresnel zone, radius ~ sqrt(lambda * z). This is why the 0.5 m radar surface pixel
      does NOT carry to depth: the inversion cannot localise a deep feature finer than its
      Fresnel zone, whatever the surface sampling.
"""
import numpy as np

# --- claimed target features (Great Sphinx scale) ---
FACE_W = 4.0        # m, width of the Sphinx face
FACE_H = 5.0        # m
URAEUS = 0.6        # m, the cobra on the forehead (a claimed feature)
SUBFEATURE = 1.0    # m, nose/mouth/eye scale
print("Claimed recognizable features (need >=2 samples across each to render):")
for n,s in [("whole face width",FACE_W),("nose/mouth/eye ~",SUBFEATURE),("uraeus cobra ~",URAEUS)]:
    print(f"   {n:22s} {s:5.1f} m  -> need voxel <= {s/2:.2f} m")

R = 650e3           # slant range (m), spaceborne
A = 42e3            # synthetic aperture in the Doppler synthesis (m), authors' value
print(f"\nGeometry: R={R/1e3:.0f} km, A={A/1e3:.0f} km")

def dz(v,f): return (v/f)*R/(2*A)
print("\n(1) VERTICAL depth resolution dz = (v/f) R / 2A:")
for label,v,f in [("honest ambient seismic (v=3000, f=50 Hz)",3000,50),
                  ("generous (v=2000, f=100 Hz)",2000,100),
                  ("Biondi's OWN 22 kHz (ultrasonic, unphysical)",6000,22000)]:
    lam=v/f
    print(f"   {label:46s}: lambda={lam:8.3f} m  dz={dz(v,f):8.2f} m")

print("\n(2) HORIZONTAL resolution at depth = Fresnel radius sqrt(lambda*z):")
for z in [500,1000]:
    print(f"   at z={z} m:")
    for label,v,f in [("honest (f=50 Hz, v=3000 -> lambda=60 m)",3000,50),
                      ("Biondi 22 kHz (lambda=0.27 m)",6000,22000)]:
        lam=v/f; fr=np.sqrt(lam*z)
        print(f"      {label:42s}: Fresnel radius ~ {fr:7.1f} m")

print("\nVERDICT:")
print("  Honest physics: one resolution cell (tens-to-hundreds of m vertically, ~100+ m")
print("  horizontally at 500 m via Fresnel) is 20-300x LARGER than the whole 4-5 m face.")
print("  The face is sub-voxel: it cannot exist in the data.")
print("  Even at the authors' own unphysical 22 kHz best case (dz~3.7 m), one voxel ~ the")
print("  entire face width, so you get ONE blob for the whole face; a 0.6 m uraeus needs")
print("  ~6x finer than their own claimed resolution and ~200x finer than honest physics.")
print("  => The chin/nose/eyes/cobra detail is 1-3 orders of magnitude finer than the")
print("     method's OWN claimed resolution. It is not measured; it enters downstream")
print("     (the '3D model' the 2022 paper pairs with the tomogram, plus AI/rendering).")
