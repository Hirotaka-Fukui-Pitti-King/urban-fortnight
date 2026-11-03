"""Reproducible fixed-quoted-price household value and Nash policy audit.

Uses Stage 2-D discrete bargaining, not the original continuous Nash contract
space. No stationary monetary general equilibrium is claimed.
"""
from pathlib import Path
import sys,json,csv,platform
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
sys.path.insert(0,str(HERE.parent/"stage2d"/"src"))
sys.path.insert(0,str(HERE.parent/"stage2c"/"src"))
from exact_core import ExactCMModel
from molico_grid import Calibration
from fixed_contracts import (improve_nash_contracts,evaluate_contracts,
    iterate_policy_evaluation,fixed_contract_bellman)
model=ExactCMModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.,y_choices=4,d_choices=5))
f=np.zeros(model.n);f[12]=1.
rows=[]
for price in (2.5,3.):
    y,d=improve_nash_contracts(model,np.zeros(model.n),price)
    fixed=evaluate_contracts(model,f,price,y,d,tol=1e-8,maxiter=1500)
    policy=iterate_policy_evaluation(model,f,price,max_policy_iter=30)
    v=fixed["value"]
    nv=fixed_contract_bellman(v,model.k,model.m,f,price,y,d,
        model.p.beta,model.p.b,model.p.eta,model.p.alpha,model.p.A,
        model.p.delta,model.p.Ntypes)
    row=dict(price=price,fixed_contract_Bellman_converged=fixed["converged"],
        fixed_contract_evaluations=fixed["iterations"],
        fixed_contract_Bellman_sup=float(np.max(abs(nv-v))),
        endogenous_Nash_policy_status=policy["status"],
        Nash_policy_improvements=len(policy["history"]),
        final_contract_array_changes=policy["history"][-1]["contract_array_changes"],
        last_policy_changes=[r["contract_array_changes"] for r in policy["history"][-6:]],
        max_inner_Bellman_sup=max(r["value_residual"] for r in policy["history"]))
    rows.append(row)
    print(json.dumps(row,indent=2),flush=True)
assert all(z["fixed_contract_Bellman_sup"]<1e-7 for z in rows)
assert not any(z["endogenous_Nash_policy_status"]==
    "FINITE_DISCRETE_NASH_FIXED_PRICE_PRIVATE_EQUILIBRIUM" for z in rows),\
    "Nash fixed point found; needs fresh independent certification"
out=HERE/"results";out.mkdir(exist_ok=True)
(out/"fixed_price_diagnostic.json").write_text(json.dumps(dict(
    status="FIXED_CONTRACT_VALUE_CONVERGED_ENDOGENOUS_NASH_DID_NOT_STABILIZE",
    baseline="5x5 finite-contract Stage2D private problem, NOT monetary GE",
    partner_distribution="all mass at (k=1.5,m=1), not a stationary GE",
    python=platform.python_version(),runs=rows,equilibrium_certified=False),
    indent=2)+"\n")
with (out/"fixed_price_diagnostic.csv").open("w",newline="") as file:
    writer=csv.DictWriter(file,fieldnames=list(rows[0]))
    writer.writeheader();writer.writerows(rows)
