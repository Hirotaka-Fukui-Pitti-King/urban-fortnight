"""Stage 2-H: controlled 5x5 continuation and joint endogenous Nash–Bellman root.

This is a *numerical experiment*: Stage 2-G optimized continuous contracts are
used inside every operator evaluation; no global certificate is inferred from
a local root. No GE or stationary-distribution claims are made.

The transition in matching weight changes the *private* problem. At rate 0,
the buyer/seller meeting contributions vanish but the CM is unchanged.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import root

HERE=Path(__file__).resolve().parents[1]
RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/"stage2g"/"src"))
sys.path.insert(0,str(RESEARCH/"stage2c"/"src"))
sys.path.insert(0,str(RESEARCH/"stage2e"/"src"))

from private_nash_bellman import fixture_3x3, solve_private, endogenous_operator
from continuous_core import ContinuousModel, cm_opt
from molico_grid import Calibration


def cm_outside(model, values, price):
    p=model.p
    return np.array([cm_opt((1-p.delta)*k+m/price,
                   price,model.k,model.m,values,model.edges,p.beta,
                   p.b,p.eta)[0] for k,m in zip(model.k,model.m)])


def complete_operator(v, model, f, price, match, nq, nx):
    if match==0:
        return cm_outside(model,v,price)
    if match==1:
        return endogenous_operator(v,f,price,model,nq,nx)[0]
    # 'match' is relative to the model's source opportunity probability 1/Ntypes.
    w0=cm_outside(model,v,price)
    full=endogenous_operator(v,f,price,model,nq,nx)[0]
    return w0+match*(full-w0)


def root_at_match(model,f,price,z0,match,nq=9,nx=7,maxfev=500):
    calls=0
    best=float("inf")
    best_z=z0.copy()
    def R(z):
        nonlocal calls,best,best_z
        v=np.r_[0.,z]
        t=complete_operator(v,model,f,price,match,nq,nx)
        res=t[1:]-t[0]-z
        error=float(np.max(np.abs(res)))
        calls+=1
        if error<best:
            best=error
            best_z=z.copy()
        return res
    result=root(R,z0,method="hybr",
                options={"xtol":1e-10,"eps":1e-7,"maxfev":maxfev})
    errors=[(float(np.max(np.abs(R(z)))),z.copy())
            for z in (result.x,best_z)]
    errors.sort(key=lambda a:a[0])
    return errors[0][1],dict(match=float(match),root_success=bool(result.success),
                message=str(result.message),calls=int(calls),
                relative_residual=errors[0][0],
                highest_previous_residual=float(best),
                method="hybr")


def run(out=HERE/"results", nq=9,nx=7,maxfev=500):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    tic=time.monotonic()
    small,fs=fixture_3x3()
    sys.path.insert(0,str(RESEARCH/"stage2g"/"scripts"))
    from solve_private import WARM_RELATIVE_VALUE
    baseline=solve_private(small,fs,2.5,np.asarray(WARM_RELATIVE_VALUE),
                           nq=17,nx=15,maxfev=200)
    print("3x3 baseline:",baseline["bellman_sup"],flush=True)
    big=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(big.n)
    assert big.k[12]==1.5 and big.m[12]==1.
    f[12]=1.
    rgi=RegularGridInterpolator((small.kg,small.mg),
                       baseline["value"].reshape(3,3),bounds_error=True)
    z0=rgi(np.column_stack((big.k,big.m)))
    z0=z0-z0[0]
    z0=z0[1:]  # relative-value root has n-1 independent coordinates
    stages=[]
    # Smooth matching-rate continuation. Never use a failed point to seed the
    # next target; halve the step on poor progress, then retry the last
    # certified private root. This is *not* monetary GE continuation.
    z=z0.copy()
    last_lambda=0.
    z,diag=root_at_match(big,f,2.5,z,0.,nq,nx,maxfev)
    stages.append(dict(diag,label="adaptive",accepted=diag["relative_residual"]<1e-7))
    if diag["relative_residual"]>=1e-7:
        raise RuntimeError("no-matching private baseline failed")
    # First reproduce the already observed successful coarse continuation
    # branch: 0, .05, .15, .30, .55. Starting with tiny steps from zero
    # instead selected a different branch and stalled near 0.1756.
    seed_path=[.05,.15,.30,.55]
    for target in seed_path:
        candidate,diag=root_at_match(big,f,2.5,z,target,nq,nx,maxfev)
        accepted=diag["relative_residual"]<1e-7
        stages.append(dict(diag,label="branch_seed",accepted=bool(accepted)))
        print("SEED_BRANCH",json.dumps(stages[-1]),flush=True)
        if not accepted:
            break
        last_lambda=target
        z=candidate
        np.savez(out/"private_5x5_last_accepted.npz",
                 relative_value=z,matching_multiplier=last_lambda)
    step=.05
    attempts=0
    if last_lambda>=.55-1e-10:
        while last_lambda < 1.-1e-12 and attempts<35:
            attempts+=1
            target=round(min(1.,last_lambda+step),12)
            candidate,diag=root_at_match(big,f,2.5,z,target,nq,nx,maxfev)
            accepted=diag["relative_residual"]<1e-7
            stages.append(dict(diag,label="branch_follow",accepted=bool(accepted)))
            print("BRANCH_FOLLOW",json.dumps(stages[-1]),flush=True)
            if accepted:
                last_lambda=target
                z=candidate
                np.savez(out/"private_5x5_last_accepted.npz",
                         relative_value=z,matching_multiplier=last_lambda)
                step=min(.08,step*1.25)
            else:
                step*=.5
                if step<.0005:
                    print("BRANCH_STOP_MINIMUM_STEP",step,flush=True)
                    break
    success=last_lambda>=1.-1e-12
    final_diagnostics={}
    if success:
        relative=np.r_[0.,z]
        raw=endogenous_operator(relative,f,2.5,big,nq=max(17,nq),nx=max(15,nx))[0]
        level=raw[0]/(1-big.p.beta)
        values=relative+level
        tfine,yy,dd,kkt=endogenous_operator(values,f,2.5,big,nq=max(23,nq),
                                             nx=max(19,nx))
        final_diagnostics=dict(independent_full_Bellman_sup=float(
                       np.max(np.abs(tfine-values))),
                       independent_Nash_KKT_max=float(kkt),
                       candidate_positive_contracts=int(np.count_nonzero(yy)))
        np.savez(out/"private_5x5_candidate.npz",V=values,y=yy,d=dd,f=f,
                 k=big.k,m=big.m)
    # A strict fixed point must always be independently reevaluated at *finer*
    # Nash precision. A low coarse-search root residual alone is insufficient.
    report=dict(grid=[5,5],price=2.5,partner_state=[1.5,1.],
                stages=stages,stage_2g_3x3_bellman_sup=baseline["bellman_sup"],
                continuation_last_successful_multiplier=float(last_lambda),
                independent_diagnostics=final_diagnostics,
                coarse_5x5_relative_root=bool(success),
                all_pair_Nash_global_certification=False,
                high_accuracy_full_bellman_certification=False,
                stationary_GE=False,wall_seconds=time.monotonic()-tic)
    (out/"private_5x5.json").write_text(json.dumps(report,indent=2)+"\n")
    print("FINAL_SUMMARY",json.dumps({k:v for k,v in report.items() if k!="stages"}),flush=True)
    return report


if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--nq",type=int,default=9)
    a.add_argument("--nx",type=int,default=7)
    a.add_argument("--maxfev",type=int,default=500)
    opt=a.parse_args()
    run(nq=opt.nq,nx=opt.nx,maxfev=opt.maxfev)
