"""Re-check ONE representative pair of the conditional 3x3 solved private V.

This numerical box certificate is against the interpolated W, not the
undiscretized economy. Truncation or lack of an incumbent reports UNRESOLVED.
The final JSON must never claim global Nash optimality on failure.
"""
import argparse
from dataclasses import asdict
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from private_nash_bellman import fixture_3x3, endogenous_operator
from continuous_core import cm_opt
from molico_grid import g
from nash_global_bounds import bound_nash


def run(folder:Path,buyer:int=4,seller:int=4,
        gap:float=.02,max_boxes:int=50000):
    model,f=fixture_3x3()
    data=np.load(folder/"private_arrays.npz")
    V=np.asarray(data["value"],dtype=float)
    p=2.5
    if not 0<=buyer<model.n or not 0<=seller<model.n:
        raise ValueError("state index out of bounds")
    pp=model.p
    if model.m[buyer]<=0 or model.k[seller]<=0:
        raise ValueError("need a potentially trading matched pair")
    # Same CM objective but an entirely distinct global search.
    w=lambda wealth:float(cm_opt(wealth,p,model.k,model.m,V,
                    model.edges,pp.beta,pp.b,pp.eta)[0])
    cost=lambda quantity:float(g(quantity,model.k[seller],pp.alpha,pp.A))
    wb=(1-pp.delta)*model.k[buyer]+model.m[buyer]/p
    ws=(1-pp.delta)*model.k[seller]+model.m[seller]/p
    _,policy_y,policy_d,_=endogenous_operator(V,f,p,model,nq=17,nx=15)
    initial=(float(policy_y[buyer,seller]),float(policy_d[buyer,seller])/p)
    result=bound_nash(w,cost,wb,ws,model.m[buyer]/p,
                      pp.A*model.k[seller]**pp.alpha,
                      pp.theta,initial=initial,
                      log_gap_tolerance=gap,max_boxes=max_boxes)
    record=dict(asdict(result),buyer=buyer,seller=seller,
                price=p,target_log_gap=gap,max_boxes=max_boxes,
                W_approximation="triangular piecewise-affine CM",
                exact_real_arithmetic_proof=False,
                undiscretized_Nash_optimum_certified=False,
                stationary_GE_certified=False)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"nash_monotone_bound_one_pair.json").write_text(
        json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2))
    return record


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"results")
    parser.add_argument("--gap",type=float,default=.02)
    parser.add_argument("--max-boxes",type=int,default=50000)
    parser.add_argument("--buyer",type=int,default=4)
    parser.add_argument("--seller",type=int,default=4)
    args=parser.parse_args()
    run(args.out,args.buyer,args.seller,args.gap,args.max_boxes)
