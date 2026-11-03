"""Audit Molico--Zhang Section 4 CM-then-DM iteration, not a GE solver.

This is an independently recorded run of the already implemented source
ordering. Never interpret a cleared conditional CM as stationary equilibrium.
"""
from __future__ import annotations
import argparse,csv,json,platform,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE.parent/"stage2c"/"src"))
sys.path.insert(0,str(HERE/"src"))
from molico_grid import Calibration
from continuous_core import ContinuousModel
from source_aligned import (
    make_CM_entrants,clear_CM_entrants,next_DM,
    optimal_CM_entrants,CMPriceFailure
)

def finite_record(values):
    return [float(x) for x in values if np.isfinite(x)]

def audit(maxit=4,alpha_v=.035,alpha_distribution=.035):
    p=Calibration(nk=5,nm=5,kmax=3.,mmax=2.,y_choices=4,d_choices=5)
    model=ContinuousModel(p)
    V=5*(model.k+model.m/3.)+.02*np.sin(model.k)+.003*np.sin(2*model.m)
    entrants=make_CM_entrants(model,1.5,1.)
    price=3.
    hist=[];failure=None
    for it in range(maxit):
        try:
            CM=clear_CM_entrants(model,V,entrants,price_hint=price,M=1.,tol=3e-9)
        except CMPriceFailure as exc:
            scans=[]
            for pc in np.geomspace(.12,40,27):
                try:
                    e=optimal_CM_entrants(model,V,entrants,pc,tol=3e-9)
                    scans.append((float(pc),float(e["minM"]),float(e["maxM"])))
                except (CMPriceFailure,ValueError):
                    continue
            lower=min((v[1] for v in scans),default=None)
            upper=max((v[2] for v in scans),default=None)
            failure=dict(stage="CM_PRICE",iteration=it+1,error=str(exc),
                         scanned_money_min=lower,scanned_money_max=upper,
                         price_scan_points=scans,
                         scanned_envelope_excludes_one=(
                             bool(lower>1 or upper<1)
                             if lower is not None and upper is not None else None))
            break
        VV,next_ent,dm=next_DM(model,V,CM["f"],CM["price"])
        ev=float(np.max(abs(VV-V)))
        eg=float(np.max(abs(next_ent-entrants)))
        mass=float(next_ent.sum())
        mincash=float(next_ent@model.postm)
        cm_money=float(CM["f"]@model.m)
        wealth_current=entrants@(model.postk+model.postm/CM["price"])
        wealth_next=next_ent@(model.postk+model.postm/CM["price"])
        topk=float(CM["f"][model.k>=p.kmax-1e-12].sum())
        topm=float(CM["f"][model.m>=p.mmax-1e-12].sum())
        row=dict(
            iteration=it+1,price=float(CM["price"]),
            bellman_sup=ev,entrant_distribution_sup=eg,
            fiat_at_CM_entry=float(entrants@model.postm),
            fiat_post_CM=cm_money,fiat_post_DM=mincash,
            capital_post_CM=float(CM["f"]@model.k),
            capital_grid_top_mass=topk,money_grid_top_mass=topm,
            maximum_CM_entrants_real_wealth=float(np.max(
                (model.postk+model.postm/CM["price"])[entrants>1e-14])),
            money_demand_min=float(CM["minM"]),
            money_demand_max=float(CM["maxM"]),
            money_mix=float(CM["mix"]),
            CM_budget_gap=float(CM["budget_error"]),
            DM_trade_rate=float(dm["trades"]),
            DM_output=float(dm["output"]),
            accounting_wealth_gap=float(
                wealth_next-(wealth_current-CM["consumption"]
                -p.delta*(CM["f"]@model.k)+dm["output"])),
            mass_error=abs(mass-1)
        )
        hist.append(row)
        if abs(cm_money-1)>1e-9 or abs(mincash-1)>1e-9:
            failure=dict(stage="ACCOUNTING",iteration=it+1,message=row)
            break
        if eg<1e-8 and ev<1e-7 and abs(CM["budget_error"])<1e-9:
            failure=dict(stage="CANDIDATE",iteration=it+1,
                         reason="Requires continuous Nash all-pair and high-grid certification")
            break
        V=(1-alpha_v)*V+alpha_v*VV
        entrants=(1-alpha_distribution)*entrants+alpha_distribution*next_ent
        price=CM["price"]
    status=("CANDIDATE_NOT_CERTIFIED" if failure and failure["stage"]=="CANDIDATE"
            else "STATIONARY_NOT_CONVERGED_OR_FEASIBLE_PRICE_NOT_FOUND")
    report=dict(status=status,source="Molico-Zhang manuscript Section 4 steps 1–8",
        reference_model="5x5 piecewise-affine CM and discrete all-pair Nash; NOT original replication",
        python=platform.python_version(),iterations_attempted=maxit,
        history=hist,failure=failure,
        full_stationary_general_equilibrium=False,
        test_scope="Source-aligned price-before-DM iteration; conditional results only",
        original_grid_adaptivity="Original step 6 changes capital/money grid bounds with wmax and current p; this pilot keeps fixed boundaries")
    out=HERE/"results";out.mkdir(parents=True,exist_ok=True)
    (out/"source_iteration_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    if hist:
        with (out/"source_iteration_audit.csv").open("w",newline="") as file:
            writer=csv.DictWriter(file,fieldnames=list(hist[0]))
            writer.writeheader();writer.writerows(hist)
    print(json.dumps(dict(status=status,rows=len(hist),failure=failure,
        history_summary=[{k:v for k,v in x.items() if k in
            ("iteration","price","bellman_sup","entrant_distribution_sup",
             "money_grid_top_mass","capital_grid_top_mass")} for x in hist]),indent=2))
    assert all(abs(x["fiat_post_DM"]-1)<1e-8 and abs(x["mass_error"])<1e-8 for x in hist)
    assert all(abs(x["CM_budget_gap"])<1e-8 for x in hist)
    assert status!="CANDIDATE_NOT_CERTIFIED", "Candidate needs separate independent certification"
    return report

if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--steps",type=int,default=4)
    parsed=args.parse_args()
    audit(maxit=parsed.steps)
