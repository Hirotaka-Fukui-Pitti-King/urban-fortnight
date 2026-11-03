"""Independent dense rectangular Nash benchmark at the certified private V.

A nonnegative improvement over candidate is a LOWER BOUND on its true
suboptimality gap, not a numerical upper bound or proof of global optimality.
"""
import csv
import json
import sys
from pathlib import Path
import numpy as np
from numba import njit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from private_nash_bellman import fixture_3x3, endogenous_operator, nash_score, _W
from molico_grid import g

@njit(cache=True)
def dense_reference(i,j,price,k,m,V,edges,beta,b,eta,alpha,A,theta,delta,nq,nx):
    if m[i]<=0 or k[j]<=0:
        return -1e250
    cap=A*k[j]**alpha
    wb=(1-delta)*k[i]+m[i]/price
    ws=(1-delta)*k[j]+m[j]/price
    b0=_W(wb,price,k,m,V,edges,beta,b,eta)
    s0=_W(ws,price,k,m,V,edges,beta,b,eta)
    best=-1e250
    for qi in range(1,nq):
        q=cap*qi/nq
        cost=g(q,k[j],alpha,A)
        for xi in range(1,nx+1):
            x=min(m[i]/price,q)*xi/nx
            bg=_W(wb+q-x,price,k,m,V,edges,beta,b,eta)-b0
            sg=_W(ws+x,price,k,m,V,edges,beta,b,eta)-s0-cost
            if bg<=0 or sg<=0:continue
            val=theta*np.log(bg)+(1-theta)*np.log(sg)
            if val>best:best=val
    return best

def run(folder: Path,nq=201,nx=201):
    model,f=fixture_3x3()
    a=np.load(folder/"private_arrays.npz")
    V=a["value"]
    price=2.5
    # Fresh reoptimization, never merely certify cached saved policies.
    T,y,d,kkt=endogenous_operator(V,f,price,model,nq=23,nx=19)
    rows=[]
    for i in range(model.n):
        for j in range(model.n):
            if f[i]<=0 and f[j]<=0:continue
            dense=float(dense_reference(i,j,price,model.k,model.m,
                                        V-max(V),model.edges,model.p.beta,
                                        model.p.b,model.p.eta,model.p.alpha,
                                        model.p.A,model.p.theta,model.p.delta,nq,nx))
            candidate=float(nash_score(y[i,j],d[i,j],i,j,model,V-max(V),price))
            if dense<=-1e200 and candidate<=-1e200:improve=0.
            else:improve=max(0.,dense-candidate)
            rows.append({"buyer":i,"seller":j,"quantity":float(y[i,j]),
                         "payment":float(d[i,j]),"benchmark_log":dense,
                         "candidate_log":candidate,"benchmark_improvement":improve})
    with (folder/"nash_global_checks.csv").open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    summary={"pairs":len(rows),"positive_pairs":sum(r["quantity"]>0 for r in rows),
             "maximum_dense_improvement":max(r["benchmark_improvement"] for r in rows),
             "nq":nq,"nx":nx,"nash_KKT":kkt,
             "global_optimality_proven":False}
    (folder/"nash_checks.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    run(ROOT/"results")
