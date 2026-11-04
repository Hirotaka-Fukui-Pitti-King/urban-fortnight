"""Price/liquidity-value homotopy at the paper's FULL matching intensity.

This is a separate conditional-private path from matching-intensity homotopy:
hold the source matching probability 1/Ntypes fixed throughout, start at a
large finite price (nominal cash has small real purchasing power), then
continue to the requested p=2.5. Each trial recomputes endogenous bilateral
Nash contracts and CM portfolios. The endpoint is NOT certified without an
independent all-pair convex reoptimization. No monetary GE is claimed.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for q in (ROOT/"src",ROOT/"scripts",BASE/"stage2g"/"src",
          BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(q))
from solve_5x5_active import active_root,active_complete
from solve_private_5x5 import cm_outside
from continuous_core import ContinuousModel
from molico_grid import Calibration


def run(folder=ROOT/"results",initial_price=100.,target_price=2.5,
        maxfev=250,max_trials=35):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(model.n)
    assert model.k[12]==1.5 and model.m[12]==1.
    f[12]=1.
    if initial_price<=target_price or target_price<=0:
        raise ValueError("initial price must exceed positive target")
    # Genuine no-matching private Bellman by contraction, at fixed large price.
    v=np.zeros(model.n)
    no_match_res=float("inf")
    for it in range(1400):
        w=cm_outside(model,v,initial_price)
        no_match_res=float(np.max(np.abs(w-v)))
        v=w
        if no_match_res<1e-9:
            break
    z=v[1:]-v[0]
    reports=[]
    # Start at full matching: the high-price economy may have (nearly)
    # absent monetary services but is not claimed to clear money.
    ztrial,first=active_root(model,f,initial_price,z,1.,
                             nq=13,nx=11,maxfev=maxfev)
    reports.append(dict(price=float(initial_price),stage="initial_full_matching",
                        **first,accepted=bool(first["sup"]<1e-7)))
    print("PRICE_CONTINUATION",json.dumps(reports[-1]),flush=True)
    current=float(initial_price)
    reached=first["sup"]<1e-7
    if reached:z=ztrial
    step=.5
    trial_count=0
    while reached and current>target_price*(1+1e-12) and trial_count<max_trials:
        if step<.006:
            break
        trial_count+=1
        proposal=float(max(target_price,current*math.exp(-step)))
        nxt,diag=active_root(model,f,proposal,z,1.,
                             nq=13,nx=11,maxfev=maxfev)
        accepted=diag["sup"]<1e-7
        reports.append(dict(stage="decrease_price",price=proposal,
                            **diag,accepted=bool(accepted)))
        print("PRICE_CONTINUATION",json.dumps(reports[-1]),flush=True)
        if accepted:
            z=nxt
            current=proposal
            step=min(.8,step*1.2)
            np.savez(folder/"5x5_price_path_last_accepted.npz",
                 relative_value=z,price=current,matching_multiplier=1.)
        else:
            step*=.5
    at_target=reached and abs(current-target_price)<1e-10
    final={}
    if at_target:
        full=np.r_[0.,z]
        op=active_complete(full,model,f,target_price,1.,nq=19,nx=15)
        V=full+op[0]/(1.-model.p.beta)
        independent=active_complete(V,model,f,target_price,1.,nq=19,nx=15)
        final=dict(independent_fast_sup=float(np.max(np.abs(independent-V))))
        np.savez(folder/"private_5x5_price_candidate.npz",
                 V=V,relative_value=z,f=f,k=model.k,m=model.m,
                 price=target_price,matching_multiplier=1.)
    report=dict(status=("FULL_MATCHING_PRICE_PATH_CANDIDATE" if at_target else
                        "FULL_MATCHING_PRICE_PATH_NOT_CONVERGED"),
                grid=[5,5],source_matching_multiplier=1.,
                initial_price=initial_price,source_price=target_price,
                no_match_initial_sup=no_match_res,
                reached_price=current,source_price_candidate=bool(at_target),
                independent_fast_end=final,
                global_Nash_allpair_certified=False,
                private_5x5_fixed_point_certified=False,
                stationary_GE=False,iterations=reports,
                elapsed_seconds=time.monotonic()-start)
    (folder/"private_5x5_price_continuation.json").write_text(
       json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("PRICE_CONTINUATION_SUMMARY",
          json.dumps({k:v for k,v in report.items() if k!="iterations"}),flush=True)
    return report


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--initial-price",type=float,default=100.)
    a.add_argument("--maxfev",type=int,default=250)
    a.add_argument("--max-trials",type=int,default=35)
    opts=a.parse_args()
    run(initial_price=opts.initial_price,maxfev=opts.maxfev,
        max_trials=opts.max_trials)
