"""Try economically distinct global-Nash contract branches from the real 0.85 KKT root.

The two challengers below were obtained from independent all-49 convex Nash
reoptimization in Actions 41772366085 at exactly lambda=.850006103515625.
Unlike value perturbation probes, this is a genuine conditional equilibrium
root-correction attempt after changing the offending contract branches.
A branch is never called a full Nash equilibrium without independent
global-Nash verification on the *new* value function.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for folder in (HERE/"src",BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
               BASE/"stage2g"/"src",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(folder))
from conditional_kkt import ConditionalKKT,fit_step,independent_candidate_check
from continuous_core import ContinuousModel
from molico_grid import Calibration
from active_nash import active_operator
from solve_5x5_active import active_complete
from private_nash_bellman import nash_score

CHALLENGERS={
    (19,12):(1.0389497133382632,1.4120800135268812),
    (23,12):(1.042514092199733,1.3449249227908484),
}

def run(folder=None, max_nfev=60):
    out=Path(folder) if folder else HERE/"results"
    out.mkdir(parents=True,exist_ok=True)
    saved=np.load(out/"active_set_last_accepted.npz")
    lm=float(saved["matching_multiplier"])
    assert abs(lm-0.850006103515625)<1e-8,lm
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    original=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    z0=np.asarray(original["relative_value"])
    raw0=active_complete(np.r_[0.,z0],model,f,2.5,
                         float(original["matching_multiplier"]))
    V0=np.r_[0.,z0]+raw0[0]/(1.-model.p.beta)
    _,y0,d0,_,_=active_operator(V0,f,2.5,model)
    base=ConditionalKKT(model,2.5,y0,d0)
    flag=np.asarray(saved["binding_payment_flags"],dtype=bool)
    assert len(flag)==len(base.pairs)==39
    override={pair:bool(flag[n]) for n,pair in enumerate(base.pairs)}
    u0=np.asarray(saved["joint_unknown"])
    system=ConditionalKKT(model,2.5,y0,d0,upper_override=override)
    assert len(u0)==system.length,(len(u0),system.length)
    diag,y,d,v,T=system.validate(u0,lm)
    assert diag["conditional_solution"],{
        "bellman":diag["bellman_sup"],"payment":diag["max_payment_upper_violation"]}
    baseline=dict(conditional_Bellman_sup=diag["bellman_sup"],
                  conditional_KKT_pass=diag["conditional_solution"])
    report={"status":"BRANCH_SWITCHING_ATTEMPT_EXECUTED",
            "reference_lambda":lm,"challengers":CHALLENGERS.__repr__(),
            "reference":baseline,"trials":[],
            "source_matching_certified":False,"stationary_GE":False}
    # Distinct candidates are tested singly and jointly. Each uses full
    # endogenous Bellman-KKT corrections, not a frozen-contract Bellman update.
    best=None
    for subset in (((19,12),),((23,12),),((19,12),(23,12))):
        q=y.copy();pay=d.copy()
        old_scores={};challenger_scores={}
        for pair in subset:
            i,j=pair
            old_scores[str(pair)]=float(nash_score(
                q[i,j],pay[i,j],i,j,model,v,2.5))
            q[i,j],pay[i,j]=CHALLENGERS[pair]
            challenger_scores[str(pair)]=float(nash_score(
                q[i,j],pay[i,j],i,j,model,v,2.5))
        # Fixed payment-cap active sets are inherited from the last accepted
        # conditional branch, and CM portfolio optima are reoptimized at every
        # residual; crossing CM kinks may prevent smooth KKT correction.
        start=system.initialize(v[1:],q,pay)
        try:
            u,fit,_=fit_step(system,start,lm,max_nfev=max_nfev)
            result,yy,dd,vv,_=system.validate(u,lm)
            # Verify challengers retain their economic contract identity.
            changes={str(pair):dict(
                quantity=float(yy[pair]),payment=float(dd[pair]),
                distance_from_old=float(max(
                    abs(yy[pair]-y[pair]),abs(dd[pair]-d[pair]))),
                distance_from_challenger=float(max(
                    abs(yy[pair]-CHALLENGERS[pair][0]),
                    abs(dd[pair]-CHALLENGERS[pair][1])))) for pair in subset}
            # Compare KKT root against the original competing contract at
            # the corrected V. This is a lower-bound dominance test only.
            best_score=None
            for pair in subset:
                i,j=pair
                s_old=float(nash_score(y[i,j],d[i,j],i,j,model,vv,2.5))
                s_new=float(nash_score(yy[i,j],dd[i,j],i,j,model,vv,2.5))
                gain=s_new-s_old
                best_score=gain if best_score is None else min(best_score,gain)
                changes[str(pair)]["new_minus_old_log_nash"]=gain
            trial={"replaced_pairs":[list(pair) for pair in subset],
                   "original_log_nash":old_scores,
                   "challenger_log_nash":challenger_scores,
                   "corrector":fit,"changes":changes,
                   "root_on_new_branch":bool(result["conditional_solution"] and
                      any(c["distance_from_old"]>1e-3
                          for c in changes.values())),
                   "minimum_log_gain_over_old":best_score}
            if result["conditional_solution"] and (
                    best is None or best_score>best[0]):
                best=(best_score,system,u,trial)
                np.savez(out/"switched_085_conditional_candidate.npz",
                         joint_unknown=u,relative_value=vv[1:],
                         matching_multiplier=lm,
                         binding_payment_flags=flag,
                         conditional_quantity=yy,conditional_payment=dd)
        except Exception as e:
            trial={"replaced_pairs":[list(pair) for pair in subset],
                   "error":repr(e),"root_on_new_branch":False}
        report["trials"].append(trial)
        print("BRANCH_SWITCH_085",json.dumps(trial),flush=True)
    if best is not None:
        _,new_system,u,trial=best
        report["best_branch"]=trial
        # Continue newly switched branch with lambda as a parameter.
        attempts=[]
        for target in (.86,.90,.95,1.):
            try:
                u1,fit,_=fit_step(new_system,u,target,max_nfev=max_nfev)
                attempts.append(fit)
                print("BRANCH_SWITCH_FOLLOW",json.dumps(fit),flush=True)
                if not fit["candidate_accepted"]:
                    break
                u=u1
                if abs(target-1.)<1e-12:
                    independent=independent_candidate_check(
                        new_system,u,target,global_check=True,export_folder=out)
                    report["source_independent"]=independent
                    report["source_matching_certified"]=bool(
                        independent["verified_source_rate_5x5_private_fixedpoint"])
            except Exception as e:
                attempts.append({"target":target,"error":repr(e)})
                break
        report["continuation"]=attempts
    (out/"branch_switch_085.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("BRANCH_SWITCH_SUMMARY",json.dumps({
        "source_matching_certified":report["source_matching_certified"],
        "trial_count":len(report["trials"]),
        "best_branch":report.get("best_branch",{}).get("replaced_pairs"),
        "reached":report.get("continuation",[])[-1].get("lambda_matching")
             if report.get("continuation") else None}),flush=True)
    return report

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-nfev",type=int,default=60)
    args=ap.parse_args()
    run(max_nfev=args.max_nfev)
