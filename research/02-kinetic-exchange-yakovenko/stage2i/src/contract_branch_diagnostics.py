"""Observe economically distinct Nash and CM active-set changes at an inherited root.

The local fast Nash oracle supplies candidates, not a global correspondence.
A global convex check is available as an optional independent audit.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import csv
import json
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
for directory in (BASE/"stage2h"/"src", BASE/"stage2h"/"scripts",
                  BASE/"stage2g"/"src", BASE/"stage2e"/"src",
                  BASE/"stage2c"/"src"):
    sys.path.insert(0, str(directory))
from active_nash import active_operator
from solve_5x5_active import active_complete
from private_nash_bellman import nash_grad, nash_score
from continuous_core import ContinuousModel, cm_opt, cm_extreme_portfolios
from molico_grid import Calibration, g


def is_distinct(first, second, qscale, dscale, radius=1e-3):
    """Distinguish economic contracts, not interpolation-triangle labels."""
    if first is None or second is None:
        return first != second
    return max(abs(first[0]-second[0])/max(qscale, 1e-14),
               abs(first[1]-second[1])/max(dscale, 1e-14)) >= radius


def cm_snapshot(model, value, wealth, price, tolerance=1e-9):
    p = model.p
    val, kp, mp, consumption = cm_opt(
        wealth, price, model.k, model.m, value, model.edges,
        p.beta, p.b, p.eta)
    extremes = cm_extreme_portfolios(
        wealth, price, model.k, model.m, value, model.edges,
        p.beta, p.b, p.eta, tolerance)
    # The selected economic portfolio, rather than a triangle ID, is primary.
    # A vertex belongs to several triangles without representing multiplicity.
    return dict(value=float(val), kprime=float(kp), mprime=float(mp),
                consumption=float(consumption),
                near_optimal_money_spread=float(extremes[5]-extremes[2]))


def policy_at(model, value, price, f):
    operator, y, d, max_kkt, released = active_operator(
        value, f, price, model, nq=9, nx=7)
    return operator, y, d, max_kkt, released


def snapshot(model, value, price, f, y, d, buyer, seller):
    p = model.p
    q = float(y[buyer,seller])
    payment = float(d[buyer,seller])
    wb = (1-p.delta)*model.k[buyer]+model.m[buyer]/price
    ws = (1-p.delta)*model.k[seller]+model.m[seller]/price
    buyer_out = cm_snapshot(model,value,wb,price)
    seller_out = cm_snapshot(model,value,ws,price)
    if not (q>0 and payment>0):
        return dict(y=0.,d=0.,log_nash=None,buyer_surplus=0.,
                    seller_surplus=0.,payment_upper=False,
                    kkt_payment_violation=None,cm_buyer=None,
                    cm_seller=None,cm_buyer_out=buyer_out,
                    cm_seller_out=seller_out)
    b = cm_snapshot(model,value,wb+q-payment/price,price)
    s = cm_snapshot(model,value,ws+payment/price,price)
    bg=b["value"]-buyer_out["value"]
    sg=s["value"]-seller_out["value"]-float(g(q,model.k[seller],p.alpha,p.A))
    score=float(nash_score(q,payment,buyer,seller,model,value,price))
    derivative = nash_grad(q,payment,buyer,seller,price,model.k,model.m,
                           value,model.edges,p.beta,p.b,p.eta,p.alpha,
                           p.A,p.theta,p.delta)
    upper=payment >= model.m[buyer]*(1-1e-7)
    gx=float(derivative[1])
    # Maximum under d <= money: derivative at binding upper bound >= 0.
    violation = max(0.,-gx) if upper else abs(gx)
    return dict(y=q,d=payment,log_nash=score if np.isfinite(score) else None,
                buyer_surplus=float(bg),seller_surplus=float(sg),
                payment_upper=bool(upper),
                kkt_quantity_abs=float(abs(derivative[0])),
                kkt_payment_violation=float(violation),
                cm_buyer=b,cm_seller=s,cm_buyer_out=buyer_out,
                cm_seller_out=seller_out)


def diagnose(folder=None, global_audit=False, scale=3e-6):
    folder = Path(folder) if folder is not None else HERE/"results"
    folder.mkdir(parents=True,exist_ok=True)
    saved = BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz"
    if not saved.is_file():
        raise FileNotFoundError("Required CI artifact missing: "+str(saved))
    data=np.load(saved)
    z=np.asarray(data["relative_value"],float)
    multiplier=float(data["matching_multiplier"])
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n)
    f[12]=1.
    price=2.5
    rel=np.r_[0.,z]
    T=active_complete(rel,model,f,price,multiplier)
    value=rel+T[0]/(1-model.p.beta)
    raw,y0,d0,kkt,released=policy_at(model,value,price,f)
    outside=np.array([cm_opt(
        (1-model.p.delta)*model.k[i]+model.m[i]/price,
        price,model.k,model.m,value,model.edges,
        model.p.beta,model.p.b,model.p.eta)[0]
        for i in range(model.n)])
    # A direction derived from first-order exposure to matching; NOT a
    # tangent to the endogenous equilibrium correspondence.
    direction=raw-outside
    direction-=direction[0]
    direction/=max(np.max(np.abs(direction)),1e-12)
    probes=[(-scale,value-scale*direction),(0.,value),
            (scale,value+scale*direction)]
    predictions=[]
    for eps,v in probes:
        _,y,d,_,_=policy_at(model,v,price,f)
        predictions.append((eps,v,y,d))
    rows=[]
    all_global_pass=True
    for buyer in range(model.n):
        for seller in range(model.n):
            if buyer!=12 and seller!=12:
                continue
            cap=model.p.A*model.k[seller]**model.p.alpha
            snapshots=[snapshot(model,v,price,f,yy,dd,buyer,seller)
                       for _,v,yy,dd in predictions]
            anchor=snapshots[1]
            qscale=max(cap,1e-12)
            dscale=max(model.m[buyer],1e-12)
            contract_changes=[is_distinct(
                (anchor["y"],anchor["d"]), (ss["y"],ss["d"]),
                qscale,dscale,1e-3) for ss in (snapshots[0],snapshots[2])]
            cm_changes=[]
            for label in ("cm_buyer","cm_seller"):
                center=anchor[label]
                if center is None:
                    cm_changes.append(False)
                    continue
                for point in (snapshots[0],snapshots[2]):
                    other=point[label]
                    if other is None:
                        cm_changes.append(True)
                    else:
                        change=max(abs(other["kprime"]-center["kprime"]),
                                   abs(other["mprime"]-center["mprime"]))
                        cm_changes.append(change>1e-5)
            near_tie=None
            for ss in (snapshots[0],snapshots[2]):
                # Reevaluate distinct perturbed-oracle contracts at ANCHOR V.
                if is_distinct((anchor["y"],anchor["d"]),
                               (ss["y"],ss["d"]),qscale,dscale,1e-3):
                    alt=nash_score(ss["y"],ss["d"],buyer,seller,
                                   model,value,price) if ss["y"]>0 else -np.inf
                    if np.isfinite(alt) and anchor["log_nash"] is not None:
                        gap=max(0.,anchor["log_nash"]-float(alt))
                        near_tie=gap if near_tie is None else min(near_tie,gap)
            global_gap=None
            globally_verified=False
            if global_audit:
                from convex_nash import solve_pair
                res=solve_pair(model,value,price,buyer,seller)
                reference=(res.y,res.d)
                candidate=(anchor["y"],anchor["d"])
                global_gap=(res.log_nash-anchor["log_nash"]
                            if anchor["log_nash"] is not None and
                               np.isfinite(res.log_nash) else None)
                globally_verified=bool(res.unresolved_branches==0 and
                    (global_gap is None or global_gap<1e-7) and
                    not is_distinct(reference,candidate,qscale,dscale,1e-3))
                all_global_pass &= globally_verified
            rows.append(dict(buyer=buyer,seller=seller,
                quantity=anchor["y"],nominal_payment=anchor["d"],
                buyer_surplus=anchor["buyer_surplus"],
                seller_surplus=anchor["seller_surplus"],
                log_nash=anchor["log_nash"],
                payment_upper=anchor["payment_upper"],
                payment_kkt_violation=anchor["kkt_payment_violation"],
                quantity_kkt_abs=anchor.get("kkt_quantity_abs"),
                contract_changed=any(contract_changes),
                cm_portfolio_changed=any(cm_changes),
                cm_near_optimal_money_spread=max(
                    [s["near_optimal_money_spread"] for s in
                     (anchor["cm_buyer"],anchor["cm_seller"])
                     if s is not None] or [0.]),
                distinct_candidate_log_gap=near_tie,
                global_candidate_gap=global_gap,
                global_candidate_pass=globally_verified))
    assert len(rows)==49
    csv_path=folder/"contract_branches.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary=dict(status="EMPIRICAL_CANDIDATE_SWITCHING_AUDIT",
        reference_matching_multiplier=multiplier, price=price,
        relevant_pairs=49, positive_contracts=sum(r["quantity"]>0 for r in rows),
        candidate_contract_changes=sum(r["contract_changed"] for r in rows),
        candidate_CM_changes=sum(r["cm_portfolio_changed"] for r in rows),
        near_tied_distinct_candidate_pairs=sum(
            r["distinct_candidate_log_gap"] is not None and
            r["distinct_candidate_log_gap"]<1e-6 for r in rows),
        max_payment_kkt_violation=max(
            [r["payment_kkt_violation"] for r in rows
             if r["payment_kkt_violation"] is not None] or [0.]),
        probe_value_amplitude=scale,probe_direction="matching_exposure_not_equilibrium_tangent",
        actual_branch_root_tracking=False,global_audit_requested=global_audit,
        all_49_globally_verified_in_this_run=bool(global_audit and all_global_pass),
        full_matching_5x5_fixedpoint_certified=False,stationary_GE=False,
        classification="NOT_YET_IDENTIFIED")
    (folder/"matching_boundary_diagnostics.json").write_text(
        json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("STAGE2I_DIAGNOSIS",json.dumps(summary),flush=True)
    return summary


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--global-audit",action="store_true")
    ap.add_argument("--scale",type=float,default=3e-6)
    args=ap.parse_args()
    diagnose(global_audit=args.global_audit,scale=args.scale)
