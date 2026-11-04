"""Independent Nash B&B on the one unresolved conic branch of the 5x5 intermediate root.

Loads the *identical* saved private V at matching .609033... and compares
the incumbent contract for buyer 3 / seller 12 to a global numerical
monotonic rectangle bound on the continuous (quantity,real payment) domain.
Does NOT certify a source-rate (lambda=1) root or outward-rounded arithmetic.
"""
import json
import sys
from pathlib import Path
from dataclasses import asdict
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT.parent
for p in (ROOT/"src",ROOT/"scripts",RESEARCH/"stage2g"/"src",
          RESEARCH/"stage2e"/"src",RESEARCH/"stage2c"/"src"):
    sys.path.insert(0,str(p))
from nash_global_bounds import bound_nash
from private_nash_bellman import nash_score
from active_nash import active_operator
from solve_5x5_active import active_complete
from continuous_core import ContinuousModel,cm_opt
from molico_grid import Calibration,g


def run(folder=ROOT/"results"):
    folder=Path(folder)
    arr=np.load(folder/"private_5x5_active_last_accepted.npz")
    lm=float(arr["matching_multiplier"])
    z=np.asarray(arr["relative_value"])
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(model.n);f[12]=1.
    price=2.5
    rel=np.r_[0.,z]
    t=active_complete(rel,model,f,price,lm)
    v=rel+t[0]/(1-model.p.beta)
    _,Y,D,_,_=active_operator(v,f,price,model,9,7)
    i,j=3,12
    q,pay=Y[i,j],D[i,j]
    p=model.p
    W=lambda wealth:float(cm_opt(wealth,price,model.k,model.m,v,
                          model.edges,p.beta,p.b,p.eta)[0])
    C=lambda quantity:float(g(quantity,model.k[j],p.alpha,p.A))
    wb=(1-p.delta)*model.k[i]+model.m[i]/price
    ws=(1-p.delta)*model.k[j]+model.m[j]/price
    score=float(nash_score(float(q),float(pay),i,j,model,v,price))
    bound=bound_nash(W,C,wb,ws,model.m[i]/price,
                     p.A*model.k[j]**p.alpha,p.theta,
                     initial=(float(q),float(pay/price)),
                     log_gap_tolerance=1e-6,max_boxes=500_000)
    report=dict(grid=[5,5],matching_multiplier=lm,
        buyer=i,seller=j,old_quantity=float(q),old_payment=float(pay),
        old_nash_log=score,upper_objective_minus_incumbent=float(
            bound.upper_log_nash-score),
        numerical_global_bound_only=True,
        original_source_matching_fixedpoint_certified=False,
        stationary_GE=False,**asdict(bound))
    path=folder/"remaining_5x5_monotone_nash.json"
    path.write_text(json.dumps(report,indent=2)+"\n")
    print("REMAINING_NASH",json.dumps(report),flush=True)
    return report


if __name__=="__main__":
    run()
