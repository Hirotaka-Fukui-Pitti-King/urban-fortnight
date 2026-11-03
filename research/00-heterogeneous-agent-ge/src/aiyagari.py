"""Stationary Aiyagari GE: EGM, Rouwenhorst shocks, and conservative distributions."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
from numba import njit

@dataclass(frozen=True)
class Calibration:
    beta: float = 0.96
    sigma: float = 2.0
    alpha: float = 0.36
    delta: float = 0.08
    productivity: float = 1.0
    rho: float = 0.90
    z_std: float = 0.20
    nz: int = 5
    na: int = 360
    amax: float = 600.0
    amin: float = 0.0
    curvature: float = 3.0
    egm_tol: float = 1e-10
    dist_tol: float = 1e-12
    ge_tol: float = 5e-9
    max_egm: int = 8000
    max_dist: int = 30000

def rouwenhorst(n, rho, unconditional_std):
    if n < 2 or not (0 <= rho < 1):
        raise ValueError("Need n>=2 and 0<=rho<1")
    p = (1+rho)/2
    P = np.array([[p,1-p],[1-p,p]])
    for k in range(3,n+1):
        O = np.zeros((k,k))
        O[:-1,:-1] += p*P
        O[:-1,1:] += (1-p)*P
        O[1:,:-1] += (1-p)*P
        O[1:,1:] += p*P
        O[1:-1,:] /= 2
        P = O
    logz=np.linspace(-unconditional_std*np.sqrt(n-1),unconditional_std*np.sqrt(n-1),n)
    pi=np.ones(n)/n
    for _ in range(20000):
        nxt=pi@P
        if max(abs(nxt-pi))<1e-15:
            pi=nxt
            break
        pi=nxt
    z=np.exp(logz)
    z/=np.dot(pi,z)
    return z,P,pi

def grid(cal):
    return cal.amin+(cal.amax-cal.amin)*np.linspace(0,1,cal.na)**cal.curvature

@njit(cache=True)
def egm_loop(a,z,P,beta,sigma,r,wage,tol,maxit):
    na=len(a);nz=len(z)
    cash=(1+r)*a[None,:]+wage*z[:,None]
    c=np.empty((nz,na))
    for k in range(nz):
        for j in range(na):
            c[k,j]=max(1e-12,cash[k,j]-a[0])
    g=np.empty_like(c)
    for iteration in range(maxit):
        Emu=P@(c**(-sigma))
        cend=(beta*(1+r)*Emu)**(-1/sigma)
        endog=(cend+a[None,:]-wage*z[:,None])/(1+r)
        for k in range(nz):
            for j in range(1,na):
                if endog[k,j]<=endog[k,j-1]:
                    return c,g,iteration,1
            if endog[k,-1]<a[-1]:
                return c,g,iteration,2
            for j in range(na):
                if a[j]<=endog[k,0]:
                    ap=a[0]
                else:
                    idx=np.searchsorted(endog[k],a[j])
                    if idx==0: idx=1
                    if idx>=na: idx=na-1
                    wt=(a[j]-endog[k,idx-1])/(endog[k,idx]-endog[k,idx-1])
                    ap=a[idx-1]+wt*(a[idx]-a[idx-1])
                g[k,j]=ap
        newc=cash-g
        if np.min(newc)<=0:
            return c,g,iteration,3
        err=np.max(np.abs(newc-c)/(1+np.abs(c)))
        c=newc
        if err<tol:
            return c,g,iteration+1,0
    return c,g,maxit,4

@njit(cache=True)
def histogram_step(mu,a,g,P):
    nz,na=mu.shape
    newmu=np.zeros_like(mu)
    for iz in range(nz):
        for ia in range(na):
            s=g[iz,ia]
            if s<a[0]-1e-11 or s>a[-1]+1e-11:
                return newmu,1
            hi=np.searchsorted(a,s)
            if hi==0: hi=1
            if hi>=na: hi=na-1
            w=min(1.,max(0.,(s-a[hi-1])/(a[hi]-a[hi-1])))
            mass=mu[iz,ia]
            for jz in range(nz):
                newmu[jz,hi-1]+=mass*P[iz,jz]*(1-w)
                newmu[jz,hi]+=mass*P[iz,jz]*w
    return newmu,0

def household(a,z,P,cal,r,w):
    c,g,it,status=egm_loop(a,z,P,cal.beta,cal.sigma,r,w,cal.egm_tol,cal.max_egm)
    if status:
        raise RuntimeError(f"EGM invalid: code={status}, iterations={it}; grid bound={a[-1]}, r={r}")
    return c,g,int(it)

def distribution(a,g,P,pi,cal):
    mu=np.zeros_like(g)
    mu[:,0]=pi
    for it in range(cal.max_dist):
        nxt,status=histogram_step(mu,a,g,P)
        if status: raise RuntimeError("Asset policy outside grid")
        err=np.max(np.abs(nxt-mu))
        mu=nxt
        if err<cal.dist_tol:
            break
    else:
        raise RuntimeError("Invariant distribution failed to converge")
    final,status=histogram_step(mu,a,g,P)
    return mu,int(it+1),float(np.max(np.abs(final-mu)))

def firm_from_r(r,cal,L):
    K=L*(cal.alpha*cal.productivity/(r+cal.delta))**(1/(1-cal.alpha))
    w=(1-cal.alpha)*cal.productivity*(K/L)**cal.alpha
    return K,w

def gini(x,weights):
    x=np.asarray(x);weights=np.asarray(weights)
    p=np.argsort(x);x=x[p];weights=weights[p]
    cw=np.cumsum(weights);wx=np.cumsum(weights*x)
    if wx[-1]<=0: return 0.
    area=np.trapezoid(np.r_[0.,wx/wx[-1]],np.r_[0.,cw/cw[-1]])
    return float(1-2*area)

def weighted_quantile(x,weights,qs):
    k=np.argsort(x)
    x=np.asarray(x)[k];w=np.asarray(weights)[k]
    return np.interp(qs,(np.cumsum(w)-w/2)/np.sum(w),x).tolist()

def euler_diagnostics(a,z,P,cal,c,g,r,mu):
    expected=np.zeros_like(c)
    for iz in range(len(z)):
        for jz in range(len(z)):
            expected[iz]+=P[iz,jz]*np.interp(g[iz],a,c[jz])**(-cal.sigma)
    lhs=c**(-cal.sigma);rhs=cal.beta*(1+r)*expected
    binding=(g<=a[0]+1e-10)
    violations=np.where(binding,np.maximum(rhs/lhs-1,0),np.abs(np.log(lhs/rhs)))
    mass=mu.ravel(); errors=violations.ravel()
    return {"weighted_mean_kkt_or_log_euler":float(np.dot(mass,errors)),
            "weighted_p99_kkt_or_log_euler":float(weighted_quantile(errors,mass,[.99])[0]),
            "max_grid_kkt_or_log_euler":float(errors.max()),
            "binding_mass":float(mu[binding].sum())}

def equilibrium(cal:Calibration,verbose=False):
    a=grid(cal);z,P,pi=rouwenhorst(cal.nz,cal.rho,cal.z_std)
    L=float(pi@z)
    cache={}
    def evaluate(r):
        key=round(float(r),13)
        if key not in cache:
            Kd,w=firm_from_r(r,cal,L)
            c,g,nit=household(a,z,P,cal,r,w)
            mu,mit,derr=distribution(a,g,P,pi,cal)
            Ks=float(np.sum(mu*a[None,:]))
            cache[key]=(Ks-Kd,(Kd,w,c,g,mu,nit,mit,derr,Ks))
            if verbose:
                print(f"r={r:.9f}, K_supply={Ks:.9f}, K_demand={Kd:.9f}, excess={Ks-Kd:.8f}",flush=True)
        return cache[key]
    # Test actual excess capital supply for a sign change, never invent a bracket.
    rates=np.r_[np.linspace(.005,.035,7),np.linspace(.036,min(.0395,1/cal.beta-1-.0008),8)]
    tested=[]
    for r in rates:
        try: tested.append((float(r),evaluate(float(r))[0]))
        except RuntimeError as exc:
            if verbose: print("candidate rejected",float(r),str(exc),flush=True)
    brackets=[(x[0],y[0]) for x,y in zip(tested,tested[1:]) if x[1]*y[1]<0]
    if not brackets:
        raise RuntimeError("No equilibrium bracket. Excess supply schedule: "+str(tested))
    root=brentq(lambda r:evaluate(float(r))[0],*brackets[0],xtol=cal.ge_tol,rtol=1e-12)
    excess,dat=evaluate(root)
    K,w,c,g,mu,nit,mit,derr,Ks=dat
    r=float(root)
    Y=cal.productivity*K**cal.alpha*L**(1-cal.alpha)
    C=float(np.sum(mu*c));Kg=float(np.sum(mu*g))
    eul=euler_diagnostics(a,z,P,cal,c,g,r,mu)
    summary={**asdict(cal),"K_demand":K,"K_supply":Ks,"r":r,"w":w,"L":L,"Y":Y,"C":C,
             "ge_excess_K":excess,"ge_relative_capital_error":abs(excess)/K,
             "goods_resource_error":Y-C-cal.delta*K,
             "labor_market_error":L-float(pi@z),
             "next_assets_stationarity_error":Kg-Ks,
             "distribution_mass_error":float(abs(mu.sum()-1)),
             "distribution_invariance_max_error":derr,
             "income_state_max_error":float(np.max(abs(mu.sum(axis=1)-pi))),
             "asset_top_mass":float(mu[:,-1].sum()),
             "asset_policy_top_gap":float(np.min(a[-1]-g[:,-1])),
             "gini_assets":gini(np.tile(a,len(z)),mu.ravel()),
             "wealth_quantiles":weighted_quantile(np.tile(a,len(z)),mu.ravel(),[.1,.5,.9,.99]),
             "egm_iterations":nit,"distribution_iterations":mit,**eul}
    if abs(excess)/K>1e-6 or abs(summary["goods_resource_error"])/Y>1e-6:
        raise RuntimeError("Market clearing failed: "+str(summary))
    return dict(summary=summary,a=a,z=z,P=P,pi=pi,c=c,g=g,mu=mu)

def save_equilibrium(res,folder):
    import pandas as pd
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/"equilibrium_summary.json").write_text(json.dumps(res["summary"],indent=2)+"\n")
    pd.DataFrame({"a":np.tile(res["a"],len(res["z"])),"z":np.repeat(res["z"],len(res["a"])),
                  "probability":res["mu"].ravel()}).to_csv(folder/"stationary_distribution.csv",index=False)
    pd.DataFrame({"a":np.tile(res["a"],len(res["z"])),"z":np.repeat(res["z"],len(res["a"])),
                  "savings":res["g"].ravel(),"consumption":res["c"].ravel()}).to_csv(folder/"policy_functions.csv",index=False)
    return res["summary"]
