"""Payment-active-set event localization and conditional Nash-Bellman homotopy.

Continue actual conditional KKT/Bellman roots (not a frozen fast-Nash oracle).
At binding payment violations, release precisely identified constraints and
resolve adjacent KKT equations. Global Nash reoptimization is independent and
mandatory before source-rate certification. CM switches and folds are not
automatically resolved, and reported numerical success is conditional.
"""
from __future__ import annotations
import csv
import json
import sys
import time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
sys.path.insert(0,str(HERE/"src"))
for src in (BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
            BASE/"stage2g"/"src",BASE/"stage2e"/"src",
            BASE/"stage2c"/"src"):
    sys.path.insert(0,str(src))
from conditional_kkt import ConditionalKKT,fit_step,independent_candidate_check
from active_nash import active_operator
from solve_5x5_active import active_complete
from continuous_core import ContinuousModel
from molico_grid import Calibration


def binding_violations(system,unknown,lm,tol=1e-6):
    diag,_,_,_,_=system.validate(unknown,lm)
    return [dict(buyer=a["buyer"],seller=a["seller"],
                 payment_FOC=a["payment_FOC"],
                 nominal_payment=a["nominal_payment"])
            for a in diag["observations"]
            if a["payment_upper"] and a["payment_FOC"] < -tol]


def release_payment_branch(system,unknown,lm,*,nfev=80):
    violating=binding_violations(system,unknown,lm)
    if not violating:
        return None,None,[],None
    diag,q,payment,value,_=system.validate(unknown,lm)
    overrides={pair:bool(system.upper[n])
               for n,pair in enumerate(system.pairs)}
    for obs in violating:
        overrides[(obs["buyer"],obs["seller"])]=False
    new_system=ConditionalKKT(system.model,system.price,q,payment,
                              upper_override=overrides)
    trials=[]
    for fraction in (0.999,0.98,0.9):
        trial_pay=payment.copy()
        for obs in violating:
            i,j=obs["buyer"],obs["seller"]
            trial_pay[i,j]=min(trial_pay[i,j],
                      fraction*system.model.m[i])
        init=new_system.initialize(value[1:],q,trial_pay)
        try:
            candidate,summary,diagnostics=fit_step(
                 new_system,init,lm,max_nfev=nfev)
        except (ValueError,OverflowError,FloatingPointError) as exc:
            trials.append(dict(error=str(exc),fraction=fraction,
                               candidate_accepted=False))
            continue
        summary["released_seed_fraction"]=fraction
        trials.append(summary)
        if summary["candidate_accepted"]:
            return new_system,candidate,violating,dict(
                accepted=True,trial_summaries=trials)
    return None,None,violating,dict(accepted=False,trial_summaries=trials)


def advance(system,unknown,target,*,nfev=60,max_releases=15):
    trial,summary,_=fit_step(system,unknown,target,max_nfev=nfev)
    attempts=[dict(summary,phase="fixed_payment_active_set")]
    events=[]
    if summary["candidate_accepted"]:
        return system,trial,True,attempts,events
    for index in range(max_releases):
        active,updated,violations,record=release_payment_branch(
            system,trial,target,nfev=max(60,nfev))
        if violations:
            events.extend([dict(lambda_matching=target,
                                kind="payment_upper_release",
                                **v) for v in violations])
        if record is not None:
            attempts.extend(dict(x,phase=f"release_attempt_{index+1}")
                            for x in record["trial_summaries"])
        if active is None:
            return system,trial,False,attempts,events
        system,trial=active,updated
        candidate_diag,_,_,_,_=system.validate(trial,target)
        if candidate_diag["conditional_solution"]:
            return system,trial,True,attempts,events
    return system,trial,False,attempts,events


