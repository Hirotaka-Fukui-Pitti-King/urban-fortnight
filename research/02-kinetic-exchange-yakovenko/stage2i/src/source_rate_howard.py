"""Independent full-matching 5x5 attempt via fixed-contract Bellman contraction.

Unlike the unsuccessful smooth Jacobian continuation, this alternates the
exact fixed-contract value operator with a reoptimized candidate Nash oracle.
Every reported convergence claim still requires independent convex Nash.
The original matching rate is ONE throughout, not a modified economic model.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for item in (HERE/"src",BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
             BASE/"stage2g"/"src",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(item))
from continuous_core import ContinuousModel,cm_opt
from molico_grid import Calibration
from private_nash_bellman import _frozen_operator
from active_nash import active_operator

def fixed_contract_operator(V, y, d, model, f, price, matching=1.0):
    """CM is reoptimized. A frozen feasible DM policy is held fixed."""
    p=model.p
    V=np.asarray(V,dtype=float)
    # Shift to keep CM-value differences accurately represented.
    offset=float(V.max())
    v=V-offset
    outside=np.array([cm_opt(
        (1-p.delta)*model.k[i]+model.m[i]/price,
        price,model.k,model.m,v,model.edges,p.beta,p.b,p.eta)[0]
        for i in range(model.n)])
    with_trade=_frozen_operator(v,f,price,model.k,model.m,model.edges,
        p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,y,d)
    return outside+matching*(with_trade-outside)+p.beta*offset

def solve_frozen_policy(initial, y, d, model, f, price, *, tolerance=1e-10,
                        maxit=1600):
    """Absolute-value Picard with a beta contraction for fixed contracts."""
    v=np.asarray(initial,float).copy()
    last=np.inf
    for it in range(1,maxit+1):
        new=fixed_contract_operator(v,y,d,model,f,price)
        last=float(np.max(np.abs(new-v)))
        v=new
        if not np.isfinite(last):
            raise FloatingPointError("Invalid frozen-policy Bellman residual")
        if last<tolerance:
            break
    verified=float(np.max(np.abs(
        fixed_contract_operator(v,y,d,model,f,price)-v)))
    return v,dict(iterations=it,last_difference=last,
                  independent_frozen_Bellman_sup=verified,
                  converged=verified<tolerance)

def fast_global_candidate_operator(V,model,f,price):
    """Corrected, but NOT globally certified, inherited Nash candidate."""
    p=model.p
    candidate,y,d,kkt,releases=active_operator(
        V,f,price,model,nq=9,nx=7)
    # The active operator is the original matching rate (=1).
    relative=np.asarray(candidate)-np.asarray(V)
    sup=float(np.max(np.abs(relative)))
    return sup,y,d,float(kkt),releases

def solve(*,out=None,iterations=30):
    out=Path(out) if out else HERE/"results"
    out.mkdir(exist_ok=True,parents=True)
    started=time.monotonic()
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(model.n);f[12]=1.
    price=2.5
    previous=out/"active_set_last_accepted.npz"
    if not previous.is_file():
        raise FileNotFoundError("Required 0.85 conditional-root artifact missing")
    seed=np.load(previous)
    lm=float(seed["matching_multiplier"])
    if not abs(lm-.850006103515625)<1e-8:
        raise AssertionError(f"Unexpected prior matching multiplier {lm}")
    from conditional_kkt import ConditionalKKT
    # Reconstruct the exact inherited 0.85 conditional contracts, independently
    # from the saved KKT joint unknown and saved payment binding flags.
    from active_nash import active_operator
    from solve_5x5_active import active_complete
    original=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    zz=np.asarray(original["relative_value"],float)
    rr=np.r_[0.,zz]
    initial_T=active_complete(rr,model,f,price,float(original["matching_multiplier"]))
    initial_V=rr+initial_T[0]/(1-model.p.beta)
    _,Y0,D0,_,_=active_operator(initial_V,f,price,model,nq=9,nx=7)
    reference=ConditionalKKT(model,price,Y0,D0)
    flags=np.asarray(seed["binding_payment_flags"],bool)
    branch=ConditionalKKT(model,price,Y0,D0,upper_override={
        pair:bool(flags[n]) for n,pair in enumerate(reference.pairs)})
    diag,y,d,v,T=branch.validate(np.asarray(seed["joint_unknown"]),lm)
    if not diag["conditional_solution"]:
        raise RuntimeError("Saved conditional KKT point is not valid")
    absolute=v+T[0]/(1-model.p.beta)
    start_sup,*_=fast_global_candidate_operator(absolute,model,f,price)
    # Fixed-contract Bellman solve at ORIGINAL matching rate 1.0.
    frozen_value,fd=solve_frozen_policy(absolute,y,d,model,f,price)
    frozen_source_sup,*_=fast_global_candidate_operator(
        frozen_value,model,f,price)
    print("HOWARD_BASELINE",json.dumps(dict(
        prior_conditional_matching=lm,prior_Bellman_sup=diag["bellman_sup"],
        fast_source_sup_at_085_value=start_sup,
        fixed_contract_source_sup=frozen_source_sup,
        fixed_contract_value_diagnostics=fd)),flush=True)
    # Search two initializations; neither is claimed an equilibrium.
    histories=[]
    best=(float("inf"),None,None)
    for label,V0 in (("conditional_085_value",absolute),
                     ("source_frozen_policy_value",frozen_value)):
        V=np.array(V0,float)
        unchanged=0
        for step in range(iterations):
            r,Y,D,KKT,released=fast_global_candidate_operator(V,model,f,price)
            if r<best[0]:
                best=(r,V.copy(),label)
                np.savez(out/"howard_best_source_candidate.npz",
                         value=V,matching_multiplier=1.,
                         quantity=Y,nominal_payment=D)
            record=dict(initialization=label,iteration=step,
                        fast_Bellman_sup=r,fast_Nash_KKT=KKT,
                        payment_releases=len(released))
            histories.append(record)
            print("HOWARD_ITER",json.dumps(record),flush=True)
            if r<1e-9:
                break
            # Full CM/Bellman evaluation of the *frozen candidate contract*.
            try:
                target,inner=solve_frozen_policy(V,Y,D,model,f,price)
            except (FloatingPointError,ValueError) as err:
                histories.append(dict(initialization=label,
                    iteration=step,step_error=repr(err)))
                break
            choices=[]
            for fraction in (1.,.5,.25,.125,.0625,.03125):
                probe=V+fraction*(target-V)
                value,*_=fast_global_candidate_operator(
                    probe,model,f,price)
                choices.append((value,fraction,probe))
            choices.sort(key=lambda x:x[0])
            winner=choices[0]
            histories[-1]["best_step_fraction"]=winner[1]
            histories[-1]["next_fast_Bellman_sup"]=winner[0]
            histories[-1]["frozen_solver_iterations"]=inner["iterations"]
            if winner[0]<r-1e-9*max(1.,r):
                V=winner[2]
                unchanged=0
            else:
                unchanged+=1
                # Do not disguise discontinuities by contract smoothing.
                # Retain best value and try the other initial condition.
                if unchanged>=2:
                    histories[-1]["stop_reason"]="no_safeguarded_improvement"
                    break
                V=target
    residual,bestV,source=best
    if bestV is None:
        raise RuntimeError("No valid candidate evaluated")
    certified=False
    global_result=None
    if residual<1e-8:
        from convex_nash import solve_pair
        global_y=np.zeros((model.n,model.n))
        global_d=np.zeros_like(global_y)
        unresolved=[]
        for i in range(model.n):
            for j in range(model.n):
                if i!=12 and j!=12: continue
                answer=solve_pair(model,bestV,price,i,j)
                global_y[i,j]=answer.y;global_d[i,j]=answer.d
                if answer.unresolved_branches:
                    unresolved.append([i,j,answer.unresolved_branches])
        residual_vector=fixed_contract_operator(
            bestV,global_y,global_d,model,f,price)-bestV
        global_sup=float(np.max(np.abs(residual_vector)))
        global_result=dict(independent_global_Bellman_sup=global_sup,
            unresolved_conic_branches=unresolved,
            independent_all49_global_reoptimization=True)
        certified=bool(global_sup<1e-8 and not unresolved)
    result=dict(status=("VERIFIED_SOURCE_RATE_5X5" if certified else
                       "SOURCE_RATE_5X5_NOT_VERIFIED"),
        grid=[5,5],price=price,matching_multiplier=1.,
        prior_085_conditional_Bellman_sup=float(diag["bellman_sup"]),
        fast_source_sup_at_prior_value=start_sup,
        source_frozen_policy_diagnostics=fd,
        fast_source_sup_at_frozen_policy_value=frozen_source_sup,
        best_fast_Bellman_sup=residual,
        best_candidate_initialization=source,
        source_all49_global_check=global_result,
        source_private_root_certified=certified,stationary_GE=False,
        iteration_diagnostics=histories,
        elapsed_seconds=time.monotonic()-started)
    (out/"source_rate_howard_summary.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("HOWARD_SUMMARY",json.dumps({k:v for k,v in result.items()
                        if k!="iteration_diagnostics"}),flush=True)
    return result

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--iterations",type=int,default=30)
    args=cli.parse_args()
    solve(iterations=args.iterations)
