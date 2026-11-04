"""Correct an incorrectly binding payment constraint in continuous Nash.

A payment at its upper bound can be optimal only if the derivative with
respect to the real payment is nonnegative. If negative, scan/profile
interior payment and solve interior FOCs. This is an improved candidate
oracle, not a global Nash certificate; independent convex checks required.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize_scalar, root
from private_nash_bellman import (nash_polish,nash_grad,nash_score,
                                   nash_candidate,_frozen_operator)


def active_polish(i,j,q,d,model,v,price):
    p=model.p
    if q<=0:return 0.,0.,0.,False
    q,d,kkt=nash_polish(i,j,q,d,model,v,price)
    def grad(qq,dd):
        return nash_grad(qq,dd,i,j,price,model.k,model.m,v,model.edges,
                         p.beta,p.b,p.eta,p.alpha,p.A,p.theta,p.delta)
    gx=grad(q,d)[1]
    if not (d>=model.m[i]*(1-1e-7) and np.isfinite(gx) and gx< -1e-6):
        return q,d,kkt,False
    cap=p.A*model.k[j]**p.alpha
    old=nash_score(q,d,i,j,model,v,price)
    best=(old,q,d)
    for factor in (.97,1.,1.03):
        qq=min(cap*(1.-1e-10),q*factor)
        xmax=min(qq,model.m[i]/price)
        if xmax<=0:continue
        grid=np.linspace(max(1e-12,xmax*1e-8),xmax,49)
        vals=[nash_score(qq,xx*price,i,j,model,v,price) for xx in grid]
        for ix in range(1,len(grid)-1):
            if not (vals[ix]>vals[ix-1] and vals[ix]>=vals[ix+1]):
                continue
            def loss(x):
                val=nash_score(qq,x*price,i,j,model,v,price)
                return -val if np.isfinite(val) else 1e100
            res=minimize_scalar(loss,bounds=(grid[ix-1],grid[ix+1]),
                   method="bounded",options={"xatol":1e-13})
            trial=(float(-res.fun),float(qq),float(res.x*price))
            if trial[0]>best[0]:best=trial
    _,qq,dd=best
    if dd<model.m[i]-1e-9:
        def F(z):
            if not (0<z[0]<cap and 0<z[1]<model.m[i]):
                return [1e5,1e5]
            return grad(z[0],z[1])
        for init in ((qq,dd),(qq*.995,dd*.99)):
            rr=root(F,init,method="hybr",options={"xtol":1e-11,"maxfev":120})
            if 0<rr.x[0]<cap and 0<rr.x[1]<model.m[i]:
                sc=nash_score(*rr.x,i,j,model,v,price)
                if sc>best[0]:
                    best=(sc,float(rr.x[0]),float(rr.x[1]))
    newq,newd=best[1],best[2]
    gy,gx=grad(newq,newd)
    updated=max(abs(gy),abs(gx)) if newd<model.m[i]-1e-7 else max(abs(gy),max(0.,-gx))
    return newq,newd,float(updated),best[0]>old+1e-11


def active_operator(V,f,price,model,nq=9,nx=7):
    p=model.p
    offset=float(max(V))
    v=np.asarray(V)-offset
    y=np.zeros((model.n,model.n))
    d=np.zeros_like(y)
    released=[]
    max_kkt=0.
    for i in range(model.n):
        for j in range(model.n):
            if f[i]<=1e-15 and f[j]<=1e-15:continue
            q,pay,_=nash_candidate(i,j,price,model.k,model.m,v,model.edges,
                          p.beta,p.b,p.eta,p.alpha,p.A,p.theta,p.delta,nq,nx)
            if q<=0:continue
            q,pay,kkt,change=active_polish(i,j,q,pay,model,v,price)
            y[i,j],d[i,j]=q,pay
            max_kkt=max(max_kkt,kkt)
            if change:released.append([i,j])
    t=_frozen_operator(v,f,price,model.k,model.m,model.edges,
                      p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,y,d)
    return t+p.beta*offset,y,d,max_kkt,released
