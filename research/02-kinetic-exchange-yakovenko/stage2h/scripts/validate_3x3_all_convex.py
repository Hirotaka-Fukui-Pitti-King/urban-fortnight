"""Re-solve all 17 positive-mass-relevant 3x3 Nash pairs with convex branches.

This is distinct from the single-pair benchmark. It checks whether the
Stage 2-G private value remains a fixed point after *every* contract is
replaced by a finite-branch convex globally maximizing candidate.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT.parent
for p in (ROOT/"src",RESEARCH/"stage2g"/"src",RESEARCH/"stage2g"/"scripts",
          RESEARCH/"stage2c"/"src",RESEARCH/"stage2e"/"src"):
    sys.path.insert(0,str(p))
from solve_private import WARM_RELATIVE_VALUE
from convex_nash import solve_pair
from private_nash_bellman import fixture_3x3,solve_private,_frozen_operator,nash_score

def run(out=ROOT/"results"):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    t0=time.perf_counter()
    model,f=fixture_3x3()
    x=solve_private(model,f,2.5,np.asarray(WARM_RELATIVE_VALUE),
                    nq=17,nx=15,tolerance=1e-8)
    V=x["value"]
    yy=np.zeros((model.n,model.n))
    dd=np.zeros_like(yy)
    checks=[]
    for i in range(model.n):
        for j in range(model.n):
            if f[i]<=1e-15 and f[j]<=1e-15:
                continue
            res=solve_pair(model,V,2.5,i,j)
            yy[i,j]=res.y
            dd[i,j]=res.d
            origscore=nash_score(float(x["y"][i,j]),float(x["d"][i,j]),
                                 i,j,model,V,2.5)
            if np.isneginf(origscore) and np.isneginf(res.log_nash):
                improvement=0.
            else:
                improvement=float(res.log_nash-origscore)
            checks.append(dict(buyer=i,seller=j,
                quantity=res.y,nominal_payment=res.d,
                log_nash=res.log_nash,
                improvement_vs_stage2g=float(improvement),
                original_quantity=float(x["y"][i,j]),
                original_payment=float(x["d"][i,j]),
                convex_solver_failures=not res.dcp_pass,
                solved_triangle_pairs=res.triangles_solved,
                pruned_triangle_pairs=res.triangles_pruned))
            print("ALL_CONVEX_PAIR",i,j,"Nash gain",improvement,
                  "CVX branches",res.triangles_solved,"DCP",res.dcp_pass,flush=True)
    p=model.p
    newV=_frozen_operator(V,f,2.5,model.k,model.m,model.edges,
         p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,yy,dd)
    delta=float(np.max(np.abs(newV-V)))
    record=dict(status="3x3_CONVEX_GLOBAL_RECHECK",
        price=2.5,grid=[3,3],partner_state=[1.5,1],
        relevant_pairs=len(checks),
        positive_pairs=int(np.count_nonzero(yy)),
        previous_fast_Bellman_sup=x["bellman_sup"],
        full_Bellman_sup_after_all_convex_reoptimized=delta,
        max_absolute_nominal_payment_change=float(np.max(np.abs(dd-x["d"]))),
        max_absolute_output_change=float(np.max(np.abs(yy-x["y"]))),
        max_Nash_log_objective_improvement=max(z["improvement_vs_stage2g"] for z in checks),
        all_convex_subproblems_reported_success=not any(z["convex_solver_failures"] for z in checks),
        candidate_private_3x3_passed=bool(delta<1e-8 and not any(z["convex_solver_failures"] for z in checks)),
        roundoff_rigorous_global_Nash_certification=False,stationary_GE=False,
        elapsed_seconds=time.perf_counter()-t0,pairs=checks)
    (out/"private_3x3_all_convex.json").write_text(json.dumps(record,indent=2)+"\n")
    print("ALL_CONVEX_SUMMARY",json.dumps({k:v for k,v in record.items() if k!="pairs"}),flush=True)
    return record

if __name__=="__main__":
    run()
