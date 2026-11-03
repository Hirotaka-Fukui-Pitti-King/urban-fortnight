"""Verify strictly separable product of Aiyagari GE and monetary search.

This does not solve a nonseparable capital-money economy. Each household has
a separate home-service effort endowment and nonconvertible monetary tokens.
"""
from pathlib import Path
import sys
import numpy as np
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/"00-heterogeneous-agent-ge"/"src"))
from aiyagari import Calibration,equilibrium,histogram_step
from monetary_matching import Params,solve_candidate,diagnostics,payoff

def value_under_fixed_savings(eq,cal,tol=1e-11,maxit=4000):
    a,z,P,c,g=eq["a"],eq["z"],eq["P"],eq["c"],eq["g"]
    u=np.log(c) if cal.sigma==1 else c**(1-cal.sigma)/(1-cal.sigma)
    V=np.zeros_like(c)
    for i in range(maxit):
        nextV=np.empty_like(V)
        for k in range(len(z)):
            expected=np.zeros(len(a))
            for k2 in range(len(z)):
                expected+=P[k,k2]*np.interp(g[k],a,V[k2])
            nextV[k]=u[k]+cal.beta*expected
        if np.max(abs(nextV-V))<tol:
            return nextV,i+1
        V=nextV
    raise RuntimeError("Aiyagari policy value evaluation failed")

def product_checks(cal=Calibration(na=200,amax=600),prm=Params()):
    if abs(cal.beta-prm.beta)>1e-13:
        raise ValueError("Product economy needs a common discount factor")
    A=equilibrium(cal)
    S=solve_candidate(prm)
    d=diagnostics(S,prm)
    if d["participation_failures"]:
        raise RuntimeError("Trade acceptance violates individual optimality")
    VA,nit=value_under_fixed_savings(A,cal)
    f,mu=S["f"],A["mu"]
    M=np.eye(len(f))+S["L"]
    munext,status=histogram_step(mu,A["a"],A["g"],A["P"])
    if status:raise RuntimeError("Policy escapes capital grid")
    joint=mu[:,:,None]*f[None,None,:]
    jointnext=munext[:,:,None]*(f@M)[None,None,:]
    a,z,P,g,c=A["a"],A["z"],A["P"],A["g"],A["c"]
    ua=np.log(c) if cal.sigma==1 else c**(1-cal.sigma)/(1-cal.sigma)
    EVA=np.zeros_like(VA)
    for k in range(len(z)):
        for k2 in range(len(z)):
            EVA[k]+=P[k,k2]*np.interp(g[k],a,VA[k2])
    service_payoff=payoff(f,S["trade"],prm)
    jointBellman=(VA[:,:,None]+S["V"][None,None,:]-ua[:,:,None]
        -service_payoff[None,None,:]
        -cal.beta*(EVA[:,:,None]+(M@S["V"])[None,None,:]))
    Y=A["summary"]["Y"]
    K=A["summary"]["K_demand"]
    C=A["summary"]["C"]
    return {"capital_market_rel_error":A["summary"]["ge_relative_capital_error"],
            "goods_market_error":Y-C-cal.delta*K,
            "stationary_product_joint_sup_error":float(np.max(abs(jointnext-joint))),
            "stationary_capital_sup_error":float(np.max(abs(munext-mu))),
            "joint_separable_policy_bellman_sup_error":float(np.max(abs(jointBellman))),
            "service_output":d["trade_rate"],
            "service_consumption":d["trade_rate"],
            "token_total_supply":prm.average_tokens,
            "token_market_error":d["money_conservation_error"],
            "service_market_error":d["service_market_error"],
            "optimal_trade_participation_failures":d["participation_failures"],
            "capital_value_policy_iterations":nit,
            "caveat":"Segmented additive economy; capital and tokens nonconvertible, independent service effort."}
