"""Independently reoptimize 5x5 matched Nash contracts using convex branches.

Only run after a saved 5x5 private root exists. The positive-mass partner
support is handled in BOTH match directions; every Nash contract returned
by this module is reused in the independently reevaluated Bellman operator.
No invariant distribution or price clearing is inferred.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for p in (ROOT/"src",BASE/"stage2g"/"src",BASE/"stage2c"/"src",
          BASE/"stage2e"/"src"):
    sys.path.insert(0,str(p))
from convex_nash import solve_pair
from private_nash_bellman import _frozen_operator
from continuous_core import ContinuousModel
from molico_grid import Calibration


def run(out=ROOT/"results", tolerance=1e-8):
    out=Path(out)
    data=out/"private_5x5_candidate.npz"
    if not data.exists():
        print("NOT_RUN: independent globally checked 5x5 candidate unavailable")
        return dict(status="NO_CONVERGED_PRIVATE_5x5_CANDIDATE")
    data=np.load(data)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    V=data["V"]
    f=data["f"]
    assert len(V)==25 and abs(f.sum()-1)<1e-12
    price=2.5
    yy=np.zeros((model.n,model.n))
    dd=np.zeros_like(yy)
    checks=[]
    beginning=time.monotonic()
    for i in range(model.n):
        for j in range(model.n):
            if f[i]<=1e-15 and f[j]<=1e-15:
                continue
            res=solve_pair(model,V,price,i,j)
            yy[i,j]=res.y
            dd[i,j]=res.d
            checks.append(dict(buyer=i,seller=j,quantity=res.y,
                    nominal_payment=res.d,log_nash=res.log_nash,
                    branches_considered=res.triangles_considered,
                    branches_pruned=res.triangles_pruned,
                    branches_solved=res.triangles_solved,
                    successful_subproblems=res.successes,
                    no_solver_failure=res.dcp_pass))
            print("5x5_GLOBAL_PAIR",i,j,res.log_nash,
                  "branches",res.triangles_solved,flush=True)
    t=_frozen_operator(V,f,price,model.k,model.m,model.edges,
                    model.p.beta,model.p.b,model.p.eta,
                    model.p.alpha,model.p.A,model.p.delta,
                    model.p.Ntypes,yy,dd)
    residual=float(np.max(np.abs(t-V)))
    report=dict(status=("CHECKED_PRIVATE_FIXED_POINT" if
                   residual<tolerance and all(q["no_solver_failure"] for q in checks)
                   else "NOT_CERTIFIED"),
                bellman_sup_after_convex_reoptimization=residual,
                relevant_pairs=len(checks),
                positive_contracts=int(np.count_nonzero(yy)),
                all_convex_branches_solved_without_reported_errors=all(
                             q["no_solver_failure"] for q in checks),
                primal_dual_gap_independently_verified=False,
                continuous_state_optimality_proven=False,
                stationary_GE=False,wall_seconds=time.monotonic()-beginning,
                pairs=checks)
    (out/"private_5x5_global_check.json").write_text(
                            json.dumps(report,indent=2)+"\n")
    print("5x5_GLOBAL_FINAL",json.dumps({k:v for k,v in report.items()
                                           if k!="pairs"}),flush=True)
    return report


if __name__=="__main__":
    run()
