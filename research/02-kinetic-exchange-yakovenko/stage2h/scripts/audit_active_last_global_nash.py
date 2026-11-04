"""Independent global Nash audit of the LAST ACCEPTED active-set 5x5 root.

The maximum continuation multiplier is not necessarily the paper's multiplier
one. A small fast-operator Bellman residual is never promoted to certification
until all 49 actual trading pairs are reoptimized with convex Nash branches.
This code uses the SAVED relative value and does not recompute an altered seed.
"""
from __future__ import annotations
import csv
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT.parent
for folder in (ROOT/"src",ROOT/"scripts",RESEARCH/"stage2g"/"src",
               RESEARCH/"stage2e"/"src",RESEARCH/"stage2c"/"src"):
    sys.path.insert(0,str(folder))
from active_nash import active_operator
from solve_5x5_active import active_complete
from solve_private_5x5 import cm_outside
from convex_nash import solve_pair
from private_nash_bellman import _frozen_operator,nash_score
from continuous_core import ContinuousModel
from molico_grid import Calibration


def audit(folder=ROOT/"results"):
    folder=Path(folder)
    saved=folder/"private_5x5_active_last_accepted.npz"
    if not saved.exists():
        report=dict(status="NO_ACCEPTED_ACTIVE_ROOT_SAVED",
                    fixed_price_5x5_certified=False,stationary_GE=False)
        (folder/"5x5_active_global_audit.json").write_text(
            json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print("ACTIVE_GLOBAL_AUDIT",json.dumps(report),flush=True)
        return report
    start=time.monotonic()
    x=np.load(saved)
    lm=float(x["matching_multiplier"])
    z=x["relative_value"]
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    price=2.5
    rel=np.r_[0.,z]
    raw=active_complete(rel,model,f,price,lm)
    V=rel+raw[0]/(1.-model.p.beta)
    raw_active,yold,dold,kkt,releases=active_operator(
        V,f,price,model,nq=9,nx=7)
    T0=cm_outside(model,V,price)
    Tactive=T0+lm*(raw_active-T0)
    old_sup=float(np.max(abs(Tactive-V)))
    newy=np.zeros_like(yold)
    newd=np.zeros_like(dold)
    rows=[]
    for buyer in range(model.n):
        for seller in range(model.n):
            if f[buyer]<=1e-15 and f[seller]<=1e-15:
                continue
            ans=solve_pair(model,V,price,buyer,seller)
            newy[buyer,seller]=ans.y
            newd[buyer,seller]=ans.d
            old_score=nash_score(
                float(yold[buyer,seller]),float(dold[buyer,seller]),
                buyer,seller,model,V,price) if yold[buyer,seller]>0 else float("-inf")
            gain=(ans.log_nash-old_score if
                  np.isfinite(ans.log_nash) and np.isfinite(old_score)
                  else (float("inf") if np.isfinite(ans.log_nash) else 0.))
            row=dict(buyer=buyer,seller=seller,
                     active_y=float(yold[buyer,seller]),
                     active_d=float(dold[buyer,seller]),
                     global_y=float(ans.y),
                     global_d=float(ans.d),
                     positive_global=bool(ans.y>0),
                     logNash_improvement=float(gain) if np.isfinite(gain) else None,
                     unresolved_convex_branches=int(ans.unresolved_branches),
                     unresolved_branch_upper=(float(ans.unresolved_branch_upper_log_nash)
                         if np.isfinite(ans.unresolved_branch_upper_log_nash) else None),
                     dcp_solver_pass=bool(ans.dcp_pass))
            rows.append(row)
            print("GLOBAL_5X5",buyer,seller,"delta",gain,
                  "unresolved",ans.unresolved_branches,flush=True)
    p=model.p
    sourceT=_frozen_operator(V,f,price,model.k,model.m,model.edges,
        p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,newy,newd)
    Tcorrected=T0+lm*(sourceT-T0)
    corrected_sup=float(np.max(abs(Tcorrected-V)))
    best_gain=max((row["logNash_improvement"] for row in rows
                   if row["logNash_improvement"] is not None),default=0.)
    missing_improve=sum(
        bool(row["active_y"]==0 and row["global_y"]>0) for row in rows)
    global_success=all(row["dcp_solver_pass"] for row in rows)
    report=dict(status="INDEPENDENT_CONVEX_AUDIT_EXECUTED",
        grid=[5,5],price=price,matching_multiplier=lm,
        source_multiplier_reached=bool(lm>=1.-1e-12),
        relevant_pairs=len(rows),
        active_positive=int(np.count_nonzero(yold)),
        global_positive=int(np.count_nonzero(newy)),
        original_active_Bellman_sup=old_sup,
        Bellman_sup_after_global_reoptimization=corrected_sup,
        max_finite_logNash_improvement=best_gain,
        missed_positive_pairs=missing_improve,
        maximum_unresolved_convex_branches=max(
            (row["unresolved_convex_branches"] for row in rows),default=0),
        all_conic_branch_problems_verified=global_success,
        fixed_price_5x5_certified=bool(lm>=1.-1e-12 and
            global_success and missing_improve==0 and best_gain<1e-8 and
            corrected_sup<1e-8),
        strict_roundoff_interval_certificate=False,
        stationary_GE=False,elapsed_seconds=time.monotonic()-start)
    with (folder/"5x5_active_global_pairs.csv").open(
            "w",newline="",encoding="utf-8") as fcsv:
        writer=csv.DictWriter(fcsv,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    (folder/"5x5_active_global_audit.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("ACTIVE_GLOBAL_AUDIT",json.dumps(report),flush=True)
    return report


if __name__=="__main__":
    audit()
