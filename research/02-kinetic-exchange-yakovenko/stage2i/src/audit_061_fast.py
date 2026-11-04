"""Fast diagnostic of Nash selection divergence on saved lambda=.61 root."""
from __future__ import annotations
import sys,json,csv
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1];BASE=HERE.parent
for s in (HERE/"src",BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
          BASE/"stage2g"/"src",BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(s))
from conditional_kkt import ConditionalKKT
from active_nash import active_operator
from solve_5x5_active import active_complete
from private_nash_bellman import nash_score
from continuous_core import ContinuousModel
from molico_grid import Calibration

def run(out=None):
    out=Path(out) if out else HERE/"results";out.mkdir(parents=True,exist_ok=True)
    root=np.load(out/"joint_kkt_last_accepted.npz")
    lm=float(root["matching_multiplier"]);u=np.asarray(root["joint_unknown"])
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    base=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    v0=np.r_[0.,base["relative_value"]]
    T=active_complete(v0,model,f,2.5,float(base["matching_multiplier"]))
    vv=v0+T[0]/(1-model.p.beta)
    _,y0,d0,_,_=active_operator(vv,f,2.5,model,9,7)
    sys=ConditionalKKT(model,2.5,y0,d0)
    diag,y,d,v,_=sys.validate(u,lm)
    _,yf,df,_,_=active_operator(v,f,2.5,model,9,7)
    rows=[]
    for i in range(model.n):
        for j in range(model.n):
            if i!=12 and j!=12:continue
            cs=nash_score(y[i,j],d[i,j],i,j,model,v,2.5) if y[i,j]>0 else float("-inf")
            fs=nash_score(yf[i,j],df[i,j],i,j,model,v,2.5) if yf[i,j]>0 else float("-inf")
            row=dict(buyer=i,seller=j,
                     quantity_diff=float(yf[i,j]-y[i,j]),
                     payment_diff=float(df[i,j]-d[i,j]),
                     log_Nash_gain=float(fs-cs) if np.isfinite(cs+fs) else None,
                     candidate_y=float(y[i,j]),candidate_d=float(d[i,j]),
                     fast_y=float(yf[i,j]),fast_d=float(df[i,j]))
            rows.append(row)
    rows.sort(key=lambda a:abs(a["payment_diff"]),reverse=True)
    for x in rows[:10]:print("FAST_DOMINANCE_PAIR",json.dumps(x),flush=True)
    summary=dict(grid=[5,5],matching_multiplier=lm,
       conditional_Bellman_sup=diag["bellman_sup"],
       max_fast_payment_difference=max(abs(x["payment_diff"])for x in rows),
       max_positive_fast_log_Nash_gain=max(
           [x["log_Nash_gain"] for x in rows if x["log_Nash_gain"] is not None]+[0.]),
       positive_Nash_gain_pairs=sum(x["log_Nash_gain"] is not None and
                                   x["log_Nash_gain"]>1e-8 for x in rows),
       largest_differences=rows[:10],global_Nash_certified=False,
       full_source_rate_root_certified=False)
    (out/"fast_policy_divergence_061.json").write_text(
       json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("FAST_DOMINANCE_SUMMARY",json.dumps(summary),flush=True)
    return summary

if __name__=="__main__":
    run()
