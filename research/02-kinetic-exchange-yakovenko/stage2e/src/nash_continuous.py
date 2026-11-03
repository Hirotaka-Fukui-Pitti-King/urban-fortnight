"""Numerical continuous Nash contract at given CM value and quoted price.

Multistart SLSQP, budget/participation tests and explicit local-optimality
diagnostics. NOT a proof of global Nash optimality or a stationary GE policy.
"""
import numpy as np
from scipy.optimize import minimize
from continuous_core import cm_opt
from molico_grid import g

def continuous_nash(model,V,price,buyer,seller,starts=None,maxiter=200):
    p=model.p;kb,mb=model.k[buyer],model.m[buyer]
    ks,ms=model.k[seller],model.m[seller]
    if mb<=1e-12 or ks<=1e-12:
        return dict(y=0.,d=0.,buyer_gain=0.,seller_gain=0.,trade=False)
    cap=.985*p.A*ks**p.alpha
    be=(1-p.delta)*kb+mb/price
    se=(1-p.delta)*ks+ms/price
    CM=lambda w:cm_opt(w,price,model.k,model.m,V,model.edges,p.beta,p.b,p.eta)[0]
    baseB=CM(be);baseS=CM(se)
    def gains(x):
        y,d=x
        if y<0 or y>cap or d<0 or d>mb:
            return -np.inf,-np.inf
        bg=CM(be+y-d/price)-baseB
        sg=CM(se+d/price)-baseS-g(y,ks,p.alpha,p.A)
        return bg,sg
    def loss(x):
        bg,sg=gains(x)
        if not np.isfinite(bg+sg) or min(bg,sg)<=1e-12:
            return 1e3+1e2*(max(0.,-bg) if np.isfinite(bg) else 1) + 1e2*(max(0.,-sg) if np.isfinite(sg) else 1)
        return -p.theta*np.log(bg)-(1-p.theta)*np.log(sg)
    if starts is None:
        candidates=[]
        for y in cap*np.linspace(.05,.95,9):
            for d in mb*np.linspace(.05,.95,9):
                bg,sg=gains((y,d))
                if bg>0 and sg>0:
                    candidates.append((loss((y,d)),y,d))
        candidates.sort()
        starts=[(z[1],z[2]) for z in candidates[:6]]
    if not starts:
        return dict(y=0.,d=0.,buyer_gain=0.,seller_gain=0.,
                    trade=False,feasible_start_count=0)
    best=(1e100,None)
    for initial in starts:
        res=minimize(loss,np.asarray(initial,dtype=float),method='SLSQP',
                     bounds=((0,cap),(0,mb)),
                     options={'ftol':1e-11,'maxiter':maxiter})
        val=loss(res.x)
        if val<best[0]:best=(val,res)
    val,res=best;bg,sg=gains(res.x)
    if min(bg,sg)<=0 or val>500:
        return dict(y=0.,d=0.,buyer_gain=0.,seller_gain=0.,
                    trade=False,status='NO_POSITIVE_NASH_MAX_FOUND')
    coarse=min(loss(z) for z in starts)
    return dict(y=float(res.x[0]),d=float(res.x[1]),
        buyer_gain=float(bg),seller_gain=float(sg),trade=True,
        nash_log=float(-val),coarse_best_nash_log=float(-coarse),
        improvement_over_coarse=float(coarse-val),nfev=int(res.nfev),
        seller_labor=float((res.x[0]/(p.A*ks**p.alpha))**(1/(1-p.alpha))),
        payment_feasibility=float(mb-res.x[1]),
        participant_slack=float(min(bg,sg)),success=bool(res.success),
        max_abs_steps=float(np.max(abs(res.jac))) if res.jac is not None else None)
