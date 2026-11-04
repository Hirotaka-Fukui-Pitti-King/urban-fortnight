"""Correct payment-active Nash policy inside 5x5 private fixed-point roots.

The new private oracle releases improperly binding nominal payment constraints
in addition to the original continuous Nash search. It remains a *candidate*
oracle: any converged full-source-rate root must be independently verified by
the all-49-pair convex global Nash solver before certification.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.optimize import root
from scipy.interpolate import RegularGridInterpolator

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for path in (HERE/"src",HERE/"scripts",BASE/"stage2g"/"src",
             BASE/"stage2g"/"scripts",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(path))
from solve_private_5x5 import root_at_match,complete_operator,cm_outside
from private_nash_bellman import fixture_3x3,solve_private
from active_nash import active_operator
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import ContinuousModel
from molico_grid import Calibration


def active_complete(v, model, partners, price, multiplier, nq=9, nx=7):
    outside=cm_outside(model,v,price)
    if multiplier==0:return outside
    trial=active_operator(v,partners,price,model,nq=nq,nx=nx)[0]
    return outside + multiplier*(trial-outside)


def active_root(model,f,price,initial_z,multiplier,nq=9,nx=7,maxfev=500):
    num=0
    best=(float("inf"),initial_z.copy())
    def residual(z):
        nonlocal num,best
        vv=np.r_[0.,z]
        t=active_complete(vv,model,f,price,multiplier,nq,nx)
        rr=t[1:]-t[0]-z
        val=float(np.max(np.abs(rr)))
        num+=1
        if val<best[0]:
            best=(val,z.copy())
        return rr
    fit=root(residual,initial_z,method="hybr",
             options={"xtol":1e-11,"eps":1e-8,"maxfev":maxfev})
    reevaluated=[(float(np.max(np.abs(residual(z)))),z.copy())
                 for z in (fit.x,best[1])]
    reevaluated.sort(key=lambda a:a[0])
    return reevaluated[0][1],dict(
        multiplier=float(multiplier),
        sup=float(reevaluated[0][0]),root_success=bool(fit.success),
        evaluations=num,message=str(fit.message))


def run(folder=HERE/"results",maxfev=500):
    folder=Path(folder); folder.mkdir(exist_ok=True,parents=True)
    start=time.monotonic()
    small,fs=fixture_3x3()
    baseline=solve_private(small,fs,2.5,np.asarray(WARM_RELATIVE_VALUE),
                           nq=17,nx=15,maxfev=200)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    interp=RegularGridInterpolator((small.kg,small.mg),
          baseline["value"].reshape(3,3),bounds_error=True)
    w=interp(np.column_stack((model.k,model.m)))
    z=w[1:]-w[0]
    original_seed=[]
    for lm in (0.,.05,.15,.30,.55):
        znext,diag=root_at_match(model,f,2.5,z,lm,nq=9,nx=7,maxfev=maxfev)
        original_seed.append(diag)
        if diag["relative_residual"]>=1e-7:
            raise RuntimeError("Inherited 5x5 branch seed failed to reproduce")
        z=znext
    initial_active_res=active_complete(np.r_[0.,z],model,f,2.5,.55)
    initial_active_sup=float(np.max(abs(initial_active_res[1:]-initial_active_res[0]-z)))
    print("ACTIVE_INITIAL_SUP",initial_active_sup,flush=True)
    # Globally corrected Nash breaks the previous spurious private root;
    # solve it again before attempting to continue toward source multiplier 1.
    path=[]
    znext,diag=active_root(model,f,2.5,z,.55,maxfev=maxfev)
    path.append(dict(diag,label="repaired_seed"))
    print("ACTIVE_ROOT",json.dumps(path[-1]),flush=True)
    verified=diag["sup"]<1e-7
    if verified:z=znext
    lam=.55; step=.05
    for num in range(35):
        if not verified or lam>=1.-1e-12 or step<.0005:break
        target=round(min(1.,lam+step),12)
        trial,di=active_root(model,f,2.5,z,target,maxfev=maxfev)
        accept=di["sup"]<1e-7
        path.append(dict(di,label="follow",accepted=bool(accept)))
        print("ACTIVE_FOLLOW",json.dumps(path[-1]),flush=True)
        if accept:
            z=trial;lam=target;step=min(.10,step*1.25)
        else:step*=.5
    at_one=verified and lam>=1.-1e-12
    final={}
    if at_one:
        rel=np.r_[0.,z]
        base=active_complete(rel,model,f,2.5,1.)
        V=rel+base[0]/(1-model.p.beta)
        trial,y,d,maxKKT,releases=active_operator(V,f,2.5,model)
        final=dict(fast_Bellman_sup=float(max(abs(trial-V))),
                   fast_KKT=float(maxKKT),
                   fast_releases=releases,
                   positive_contracts=int(np.count_nonzero(y)))
        np.savez(folder/"private_5x5_active_candidate.npz",V=V,y=y,d=d,f=f,
                 k=model.k,m=model.m)
    report=dict(status=("UNCERTIFIED_SOURCE_ROOT_CANDIDATE" if at_one else
                        "PAYMENT_REPAIR_PRIVATE_ROOT_NOT_REACHED"),
                repaired_seed_initial_sup=initial_active_sup,
                repaired_lambda_055_converged=bool(verified),
                reached_multiplier=float(lam),
                source_rate_candidate=bool(at_one),
                all_pair_global_nash_certified=False,
                independent_full_Bellman_certified=False,
                stationary_GE=False,original_seed=original_seed,path=path,
                fast_candidate_diagnostics=final,
                elapsed_seconds=time.monotonic()-start)
    (folder/"private_5x5_active_root.json").write_text(
         json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("ACTIVE_ROOT_SUMMARY",json.dumps({k:v for k,v in report.items()
                     if k not in ("original_seed","path")}),flush=True)
    return report


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--maxfev",type=int,default=500)
    opts=parser.parse_args()
    run(maxfev=opts.maxfev)
