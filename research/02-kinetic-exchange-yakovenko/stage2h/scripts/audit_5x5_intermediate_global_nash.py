"""Audit ALL 49 Nash matches at the 5x5 matching=.55 private candidate.

This directly asks whether the previously converged intermediate private root
survives globally optimized continuous Nash contracts on its own 5x5 value
function. It is NOT the source-rate economy and NOT monetary GE.
"""
from __future__ import annotations
import csv
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for folder in (ROOT/"src",ROOT/"scripts",BASE/"stage2g"/"src",
               BASE/"stage2g"/"scripts",BASE/"stage2e"/"src",
               BASE/"stage2c"/"src"):
    sys.path.insert(0,str(folder))
from solve_private_5x5 import root_at_match,complete_operator,cm_outside
from private_nash_bellman import (fixture_3x3,solve_private,
                                  endogenous_operator,_frozen_operator,
                                  nash_score)
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import ContinuousModel
from molico_grid import Calibration
from convex_nash import solve_pair


def run(output=ROOT/"results", maxfev=500, nq=9, nx=7):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    small,fs=fixture_3x3()
    base=solve_private(small,fs,2.5,np.asarray(WARM_RELATIVE_VALUE),
                       nq=17,nx=15,maxfev=200)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(model.n);f[12]=1.
    interp=RegularGridInterpolator((small.kg,small.mg),
          base["value"].reshape(3,3),bounds_error=True)
    guess=interp(np.column_stack((model.k,model.m)))
    z=guess[1:]-guess[0]
    seed=[]
    target=.55
    for lm in (0.,.05,.15,.30,.55):
        candidate,diag=root_at_match(model,f,2.5,z,lm,nq,nx,maxfev)
        seed.append(diag)
        print("SEED_STAGE",json.dumps(diag),flush=True)
        if diag["relative_residual"]>=1e-7:
            report=dict(status="INTERMEDIATE_ROOT_NOT_REPRODUCED",
                        seed=seed,certified_private_root=False,
                        stationary_GE=False)
            (output/"private_5x5_global_seed_audit.json").write_text(
                    json.dumps(report,indent=2)+"\n",encoding="utf-8")
            return report
        z=candidate
    rel=np.r_[0.,z]
    raw=complete_operator(rel,model,f,2.5,target,nq,nx)
    V=rel+raw[0]/(1-model.p.beta)
    near=complete_operator(V,model,f,2.5,target,nq,nx)
    coarse_sup=float(max(abs(near-V)))
    sourceT,yold,dold,kkt=endogenous_operator(V,f,2.5,model,nq,nx)
    y=np.zeros_like(yold)
    d=np.zeros_like(dold)
    rows=[]
    for buyer in range(model.n):
        for seller in range(model.n):
            if f[buyer]<=1e-15 and f[seller]<=1e-15:continue
            tic=time.monotonic()
            ans=solve_pair(model,V,2.5,buyer,seller)
            y[buyer,seller]=ans.y
            d[buyer,seller]=ans.d
            oldlog=(nash_score(yold[buyer,seller],dold[buyer,seller],
                        buyer,seller,model,V,2.5)
                    if yold[buyer,seller]>0 else float("-inf"))
            if np.isfinite(oldlog) and np.isfinite(ans.log_nash):
                improvement=float(ans.log_nash-oldlog)
            else:improvement=None
            rows.append(dict(buyer=buyer,seller=seller,
                old_y=float(yold[buyer,seller]),old_d=float(dold[buyer,seller]),
                convex_y=float(ans.y),convex_d=float(ans.d),
                old_nash_log=(oldlog if np.isfinite(oldlog) else None),
                convex_nash_log=(ans.log_nash if np.isfinite(ans.log_nash) else None),
                log_improvement=improvement,
                dcp_no_solver_failure=bool(ans.dcp_pass),
                convex_branches_solved=int(ans.triangles_solved),
                convex_solver_seconds=time.monotonic()-tic))
            print("CONVEX_5X5_PAIR",buyer,seller,
                  "improvement",improvement,"branches",ans.triangles_solved,
                  flush=True)
    p=model.p
    Tfrozen=_frozen_operator(V,f,2.5,model.k,model.m,
                  model.edges,p.beta,p.b,p.eta,p.alpha,p.A,p.delta,
                  p.Ntypes,y,d)
    T0=cm_outside(model,V,2.5)
    Tglobal=T0+target*(Tfrozen-T0)
    new_sup=float(max(abs(Tglobal-V)))
    oldfull=T0+target*(sourceT-T0)
    rows_improve=[x["log_improvement"] for x in rows
                  if x["log_improvement"] is not None]
    report=dict(status="INTERMEDIATE_GLOBAL_NASH_AUDIT_EXECUTED",
       grid=[5,5],price=2.5,matching_rate_multiplier=target,
       partner_state=[1.5,1.],relevant_pairs=len(rows),
       convex_positive_contracts=int(np.count_nonzero(y)),
       surrogate_positive_contracts=int(np.count_nonzero(yold)),
       coarse_Bellman_sup=coarse_sup,
       old_operator_Bellman_sup=float(max(abs(oldfull-V))),
       globally_reoptimized_Bellman_sup=new_sup,
       max_log_Nash_improvement=(max(rows_improve) if rows_improve else None),
       no_reported_convex_solver_failure=all(x["dcp_no_solver_failure"] for x in rows),
       seed=seed,elapsed_seconds=time.monotonic()-start,
       globally_optimal_5x5_private_root_certified=False,
       exact_interval_global_optimality_proof=False,
       source_rate_5x5_fixed_point=False,stationary_GE=False)
    with (output/"private_5x5_global_seed_pairs.csv").open("w",newline="",encoding="utf-8") as fh:
        wr=csv.DictWriter(fh,fieldnames=list(rows[0]))
        wr.writeheader();wr.writerows(rows)
    (output/"private_5x5_global_seed_audit.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("GLOBAL_SEED_SUMMARY",json.dumps({k:v for k,v in report.items()
                                            if k!="seed"}),flush=True)
    return report


if __name__=="__main__":
    run()
