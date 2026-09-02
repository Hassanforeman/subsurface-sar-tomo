#!/usr/bin/env python3
"""Does a SUPER-RESOLUTION inverter (Capon/MVDR, MUSIC) also produce the surface-pinned
artifact, or only the plain Bartlett/DFT the paper reproduces?

Biondi's strongest un-preempted rebuttal is "you used a weak inverter; my method uses
super-resolution." The mechanism argument says it can't matter — the random walk enters
BEFORE any inverter. This tests it directly: feed the identical per-patch trajectories
(real Giza, and pure-noise walks) into Bartlett, Capon and MUSIC on the pipeline's own
steering grid, and compare peak depth.

Run from repo root:  python3 src/robustness_inverters.py
"""
import sys, numpy as np
sys.path.insert(0, "src")
from sarpy.io.complex.converter import open_complex
from tomogram import _patch_observations, analytic1d, DZ_TARGET

def steering(n, zgrid):
    Kz = np.arange(n) * 2*np.pi/(n*DZ_TARGET)
    return np.exp(1j*np.outer(Kz, zgrid))            # n x Z, same basis as tomogram.steering

def three_inverters(obs, zgrid, n_src=1):
    Y = np.array([analytic1d(r) for r in obs])       # P x n analytic snapshots
    P, n = Y.shape
    R = (Y.T @ Y.conj()) / P                          # n x n covariance E[y y^H] (standard convention)
    A = steering(n, zgrid)
    bart = np.array([(A[:,i].conj() @ R @ A[:,i]).real for i in range(A.shape[1])])
    Rl = R + 1e-2*(np.trace(R)/n)*np.eye(n)
    Rinv = np.linalg.inv(Rl)
    cap = np.array([1.0/(A[:,i].conj() @ Rinv @ A[:,i]).real for i in range(A.shape[1])])
    w, V = np.linalg.eigh(R)                          # ascending
    En = V[:, :n-n_src]                               # noise subspace
    mus = np.array([1.0/((np.abs(En.conj().T @ A[:,i])**2).sum()+1e-30) for i in range(A.shape[1])])
    pk = lambda s: zgrid[np.argmax(s)]/DZ_TARGET
    con = lambda s: s.max()/np.median(s)
    return {"Bartlett":(pk(bart),con(bart)), "Capon":(pk(cap),con(cap)), "MUSIC":(pk(mus),con(mus))}

def load_real(path, crop=512, n_sub=11):
    reader = open_complex(path); R,C = reader.data_size
    slc = reader[R//2-crop//2:R//2+crop//2, C//2-crop//2:C//2+crop//2]
    cols = np.linspace(0, crop-64, 24).astype(int)
    obs,_ = _patch_observations(slc, cols, crop//2-32, 64, n_sub, 0.8, 1)
    return np.asarray(obs)

def noise_walks(n_sub=11, P=24, seed=0):
    rng = np.random.default_rng(seed); out=[]
    for _ in range(P):
        t = np.cumsum(rng.standard_normal(n_sub))
        x = np.arange(n_sub)
        out.append(t - np.polyval(np.polyfit(x,t,2),x))
    return np.asarray(out)

n_sub=11; zgrid=np.linspace(0, n_sub*DZ_TARGET/2, 300)
print("peak depth in cells (surface-pinned ~1.7); does super-resolution change it?")
print(f"{'input':<22}{'Bartlett':>22}{'Capon':>22}{'MUSIC':>22}")
cases=[("Giza 7Feb (real)", load_real("data/giza_2023-02-07_UMBRA-05_SICD.nitf")),
       ("pure-noise walks", noise_walks())]
for name,obs in cases:
    r=three_inverters(obs, zgrid)
    fmt=lambda t: f"{t[0]:.2f} cells (C={t[1]:.1f})"
    print(f"{name:<22}{fmt(r['Bartlett']):>22}{fmt(r['Capon']):>22}{fmt(r['MUSIC']):>22}")
print("\nIf Capon and MUSIC also pin at ~1.7 cells, the artifact is upstream of the inverter")
print("and 'you used a weak inverter' is refuted: super-resolution sharpens it, not removes it.")
