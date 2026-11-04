"""Independently test actual Nash global dominance on saved conditional .61 root.

The root's KKT and Bellman residual alone cannot prove original equilibrium.
Compare candidate, inherited fast oracle and all 49 convex-reoptimized Nash
solutions at the *same* value function. Never certify unresolved conic branches.
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for src in (HERE/"src",BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
            BASE/"stage2g"/"src",BASE/"stage2e"/"src",
            BASE/"stage2c"/"src"):
    sys.path.insert(0,str(src))
from continuous_core import ContinuousModel,cm_opt
from molico_grid import Calibration
from active_nash import active_operator
from solve_5x5_active import active_complete
from conditional_kkt import ConditionalKKT
from private_nash_bellman import nash_score,_frozen_operator
from convex_nash import solve_pair


def audit(out=None):
    out=Path(out) if out else HERE/"results"
    out.mkdir(parents=True,exist_ok=True)
    obj=np.load(out/"joint_kkt_last_accepted.npz")
    lm=float(obj["matching_multiplier"])
    u=np.asarray(obj["joint_unknown"])
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    old=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    z0=np.asarray(old["relative_value"]);v0=np.r_[0.,z0]
    raw=active_complete(v0,model,f,2.5,float(old["matching_multiplier"]))
    V0=v0+raw[0]/(1-model.p.beta)
    _,old_y,old_d,_,_=active_operator(V0,f,2.5,model,9,7)
    sys=ConditionalKKT(model,2.5,old_y,old_d)
    assert len(u)==sys.length,(len(u),sys.length)
    diag,cy,cd,v,T=sys.validate(u,lm)
    fast,fy,fd,_,_=active_operator(v,f,2.5,model,9,7)
    gy=np.zeros_like(cy);gd=np.zeros_like(cd)
    rows=[]
    for i in range(model.n):
        for j in range(model.n):
            if i!=12 and j!=12:continue
            result=solve_pair(model,v,2.5,i,j)
            gy[i,j]=result.y
            gd[i,j]=result.d
            cs=nash_score(float(cy[i,j]),float(cd[i,j]),
                          i,j,model,v,2.5) if cy[i,j]>0 else float("-inf")
            fs=nash_score(float(fy[i,j]),float(fd[i,j]),
                          i,j,model,v,2.5) if fy[i,j]>0 else float("-inf")
            gap=(result.log_nash-cs if np.isfinite(cs) and np.isfinite(
                result.log_nash) else None)
            fastgap=(fs-cs if np.isfinite(cs) and np.isfinite(fs) else None)
            row=dict(buyer=i,seller=j,conditional_quantity=float(cy[i,j]),
               conditional_payment=float(cd[i,j]),
               fast_quantity=float(fy[i,j]),fast_payment=float(fd[i,j]),
               global_quantity=float(result.y),global_payment=float(result.d),
               conditional_log_nash=float(cs) if np.isfinite(cs) else None,
               global_log_nash=float(result.log_nash) if
                   np.isfinite(result.log_nash) else None,
               global_objective_improvement=gap,
               fast_objective_improvement=fastgap,
               payment_difference=float(abs(cd[i,j]-result.d)),
               quantity_difference=float(abs(cy[i,j]-result.y)),
               unresolved_branches=int(result.unresolved_branches),
               dominant_unresolved_bound=float(
                    result.unresolved_branch_upper_log_nash) if
                    np.isfinite(result.unresolved_branch_upper_log_nash) else None)
            rows.append(row)
            print("STAGE2I_GLOBAL_PAIR",json.dumps(row),flush=True)
    p=model.p
    baseline=np.array([cm_opt((1-p.delta)*model.k[s]+
      model.m[s]/2.5,2.5,model.k,model.m,v,model.edges,
      p.beta,p.b,p.eta)[0] for s in range(model.n)])
    tt=_frozen_operator(v,f,2.5,model.k,model.m,model.edges,
       p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,gy,gd)
    correct=baseline+lm*(tt-baseline)
    bellman=float(np.max(np.abs(correct[1:]-correct[0]-v[1:])))
    finite=[a["global_objective_improvement"] for a in rows
            if a["global_objective_improvement"] is not None]
    report=dict(status="ACTUAL_GLOBAL_NASH_AUDIT",
       matching_multiplier=lm,grid=[5,5],price=2.5,pairs=49,
       conditional_Bellman_sup=float(diag["bellman_sup"]),
       conditional_KKT_pass=bool(diag["conditional_solution"]),
       global_reoptimized_Bellman_sup=bellman,
       max_finite_global_log_Nash_improvement=max(finite,default=None),
       num_pairs_with_positive_global_improvement=sum(x>1e-7 for x in finite),
       num_pairs_with_distinct_global_payment=sum(
           a["payment_difference"]>1e-3 for a in rows),
       max_payment_difference=max(a["payment_difference"] for a in rows),
       max_fast_log_nash_improvement=max([
           a["fast_objective_improvement"] for a in rows
           if a["fast_objective_improvement"] is not None] or [0.]),
       unresolved_pairs=[[a["buyer"],a["seller"],a["unresolved_branches"]]
                         for a in rows if a["unresolved_branches"]],
       conditional_equilibrium_global_verified=bool(
         bellman<1e-8 and
         not any(a["unresolved_branches"] for a in rows) and
         all(x<=1e-8 for x in finite)),
       full_source_rate_5x5_certified=False,stationary_GE=False)
    with (out/"global_dominance_061.csv").open(
            "w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    (out/"global_dominance_061.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("STAGE2I_GLOBAL_SUMMARY",json.dumps(report),flush=True)
    return report


if __name__=="__main__":
    audit()
