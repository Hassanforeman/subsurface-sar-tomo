import sys, numpy as np, json
sys.path.insert(0,'src')
import test_j_disclosed_config as t
from sarpy.io.complex.converter import open_complex

scenes={"Butte":"data/2024-03-07-04-48-26_UMBRA-04_SICD.nitf","Giza0207":"data/giza_2023-02-07_UMBRA-05_SICD.nitf","Giza0308":"data/giza_2023-03-08_UMBRA-04_SICD.nitf","Giza0208":"data/giza_2023-02-08_UMBRA-04_SICD.nitf","Capella":"data/CAPELLA_C13_SP_SICD_HH_20241123062737_20241123062813.ntf"}
ovs=[0.5,0.6,0.7,0.8,0.85,0.9,0.93,0.95]
n=11
def crop(path):
    rd=open_complex(path); R,C=rd.data_size; c=512
    return np.asarray(rd[R//2-c//2:R//2+c//2, C//2-c//2:C//2+c//2])
out={}
def sweep(slc):
    row=[]
    for ov in ovs:
        f=1.0/(n-(n-1)*ov)
        r=t.run_config(slc,n,f,'hann','phasecorr',100,2.0)
        row.append((round(r['ratio_align'],2), round(r['peak_cells'],2)))
    return row
for s in range(5):
    rng=np.random.default_rng(100+s); slc=(rng.standard_normal((512,512))+1j*rng.standard_normal((512,512)))/2**.5
    out[f"noise{s}"]=sweep(slc)
for k,p in scenes.items():
    out[k]=sweep(crop(p))
print("overlap     ", ovs)
print("look frac   ", [round(1/(n-(n-1)*o),3) for o in ovs])
for k,v in out.items(): print(f"{k:10s}", [x[0] for x in v], " peaks", sorted(set(x[1] for x in v))[:2], "..", max(x[1] for x in v))
json.dump(dict(n_sub=n, overlaps=ovs, results=out), open('runs/overlap_sweep_posthoc_2026-11-09.json','w'), indent=1)
