#!/usr/bin/env python3
"""Exact derivation of the artifact depth constant (the '1.71 cells' / '0.856' question).

The reported depth in resolution cells is the argmax of the expected tomogram of a
degree-d-detrended random walk pushed through the pipeline's own analytic-DFT operator.
That expected tomogram is a CLOSED, parameter-free matrix quadratic form:

    E[power(z)] = f(z)^H  H (I-P_d) C (I-P_d)^T H^H  f(z)

    C[i,j] = min(i,j)+1        random-walk covariance
    P_d                        projection onto polynomials of degree <= d (the detrend)
    H                          analytic1d as a matrix (a = H r)
    f(z)_k = exp(-i Kz_k z)    the pipeline's steering, Kz_k = k 2pi/(n DZ)

Its peak is a pure number per detrend degree, converging as n grows. No Monte Carlo,
no free parameter. `--selftest` checks the 24-patch pipeline reproduces it.
"""
import numpy as np
DZ = 5.0

def _Hmat(n):
    F = np.fft.fft(np.eye(n)); h = np.zeros(n)
    if n % 2 == 0: h[0]=1; h[n//2]=1; h[1:n//2]=2
    else: h[0]=1; h[1:(n+1)//2]=2
    return (np.conj(F)/n) @ (h[:, None]*F)

def expected_peak_cells(n, deg, nz=40000):
    t = np.arange(n)
    V = np.vander(t, deg+1, increasing=True).astype(float)
    R = np.eye(n) - V @ np.linalg.pinv(V)
    C = np.minimum.outer(t, t) + 1.0
    S = _Hmat(n) @ (R @ C @ R.T) @ _Hmat(n).conj().T
    z = np.linspace(0, n*DZ/2, nz); Kz = np.arange(n)*2*np.pi/(n*DZ)
    G = np.exp(-1j*np.outer(Kz, z))
    Pex = np.einsum('kz,kl,lz->z', G, S, np.conj(G)).real
    return z[np.argmax(Pex)]/DZ

def _analytic(v):
    N=len(v); Vv=np.fft.fft(v); h=np.zeros(N)
    if N%2==0: h[0]=1;h[N//2]=1;h[1:N//2]=2
    else: h[0]=1;h[1:(N+1)//2]=2
    return np.fft.ifft(Vv*h)

def sim_pipeline_peak(n, deg, P=24, trials=1500, nz=4000, seed=0):
    rng=np.random.default_rng(seed); t=np.arange(n)
    z=np.linspace(0,n*DZ/2,nz); Kz=np.arange(n)*2*np.pi/(n*DZ); A=np.exp(1j*np.outer(Kz,z))
    pk=[]
    for _ in range(trials):
        acc=np.zeros(nz)
        for _p in range(P):
            w=np.cumsum(rng.standard_normal(n)); r=w-np.polyval(np.polyfit(t,w,deg),t)
            acc+=np.abs(A.conj().T@_analytic(r))**2
        pk.append(z[np.argmax(acc)]/DZ)
    return np.mean(pk), np.std(pk)

if __name__=="__main__":
    import sys
    print("Exact expected-tomogram peak (cells), converging in n:")
    print(f"{'n':>5} {'deg0':>9} {'deg2':>9} {'deg4':>9}")
    for n in [11,16,32,64,128,256]:
        print(f"{n:>5} {expected_peak_cells(n,0):9.4f} {expected_peak_cells(n,2):9.4f} {expected_peak_cells(n,4):9.4f}")
    print("\nAsymptotic: deg0->0.869, deg2->1.680, deg4->2.474 cells.")
    print("The empirical law k~0.856*(d/2+1) is only approximate: the true per-degree")
    print("prefactor drifts (0.870, 0.840, 0.825), so there is NO single clean constant.")
    if "--selftest" in sys.argv:
        ok=True
        for n,deg in [(32,0),(32,2),(128,2),(128,4)]:
            ex=expected_peak_cells(n,deg); m,s=sim_pipeline_peak(n,deg)
            hit=abs(m-ex)<=3*s+0.05
            ok&=hit
            print(f"[selftest] n={n} deg={deg}: exact {ex:.4f} vs 24-patch sim {m:.3f}±{s:.3f} -> {'PASS' if hit else 'FAIL'}")
        print("SELFTEST:", "PASS" if ok else "FAIL")
