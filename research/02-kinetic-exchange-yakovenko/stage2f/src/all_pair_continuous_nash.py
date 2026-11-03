"""Continuous Nash candidates for every pairing relevant to a given DM measure.

This uses existing Stage 2-E multistart SLSQP and its piecewise-affine CM
value function. A global Nash optimum is NOT certified; feasibility and a
coarse-grid lower bound are checked independently. The output is used by the
actual DM distribution law and the Bellman update, not merely for one pair.
"""
import numpy as np
from continuous_core import cm_opt
from nash_continuous import continuous_nash
from molico_grid import forward_dm

def one_step_all_relevant_continuous_nash(model,V,f,price,maxiter=120,
                                          positive_mass=1e-13):
    if abs(f.sum()-1)>1e-10 or f.min()<-1e-14:raise ValueError("invalid population")
    n=model.n;p=model.p
    supported=np.where(f>positive_mass)[0]
    if len(supported)==0:raise ValueError("no supported partner states")
    pairs=set()
    for i in range(n):
        for j in supported:
            pairs.add((i,int(j)))
            pairs.add((int(j),i))
    y=np.zeros((n,n));d=np.zeros((n,n))
    bg=np.zeros((n,n));sg=np.zeros((n,n))
    W0=np.empty(n)
    for i in range(n):
        wealth=(1-p.delta)*model.k[i]+model.m[i]/price
        W0[i]=cm_opt(wealth,price,model.k,model.m,V,model.edges,
                     p.beta,p.b,p.eta)[0]
    active=0;failed_local=0;min_surplus=float("inf");min_improvement=0.
    for buyer,seller in sorted(pairs):
        result=continuous_nash(model,V,price,buyer,seller,maxiter=maxiter)
        if not result["trade"]:continue
        q=float(result["y"]);pay=float(result["d"])
        if not (q>0 and pay>0 and pay<=model.m[buyer]+1e-10):
            raise AssertionError("payment feasibility")
        cap=p.A*model.k[seller]**p.alpha
        if q>=cap:raise AssertionError("seller unit labor feasibility")
        buyer_gain=float(result["buyer_gain"])
        seller_gain=float(result["seller_gain"])
        if buyer_gain<=0 or seller_gain<=0:
            raise AssertionError("voluntary participation")
        y[buyer,seller]=q;d[buyer,seller]=pay
        bg[buyer,seller]=buyer_gain;sg[buyer,seller]=seller_gain
        min_surplus=min(min_surplus,buyer_gain,seller_gain)
        min_improvement=min(min_improvement,float(result["improvement_over_coarse"]))
        if not result.get("success",False):failed_local+=1
        active+=1
    newV=W0+(bg@f+sg.T@f)/p.Ntypes
    entrants,invalid,trades,output=forward_dm(f,model.k,model.m,
                   model.postkg,model.postmg,y,d,p.delta,p.Ntypes)
    if invalid or abs(entrants.sum()-1)>1e-9:
        raise AssertionError("invalid DM transition or probability mass")
    cash_before=float(f@model.m);cash_after=float(entrants@model.postm)
    capital_before=float(f@model.k);capital_after=float(entrants@model.postk)
    if abs(cash_after-cash_before)>1e-9:
        raise AssertionError("DM money creation/destruction")
    if abs(capital_after-(1-p.delta)*capital_before-output)>1e-9:
        raise AssertionError("DM capital-production accounting")
    return newV,entrants,dict(
       relevant_pairs=len(pairs),population_supported_states=int(len(supported)),
       positive_continuous_contract_candidates=active,
       local_solver_failures=failed_local,
       smallest_participation_surplus=(float(min_surplus) if active else None),
       min_logNash_improvement_vs_coarse=float(min_improvement),
       trade_rate=float(trades),DM_production=float(output),
       money_before=cash_before,money_after=cash_after,
       capital_before=capital_before,capital_after=capital_after,
       Bellman_update_sup=float(np.max(abs(newV-V))),
       continuous_contracts_applied_to_actual_DM_operator=True,
       complete_global_Nash_certification=False,
       stationary_GE=False)
