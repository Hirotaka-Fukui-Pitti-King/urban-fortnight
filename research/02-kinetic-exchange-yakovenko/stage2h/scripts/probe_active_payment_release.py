"""Reproduce the lambda=.55 false private root; test Nash payment-bound release.

Numerical candidate only; the convex decomposition provides an independent
improving feasible contract, not a 5x5 general-equilibrium certification.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for path in (ROOT/"src",ROOT/"scripts",BASE/"stage2g"/"src",
             BASE/"stage2g"/"scripts",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(path))
from solve_private_5x5 import root_at_match,complete_operator,cm_outside
from private_nash_bellman import (fixture_3x3,solve_private,endogenous_operator,
                                  nash_grad,nash_score)
from active_nash import active_polish,active_operator
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import ContinuousModel
from molico_grid import Calibration
from convex_nash import solve_pair


def run(folder=ROOT/"results",maxfev=500):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    small,fsmall=fixture_3x3()
    solved=solve_private(small,fsmall,2.5,np.asarray(WARM_RELATIVE_VALUE),
                         nq=17,nx=15,maxfev=200)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n); f[12]=1.
    interp=RegularGridInterpolator((small.kg,small.mg),
                                   solved["value"].reshape(3,3),
                                   bounds_error=True)
    guess=interp(np.column_stack((model.k,model.m)))
    z=guess[1:]-guess[0]
    seeds=[]
    for lm in [0.,.05,.15,.30,.55]:
        znext,diag=root_at_match(model,f,2.5,z,lm,9,7,maxfev)
        seeds.append(diag)
        if diag["relative_residual"] >= 1e-7:
            report=dict(status="SEED_FAILED",stage=lm,seeds=seeds,
                        stationary_GE=False)
            (folder/"payment_active_release.json").write_text(
                json.dumps(report,indent=2)+"\n")
            print("RELEASE_SUMMARY",json.dumps(report),flush=True)
            return report
        z=znext
    rel=np.r_[0.,z]
    raw=complete_operator(rel,model,f,2.5,.55,9,7)
    V=rel+raw[0]/(1-model.p.beta)
    Tlegacy,oldy,oldd,legacykkt=endogenous_operator(V,f,2.5,model,9,7)
    i,j=13,12
    v=V-max(V)
    q,pay=float(oldy[i,j]),float(oldd[i,j])
    p=model.p
    grad=nash_grad(q,pay,i,j,2.5,model.k,model.m,v,model.edges,
                   p.beta,p.b,p.eta,p.alpha,p.A,p.theta,p.delta)
    nq,nd,kkt,released=active_polish(i,j,q,pay,model,v,2.5)
    convex=solve_pair(model,V,2.5,i,j)
    Told=cm_outside(model,V,2.5)+.55*(Tlegacy-cm_outside(model,V,2.5))
    Tnew,yy,dd,newKKT,release_list=active_operator(V,f,2.5,model,9,7)
    Tnew=cm_outside(model,V,2.5)+.55*(Tnew-cm_outside(model,V,2.5))
    score_old=nash_score(q,pay,i,j,model,v,2.5)
    score_repaired=nash_score(nq,nd,i,j,model,v,2.5)
    report=dict(status="ACTIVE_SET_DIAGNOSIS_EXECUTED",
                price=2.5,grid=[5,5],lambda_multiplier=.55,
                buyer=i,seller=j,
                old_quantity=q,old_payment=pay,
                old_quantity_gradient=float(grad[0]),
                old_real_payment_gradient=float(grad[1]),
                old_log_nash=float(score_old),
                repaired_quantity=float(nq),repaired_payment=float(nd),
                repaired_log_nash=float(score_repaired),
                repaired_KKT=float(kkt),released_from_upper_bound=bool(released),
                convex_quantity=convex.y,convex_payment=convex.d,
                convex_log_nash=convex.log_nash,
                convex_reported_branch_errors=not convex.dcp_pass,
                legacy_lambda_055_Bellman_sup=float(np.max(abs(Told-V))),
                active_lambda_055_Bellman_sup=float(np.max(abs(Tnew-V))),
                total_active_releases=len(release_list),
                active_release_pairs=release_list,
                max_active_candidate_KKT=float(newKKT),
                source_rate_root=False,global_allpair_Nash_certified=False,
                stationary_GE=False)
    (folder/"payment_active_release.json").write_text(json.dumps(
           report,indent=2)+"\n")
    print("RELEASE_SUMMARY",json.dumps(report),flush=True)
    return report


if __name__=="__main__":
    run()
