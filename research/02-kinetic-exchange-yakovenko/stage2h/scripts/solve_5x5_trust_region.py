"""Trust-region residual minimization for the fixed-price 5x5 private problem.

This tests whether the apparent branch failure near matching multiplier .60
comes from the local Newton method rather than private-equilibrium
nonexistence. It does NOT certify globally optimal Nash: it uses the existing
fast continuous candidate oracle until a globally checked re-evaluation.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for item in (ROOT/"scripts", BASE/"stage2g"/"src", BASE/"stage2g"/"scripts",
             BASE/"stage2e"/"src", BASE/"stage2c"/"src"):
    sys.path.insert(0,str(item))
from solve_private_5x5 import root_at_match, complete_operator
from private_nash_bellman import fixture_3x3, solve_private, endogenous_operator
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import ContinuousModel
from molico_grid import Calibration


def run(folder=ROOT/"results", max_nfev=140):
    folder=Path(folder)
    folder.mkdir(exist_ok=True, parents=True)
    start=time.monotonic()
    small,f_small=fixture_3x3()
    base=solve_private(small,f_small,2.5,np.array(WARM_RELATIVE_VALUE),
                       nq=17,nx=15,maxfev=200)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n)
    assert np.isclose(model.k[12],1.5) and np.isclose(model.m[12],1.)
    f[12]=1.
    interpolator=RegularGridInterpolator((small.kg,small.mg),
              base["value"].reshape(3,3),bounds_error=True)
    warm=interpolator(np.column_stack((model.k,model.m)))
    z=warm[1:]-warm[0]
    path=[]
    for lm in [0.,.05,.15,.30,.55]:
        znext,diag=root_at_match(model,f,2.5,z,lm,nq=9,nx=7,maxfev=500)
        path.append(diag)
        if diag["relative_residual"]>1e-7:
            print("SEED_NOT_CONVERGED",json.dumps(diag),flush=True)
            break
        z=znext
    if path[-1]["match"]<.55:
        report=dict(status="SEED_NOT_CONVERGED",path=path,
                    high_accuracy_Bellman_certified=False,stationary_GE=False)
        (folder/"5x5_trust_region.json").write_text(json.dumps(report,indent=2)+"\n")
        return report

    evaluations=0
    best=(float("inf"),z.copy())
    def residual(zz):
        nonlocal evaluations,best
        v=np.r_[0.,zz]
        values=complete_operator(v,model,f,2.5,1.,nq=9,nx=7)
        rr=values[1:]-values[0]-zz
        val=float(np.max(np.abs(rr)))
        evaluations+=1
        if val<best[0]:best=(val,zz.copy())
        if evaluations%100==0: print("TRUST_EVAL",evaluations,val,"best",best[0],flush=True)
        return rr
    first=float(np.max(np.abs(residual(z))))
    ans=least_squares(residual,z,method="trf",jac="2-point",
         x_scale="jac",diff_step=5e-6,
         ftol=1e-11,xtol=1e-11,gtol=1e-11,
         max_nfev=max_nfev,verbose=1)
    candidates=[(float(np.max(np.abs(residual(ans.x)))),ans.x),
                (best[0],best[1])]
    candidates.sort(key=lambda x:x[0])
    coarse_res,chosen=candidates[0]
    coarse_candidate=bool(coarse_res<1e-7)
    fine={}
    if coarse_candidate:
        relative=np.r_[0.,chosen]
        t=endogenous_operator(relative,f,2.5,model,nq=17,nx=15)[0]
        level=t[0]/(1-model.p.beta)
        val=relative+level
        t2,y,d,kkt=endogenous_operator(val,f,2.5,model,nq=23,nx=19)
        full=float(np.max(np.abs(t2-val)))
        fine=dict(full_bellman_sup=full,local_Nash_KKT_max=kkt,
                  positive_contracts=int(np.count_nonzero(y)))
        np.savez(folder/"5x5_trust_candidate.npz",V=val,y=y,d=d,f=f)
    report=dict(status=("COARSE_CANDIDATE" if coarse_candidate else
                           "TRUST_REGION_STILL_NO_ROOT"),
          first_relative_sup=first,best_relative_sup=coarse_res,
          least_squares_status=int(ans.status),least_squares_message=str(ans.message),
          least_squares_cost=float(ans.cost),objective_evaluations=evaluations,
          seed_path=path,full_reoptimization=fine,wall_seconds=time.monotonic()-start,
          Nash_global_optimality_verified=False,
          private_5x5_root_certified=False,stationary_GE=False)
    (folder/"5x5_trust_region.json").write_text(json.dumps(report,indent=2)+"\n")
    print("TRUST_FINAL",json.dumps(report),flush=True)
    return report


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--max-nfev",type=int,default=140)
    args=parser.parse_args()
    run(max_nfev=args.max_nfev)
