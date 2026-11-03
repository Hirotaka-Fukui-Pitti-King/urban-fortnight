"""Separate convergent fixed-contract household value evaluation from Nash improvement.

With fixed partner distribution and fixed contract policies the value operator
is a beta-contraction. Endogenous discrete Nash reoptimization can cycle.
This baseline intentionally uses Stage 2-D's original discrete contract menu,
not continuous all-pairs Nash bargaining or stationary general equilibrium.
"""
import numpy as np
from numba import njit
from exact_core import CM_exact,bargaining_exact
from molico_grid import g

@njit(cache=True)
def fixed_contract_bellman(V,k,m,f,price,y,d,beta,b,eta,alpha,A,delta,ntypes):
    n=len(k);costs=k+m/price
    W0=np.empty(n)
    for i in range(n):
        W0[i],_=CM_exact((1-delta)*k[i]+m[i]/price,costs,V,beta,b,eta)
    nextV=(ntypes-2)/ntypes*W0.copy()
    for i in range(n):
        subtotal=0.
        for j in range(n):
            if f[j]<=0:continue
            buyer,_=CM_exact((1-delta)*k[i]+(m[i]-d[i,j])/price+y[i,j],
                             costs,V,beta,b,eta)
            seller,_=CM_exact((1-delta)*k[i]+(m[i]+d[j,i])/price,
                              costs,V,beta,b,eta)
            subtotal+=f[j]*(buyer+seller-g(y[j,i],k[i],alpha,A))
        nextV[i]+=subtotal/ntypes
    return nextV

def evaluate_contracts(model,f,price,y,d,V0=None,tol=1e-8,maxiter=1500):
    if abs(f.sum()-1)>1e-9 or f.min()<0:raise ValueError("bad partner distribution")
    V=np.zeros(model.n) if V0 is None else np.array(V0,dtype=float).copy()
    p=model.p
    for iteration in range(maxiter):
        nxt=fixed_contract_bellman(V,model.k,model.m,f,price,y,d,p.beta,
                    p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes)
        error=float(np.max(abs(nxt-V)));V=nxt
        if error<tol:break
    return dict(value=V,iterations=iteration+1,residual=error,converged=error<tol)

def improve_nash_contracts(model,V,price):
    p=model.p
    y,d,_,_,_,_=bargaining_exact(model.k,model.m,price,V,p.beta,p.b,p.eta,
                p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
    return y,d

def iterate_policy_evaluation(model,f,price,max_policy_iter=30):
    """Detect rather than conceal Nash best-response nonconvergence."""
    V=np.zeros(model.n);y,d=improve_nash_contracts(model,V,price);history=[]
    for t in range(max_policy_iter):
        ev=evaluate_contracts(model,f,price,y,d,V0=V)
        V=ev["value"]
        yy,dd=improve_nash_contracts(model,V,price)
        changed=int(np.count_nonzero(abs(dd-d)>1e-10)+np.count_nonzero(abs(yy-y)>1e-10))
        history.append(dict(iteration=t+1,value_residual=ev["residual"],
            inner_value_iterations=ev["iterations"],contract_array_changes=changed))
        if changed==0 and ev["converged"]:
            r=fixed_contract_bellman(V,model.k,model.m,f,price,y,d,
                model.p.beta,model.p.b,model.p.eta,model.p.alpha,model.p.A,
                model.p.delta,model.p.Ntypes)
            return dict(status="FINITE_DISCRETE_NASH_FIXED_PRICE_PRIVATE_EQUILIBRIUM",
                value=V,y=y,d=d,history=history,bellman_sup=float(max(abs(r-V))))
        y,d=yy,dd
    return dict(status="ENDOGENOUS_NASH_POLICY_DID_NOT_STABILIZE",
                value=V,y=y,d=d,history=history)
