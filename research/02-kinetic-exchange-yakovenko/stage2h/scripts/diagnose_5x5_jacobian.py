"""Evaluate the *actual* Jacobian of the corrected 5x5 private Bellman map.

Input is the saved, independently all-49 Nash-checked intermediate private
root at lambda=.609033203125 from Actions run 41748837033. Avoid rerunning
hundreds of costly seed-path root solves. This diagnostic cannot prove
existence/nonexistence of a source-rate fixed point.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares,root

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
for p in (ROOT/"src",ROOT/"scripts",BASE/"stage2g"/"src",
          BASE/"stage2e"/"src",BASE/"stage2c"/"src"):
    sys.path.insert(0,str(p))
from solve_5x5_active import active_complete
from continuous_core import ContinuousModel
from molico_grid import Calibration


def run(folder=ROOT/"results"):
    folder=Path(folder)
    sample=folder/"private_5x5_active_last_accepted.npz"
    if not sample.exists():
        raise FileNotFoundError("Missing saved 5x5 root from reference Actions artifact")
    saved=np.load(sample)
    current=float(saved["matching_multiplier"])
    z=np.asarray(saved["relative_value"],dtype=float)
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    f=np.zeros(model.n);f[12]=1.
    def R(v,lm):
        full=np.r_[0.,v]
        t=active_complete(full,model,f,2.5,lm,nq=9,nx=7)
        return t[1:]-t[0]-v

    start=time.monotonic()
    base=R(z,current)
    def derivative(step_factor):
        jac=np.empty((len(z),len(z)))
        for j in range(len(z)):
            h=step_factor*max(1.,abs(float(z[j])))
            direction=np.zeros_like(z);direction[j]=h
            jac[:,j]=(R(z+direction,current)-R(z-direction,current))/(2*h)
        return jac
    J1=derivative(1e-6)
    J2=derivative(1e-5)
    s=np.linalg.svd(J1,compute_uv=False)
    dg=(R(z,current+1e-5)-R(z,current-1e-5))/(2e-5)
    tangent=np.linalg.lstsq(J1,-dg,rcond=1e-10)[0]
    data={
        "status":"SOURCE_RATE_NOT_CERTIFIED",
        "grid":[5,5],"price":2.5,"matching":current,
        "base_sup":float(np.max(abs(base))),
        "jacobian_singular_min":float(s[-1]),
        "jacobian_singular_max":float(s[0]),
        "jacobian_condition":float(s[0]/max(s[-1],1e-300)),
        "jacobian_h_sensitivity_max":float(np.max(abs(J2-J1))),
        "derivative_matching_sup":float(np.max(abs(dg))),
        "tangent_value_sup":float(np.max(abs(tangent))),
        "local_linear_multiplier_step_for_1_value":float(1/max(np.max(abs(tangent)),1e-300)),
        "direct_residual_at_061":float(np.max(abs(R(z,.61)))),
        "direct_residual_at_062":float(np.max(abs(R(z,.62)))),
        "trial_roots":[],
        "globally_optimal_allpair_at_tried_lambda":False,
        "stationary_GE":False
    }
    # A proper trust-region residual solve tests solver dependence, not just
    # another unguarded Newton; independent global Nash remains mandatory.
    for lam in (.61,.62):
        for init_name,guess in (("warm",z),("linear_predictor",z+(lam-current)*tangent)):
            calls=0
            def residual(q):
                nonlocal calls
                calls+=1
                return R(q,lam)
            init_sup=float(np.max(abs(residual(guess))))
            rr=least_squares(residual,guess,method="trf",jac="2-point",
                            diff_step=1e-5,max_nfev=70,ftol=1e-11,
                            xtol=1e-11,gtol=1e-11)
            end_sup=float(np.max(abs(R(rr.x,lam))))
            info=dict(lambda_target=lam,initialization=init_name,
                      initial_sup=init_sup,final_sup=end_sup,
                      evaluations=calls,solver_status=int(rr.status),
                      numerical_candidate=bool(end_sup<1e-8))
            data["trial_roots"].append(info)
            print("JACOBIAN_ROOT_TRIAL",json.dumps(info),flush=True)
            if end_sup<1e-8:
                np.savez(folder/f"5x5_jacobian_trial_{str(lam).replace('.','_')}.npz",
                         relative_value=rr.x,matching_multiplier=lam)
                break
    data["elapsed_seconds"]=time.monotonic()-start
    (folder/"5x5_jacobian_diagnostics.json").write_text(
        json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("JACOBIAN_DIAGNOSTICS",
          json.dumps({k:v for k,v in data.items() if k!="trial_roots"}),flush=True)
    return data


if __name__=="__main__":
    run()
