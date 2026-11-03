"""All 17 relevant Nash pairs: global upper bound and same-policy Bellman check."""
import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from private_nash_bellman import fixture_3x3, _frozen_operator, nash_score
from continuous_core import cm_opt
from molico_grid import g
from nash_global_bounds import bound_nash


def run(folder:Path, gap:float=1e-4, max_boxes:int=100000)->dict:
    model,f=fixture_3x3()
    saved=np.load(folder/"private_arrays.npz")
    V,y,d=saved["value"],saved["y"],saved["d"]
    price=2.5
    p=model.p
    corrected_y=y.copy()
    corrected_d=d.copy()
    rows=[]
    for buyer in range(model.n):
        for seller in range(model.n):
            if f[buyer]<=1e-15 and f[seller]<=1e-15:continue
            W=lambda wealth:float(cm_opt(wealth,price,model.k,model.m,V,
                    model.edges,p.beta,p.b,p.eta)[0])
            cost=lambda qty:float(g(qty,model.k[seller],p.alpha,p.A))
            wb=(1-p.delta)*model.k[buyer]+model.m[buyer]/price
            ws=(1-p.delta)*model.k[seller]+model.m[seller]/price
            initial=(float(y[buyer,seller]),float(d[buyer,seller]/price)) if (
                    y[buyer,seller]>0 and d[buyer,seller]>0) else None
            result=bound_nash(W,cost,wb,ws,model.m[buyer]/price,
                 p.A*model.k[seller]**p.alpha,p.theta,initial=initial,
                 log_gap_tolerance=gap,max_boxes=max_boxes)
            original_score=(nash_score(float(y[buyer,seller]),
                            float(d[buyer,seller]),buyer,seller,model,V,price)
                            if initial is not None else float("-inf"))
            if result.candidate_positive:
                policy_gap=result.upper_log_nash-original_score if (
                           initial is not None) else float("inf")
                corrected_y[buyer,seller]=result.quantity
                corrected_d[buyer,seller]=price*result.real_payment
            else:
                policy_gap=0. if initial is None else float("inf")
                corrected_y[buyer,seller]=0.
                corrected_d[buyer,seller]=0.
            row=dict(buyer=buyer,seller=seller,
                     original_positive=bool(initial is not None),
                     original_quantity=float(y[buyer,seller]),
                     original_payment=float(d[buyer,seller]),
                     policy_log_upper_gap=(float(policy_gap) if np.isfinite(policy_gap) else None),
                     policy_bounded_to_gap=bool(result.bounded_to_tolerance
                                               and policy_gap<=gap+1e-9),
                     **asdict(result))
            rows.append(row)
            print("pair",buyer,seller,"boxes",result.boxes_examined,
                  "gap",result.gap_log_nash,"policy_pass",
                  row["policy_bounded_to_gap"],flush=True)
    newV=_frozen_operator(V,f,price,model.k,model.m,model.edges,
            p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,
            corrected_y,corrected_d)
    gaps=[r["policy_log_upper_gap"] for r in rows]
    summary=dict(price=price,grid=[3,3],relevant_pairs=len(rows),
       positive_pair_count=sum(r["candidate_positive"] for r in rows),
       all_policy_nash_bounded_to_tolerance=all(r["policy_bounded_to_gap"] for r in rows),
       max_policy_upper_gap=(max(gaps) if None not in gaps else None),
       max_search_log_gap=max(r["gap_log_nash"] for r in rows),
       max_boxes_used=max(r["boxes_examined"] for r in rows),
       Bellman_sup_after_global_policy_recheck=float(np.max(np.abs(newV-V))),
       same_contracts_in_recomputed_Bellman=True,
       continuous_state_global_optimality_proven=False,
       numerical_only=True,stationary_GE=False)
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/"all_pair_monotone_bounds.csv").open("w",newline="",encoding="utf-8") as h:
        writer=csv.DictWriter(h,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    (folder/"all_pair_monotone_summary.json").write_text(
         json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return summary


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"results")
    parser.add_argument("--gap",type=float,default=1e-4)
    parser.add_argument("--max-boxes",type=int,default=100000)
    a=parser.parse_args()
    run(a.out,a.gap,a.max_boxes)
