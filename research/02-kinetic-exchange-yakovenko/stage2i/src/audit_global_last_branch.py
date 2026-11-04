"""Independent all-49 global Nash test at the .85 active-set branch.

This reuses the original convex oracle; it is NOT a globally optimal
root solver and cannot certify lambda=1.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for src in (HERE/"src",BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
            BASE/"stage2g"/"src",BASE/"stage2e"/"src",
            BASE/"stage2c"/"src"):
    sys.path.insert(0,str(src))
from conditional_kkt import ConditionalKKT,independent_candidate_check
from active_nash import active_operator
from solve_5x5_active import active_complete
from continuous_core import ContinuousModel
from molico_grid import Calibration

def run(out=None):
    out=Path(out) if out else HERE/"results"
    out.mkdir(parents=True,exist_ok=True)
    data=np.load(out/"active_set_last_accepted.npz")
    lm=float(data["matching_multiplier"])
    u=np.asarray(data["joint_unknown"])
    flags=np.asarray(data["binding_payment_flags"],dtype=bool)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    base=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    z=np.asarray(base["relative_value"])
    v=np.r_[0.,z]
    original_lambda=float(base["matching_multiplier"])
    raw=active_complete(v,model,f,2.5,original_lambda)
    V=v+raw[0]/(1-model.p.beta)
    _,y,d,_,_=active_operator(V,f,2.5,model,9,7)
    template=ConditionalKKT(model,2.5,y,d)
    assert len(flags)==len(template.pairs)
    upper={pair:bool(flags[n]) for n,pair in enumerate(template.pairs)}
    system=ConditionalKKT(model,2.5,y,d,upper_override=upper)
    assert len(u)==system.length,(len(u),system.length)
    diag,q,payment,value,T=system.validate(u,lm)
    result=independent_candidate_check(
        system,u,lm,global_check=True,export_folder=None)
    result.update(reference_matching_multiplier=lm,price=2.5,grid=[5,5],
                  source_rate_full_matching_certified=False,
                  source_artifact_run=41772112814)
    (out/"global_dominance_last_branch.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("LAST_BRANCH_GLOBAL",json.dumps(result),flush=True)
    return result

if __name__=="__main__":
    run()