def persist_csv(path,rows,keys):
    with path.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=keys,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(folder=None,max_nfev=65):
    out=Path(folder) if folder else HERE/"results"
    out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    arr=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    source_lm=float(arr["matching_multiplier"])
    assert abs(source_lm-0.609033203125)<1e-11
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    z=np.asarray(arr["relative_value"])
    v=np.r_[0.,z]
    value_raw=active_complete(v,model,f,2.5,source_lm)
    value=v+value_raw[0]/(1-model.p.beta)
    _,y,d,_,_=active_operator(value,f,2.5,model,9,7)
    system=ConditionalKKT(model,2.5,y,d)
    unknown=system.initialize(z,y,d)
    baseline,_,_,_,_=system.validate(unknown,source_lm)
    assert baseline["conditional_solution"],baseline["bellman_sup"]
    latest=source_lm
    target_index=0
    targets=[.6091,.6092,.6094,.6096,.6098,.61,.615,.62,
             .625,.63,.64,.66,.68,.70,.75,.80,.85,.90,.95,1.]
    rows=[]
    events=[]
    bisections=0
    best_source=None
    while target_index<len(targets):
        target=targets[target_index]
        if target<=latest+1e-13:
            target_index+=1
            continue
        next_sys,next_unknown,accepted,attempts,transition_events=advance(
            system,unknown,target,nfev=max_nfev)
        events.extend(transition_events)
        most_recent=attempts[-1]
        entry=dict(lambda_matching=float(target),
            previous_lambda=float(latest),
            accepted=bool(accepted),
            payment_active_count=int(next_sys.upper.sum()),
            payment_free_count=int(next_sys.nfree),
            Bellman_sup=float(most_recent.get("bellman_sup",np.nan)),
            quantity_KKT_max=float(most_recent.get("kkt_quantity_max",np.nan)),
            payment_KKT_violation=float(most_recent.get(
                "payment_upper_violation",np.nan)),
            released_pairs=len(transition_events),
            attempts_json=json.dumps(attempts))
        if accepted:
            latest=target
            unknown=next_unknown.copy()
            system=next_sys
            exact,_,_,_,_=system.validate(unknown,latest)
            entry.update(Bellman_sup=exact["bellman_sup"],
                quantity_KKT_max=exact["kkt_quantity_max"],
                payment_KKT_violation=exact[
                    "max_payment_upper_violation"])
            np.savez(out/"active_set_last_accepted.npz",
                relative_value=unknown[:24],joint_unknown=unknown,
                matching_multiplier=latest,
                binding_payment_flags=system.upper.astype(np.int8),
                quantity=np.array([exact["observations"][n]["quantity"]
                    for n in range(len(system.pairs))]))
            print("ACTIVE_SET_HOMOTOPY_ACCEPT",
                  json.dumps({k:v for k,v in entry.items()
                              if k!="attempts_json"}),flush=True)
            target_index+=1
        else:
            print("ACTIVE_SET_HOMOTOPY_REJECT",
                  json.dumps({k:v for k,v in entry.items()
                              if k!="attempts_json"}),flush=True)
            # Only refine an interval after explicit KKT corrector failure;
            # never infer nonexistence from unsuccessful correction.
            if target-latest>1e-6 and bisections<14:
                middle=(target+latest)/2.
                targets.insert(target_index,middle)
                bisections+=1
                print("ACTIVE_SET_HOMOTOPY_BISECT",latest,middle,target,flush=True)
            else:
                break
        rows.append(entry)
    # Always attempt the original lambda=1 as a distinct root search if
    # the traced sequence did not attain it.
    if latest<1.-1e-12:
        direct_sys,direct_u,accepted,attempts,transition_events=advance(
            system,unknown,1.,nfev=max_nfev)
        events.extend(transition_events)
        rows.append(dict(lambda_matching=1.,previous_lambda=latest,
            accepted=bool(accepted),
            payment_active_count=int(direct_sys.upper.sum()),
            payment_free_count=int(direct_sys.nfree),
            Bellman_sup=float(attempts[-1].get("bellman_sup",np.nan)),
            quantity_KKT_max=float(attempts[-1].get("kkt_quantity_max",np.nan)),
            payment_KKT_violation=float(attempts[-1].get("payment_upper_violation",np.nan)),
            released_pairs=len(transition_events),
            attempts_json=json.dumps(attempts)))
        if accepted:
            latest=1.
            system,unknown=direct_sys,direct_u
            print("ACTIVE_SET_HOMOTOPY_DIRECT_SOURCE_ACCEPT",flush=True)
    final=independent_candidate_check(system,unknown,latest,
             global_check=abs(latest-1.)<1e-12)
    # This strict flag requires independent 49-pair Nash reoptimization.
    success=bool(final["verified_source_rate_5x5_private_fixedpoint"])
    report=dict(status=("SOURCE_RATE_FULL_GLOBAL_CHECK_PASSED" if success
                        else "SOURCE_RATE_PRIVATE_ROOT_NOT_CERTIFIED"),
       source_rate_multiplier=1.,
       last_accepted_multiplier=latest,
       start_multiplier=source_lm,
       baseline_Bellman_sup=baseline["bellman_sup"],
       active_trades=39,
       remaining_payment_upper_count=int(system.upper.sum()),
       payment_release_events=events,
       number_of_step_attempts=len(rows),
       number_of_step_rejections=sum(not x["accepted"] for x in rows),
       bisections=bisections,
       final_independent_check=final,
       source_rate_5x5_verified=success,
       stationary_GE=False,
       elapsed_seconds=time.monotonic()-started)
    persist_csv(out/"homotopy_path.csv",rows,[
        "lambda_matching","previous_lambda","accepted",
        "payment_active_count","payment_free_count","Bellman_sup",
        "quantity_KKT_max","payment_KKT_violation",
        "released_pairs","attempts_json"])
    persist_csv(out/"active_set_events.csv",events,[
        "lambda_matching","kind","buyer","seller",
        "payment_FOC","nominal_payment"])
    (out/"active_set_homotopy_summary.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("ACTIVE_SET_HOMOTOPY_SUMMARY",
          json.dumps({k:v for k,v in report.items()
                      if k!="payment_release_events"}),flush=True)
    return report


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-nfev",type=int,default=65)
    args=ap.parse_args()
    run(max_nfev=args.max_nfev)
