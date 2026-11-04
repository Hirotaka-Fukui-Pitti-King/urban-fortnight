"""Independent CM-envelope and Nash KKT derivative audit on saved 5x5 state.

Tests the often-assumed W'(w)=u'(c*) against actual one-sided derivatives
of the piecewise-affine CM optimization, including binding c=0 or vertex
solutions. This is NOT an equilibrium root solver or existence proof.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for p in (BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
          BASE/"stage2g"/"src",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(p))
from continuous_core import cm_opt,ContinuousModel
from molico_grid import Calibration,g
from active_nash import active_operator
from solve_5x5_active import active_complete


def slopes(model,value,price,wealth,h):
    p=model.p
    def W(w):
        if w<0:return np.nan
        return float(cm_opt(w,price,model.k,model.m,value,model.edges,
                            p.beta,p.b,p.eta)[0])
    middle=W(wealth)
    left=(middle-W(wealth-h))/h if wealth>=h else None
    right=(W(wealth+h)-middle)/h
    return left,right


def audit(out=None,steps=(1e-5,1e-6)):
    out=Path(out) if out is not None else ROOT/"results"
    out.mkdir(parents=True,exist_ok=True)
    data=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    lm=float(data["matching_multiplier"])
    vrel=np.r_[0.,data["relative_value"]]
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    price=2.5
    T=active_complete(vrel,model,f,price,lm)
    v=vrel+T[0]/(1-model.p.beta)
    _,y,d,old_kkt,_=active_operator(v,f,price,model,nq=9,nx=7)
    p=model.p
    rows=[]
    for i in range(model.n):
        for j in range(model.n):
            if i!=12 and j!=12 or y[i,j]<=0:continue
            q=float(y[i,j]);x=float(d[i,j]/price)
            wb=(1-p.delta)*model.k[i]+model.m[i]/price
            ws=(1-p.delta)*model.k[j]+model.m[j]/price
            wbuy=wb+q-x
            wsell=ws+x
            if wbuy<=0 or wsell<=0:continue
            outside_b=float(cm_opt(wb,price,model.k,model.m,v,model.edges,
                                     p.beta,p.b,p.eta)[0])
            outside_s=float(cm_opt(ws,price,model.k,model.m,v,model.edges,
                                     p.beta,p.b,p.eta)[0])
            B,kb,mb,cb=cm_opt(wbuy,price,model.k,model.m,v,model.edges,
                              p.beta,p.b,p.eta)
            S,ks,ms,cs=cm_opt(wsell,price,model.k,model.m,v,model.edges,
                              p.beta,p.b,p.eta)
            B-=outside_b
            S-=outside_s+g(q,model.k[j],p.alpha,p.A)
            ell=(q/(p.A*model.k[j]**p.alpha))**(1/(1-p.alpha))
            gprime=ell/(q*(1-p.alpha)*(1-ell)**2)
            row=dict(buyer=i,seller=j,quantity=q,payment=float(d[i,j]),
                     buyer_consumption=float(cb),seller_consumption=float(cs),
                     buyer_surplus=float(B),seller_surplus=float(S),
                     payment_bound=bool(abs(d[i,j]-model.m[i])<1e-7),
                     q_bound=bool(abs(q-x)<1e-7),
                     old_buyer_marginal=float((cb+p.b)**(-p.eta)),
                     old_seller_marginal=float((cs+p.b)**(-p.eta)))
            for h in steps:
                bl,br=slopes(model,v,price,wbuy,h)
                sl,sr=slopes(model,v,price,wsell,h)
                key=f"{h:.0e}"
                row[key]=dict(B_left=bl,B_right=br,S_left=sl,S_right=sr,
                    q_foc_minmax=sorted([
                        p.theta*bv/max(B,1e-20)-(1-p.theta)*gprime/max(S,1e-20)
                        for bv in (bl,br) if bv is not None]),
                    x_foc_minmax=sorted([
                        -p.theta*bv/max(B,1e-20)+(1-p.theta)*sv/max(S,1e-20)
                        for bv in (bl,br) if bv is not None
                        for sv in (sl,sr) if sv is not None]))
            key=f"{steps[-1]:.0e}"
            high=row[key]
            row["buyer_envelope_gap"]=max(abs(s-row["old_buyer_marginal"])
                    for s in (high["B_left"],high["B_right"]) if s is not None)
            row["seller_envelope_gap"]=max(abs(s-row["old_seller_marginal"])
                    for s in (high["S_left"],high["S_right"]) if s is not None)
            rows.append(row)
    affected=sorted(rows,key=lambda r:max(
        r["buyer_envelope_gap"],r["seller_envelope_gap"]),reverse=True)
    report=dict(status="INDEPENDENT_CM_ENVELOPE_AUDIT_EXECUTED",
                source_run=41748837033,lambda_matching=lm,grid=[5,5],
                price=price,positive_contracts=len(rows),
                max_buyer_CM_envelope_gap=max([x["buyer_envelope_gap"] for x in rows]or[0]),
                max_seller_CM_envelope_gap=max([x["seller_envelope_gap"] for x in rows]or[0]),
                consumption_zero_buyer=sum(x["buyer_consumption"]<1e-10 for x in rows),
                consumption_zero_seller=sum(x["seller_consumption"]<1e-10 for x in rows),
                count_marginal_discrepancy_gt_1e2=sum(max(
                    x["buyer_envelope_gap"],x["seller_envelope_gap"])>1e-2
                    for x in rows),
                top_pairs=affected[:8],
                prior_candidate_max_kkt=float(old_kkt),
                source_rate_private_fixedpoint_verified=False,
                no_fixedpoint_nonexistence_claim=True)
    (out/"cm_envelope_derivative_audit.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("CM_ENVELOPE_AUDIT",json.dumps({k:v for k,v in report.items()
          if k!="top_pairs"}),flush=True)
    for row in affected[:8]:
        print("CM_ENVELOPE_PAIR",json.dumps(row),flush=True)
    return report


if __name__=="__main__":
    audit()
