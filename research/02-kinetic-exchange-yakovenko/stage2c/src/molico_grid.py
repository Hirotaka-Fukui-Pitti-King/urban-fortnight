"""Provisional finite-grid model built from indexed Molico--Zhang manuscript text.

Source verification status for Molico--Zhang: web-indexed text only; PDF pages and equations have NOT been visually verified.
Original equation labels and typography have NOT been checked against PDF pages.

This is NOT a numerical replication of the authors' 100x100 spline/10,000
sample nonlinear stationary equilibrium algorithm. A type-i agent stores its
own capital/consumption good and produces type i+1 goods in DM only. CM has
NO production. Nash contracts transfer fiat money for newly produced goods.
"""
from dataclasses import dataclass
import numpy as np
from numba import njit

@dataclass(frozen=True)
class Calibration:
    beta:float=.96
    alpha:float=.36
    delta:float=.07
    eta:float=5.
    b:float=.2
    theta:float=.5
    Ntypes:int=3
    A:float=1.
    kmax:float=3.
    nk:int=11
    mmax:float=3.
    nm:int=11
    y_choices:int=6
    d_choices:int=9
    maxit:int=300
    tol_v:float=1e-7
    tol_f:float=1e-8

@njit(cache=True)
def u(c,b,eta):
    return ((c+b)**(1-eta)-b**(1-eta))/(1-eta)

@njit(cache=True)
def g(y,k,alpha,A):
    if y<1e-14:return 0.
    if k<=0:return 1e100
    ell=(y/(A*k**alpha))**(1/(1-alpha))
    if ell>=1:return 1e100
    return ell/(1-ell)

@njit(cache=True)
def W_eval(wealth,ww,val):
    if wealth<0:return -1e15
    if wealth<=ww[0]:return val[0]
    if wealth>=ww[-1]:return val[-1]
    i=np.searchsorted(ww,wealth)-1
    t=(wealth-ww[i])/(ww[i+1]-ww[i])
    return val[i]*(1-t)+val[i+1]*t

@njit(cache=True)
def calc_W(V,k,m,p,beta,b,eta,wealth_grid):
    n=len(k);nw=len(wealth_grid)
    costs=k+m/p
    W=np.full(nw,-1e15)
    best=np.zeros(nw,dtype=np.int64)
    for iw in range(nw):
        wealth=wealth_grid[iw]
        for j in range(n):
            c=wealth-costs[j]
            if c>=-1e-14:
                v=u(max(c,0.),b,eta)+beta*V[j]
                if v>W[iw]:
                    W[iw]=v;best[iw]=j
    return W,best

@njit(cache=True)
def bargaining(k,m,p,W,wealth_grid,alpha,A,theta,ny,nd,delta):
    """Nash optimality is only over the explicit finite contract menu."""
    n=len(k)
    yy=np.zeros((n,n));dd=np.zeros((n,n))
    gb=np.zeros((n,n));gs=np.zeros((n,n))
    labor=np.zeros((n,n))
    post=(1-delta)*k+m/p
    W0=np.array([W_eval(post[j],wealth_grid,W) for j in range(n)])
    for buyer in range(n):
        for seller in range(n):
            if m[buyer]<1e-12 or k[seller]<1e-12:continue
            capacity=A*k[seller]**alpha
            best=-1e300
            for idd in range(1,nd+1):
                d=m[buyer]*idd/nd
                # Finite-grid upper money bound: limitation, not economic law.
                if m[seller]+d>m.max()+1e-12:continue
                for iy in range(1,ny+1):
                    y=capacity*.90*iy/(ny+1)
                    effort_cost=g(y,k[seller],alpha,A)
                    bg=W_eval(post[buyer]+y-d/p,wealth_grid,W)-W0[buyer]
                    sg=W_eval(post[seller]+d/p,wealth_grid,W)-W0[seller]-effort_cost
                    if bg<=1e-12 or sg<=1e-12:continue
                    objective=theta*np.log(bg)+(1-theta)*np.log(sg)
                    if objective>best:
                        best=objective
                        yy[buyer,seller]=y;dd[buyer,seller]=d
                        gb[buyer,seller]=bg;gs[buyer,seller]=sg
                        labor[buyer,seller]=(y/(A*k[seller]**alpha))**(1/(1-alpha))
    return yy,dd,gb,gs,labor

@njit(cache=True)
def mass_split(kg,mg,money,cap,weight,mass):
    if money<mg[0]-1e-12 or money>mg[-1]+1e-12 or cap<kg[0]-1e-12 or cap>kg[-1]+1e-12:
        return 1
    cap=min(kg[-1],max(kg[0],cap))
    money=min(mg[-1],max(mg[0],money))
    ia=np.searchsorted(kg,cap)-1
    im=np.searchsorted(mg,money)-1
    ia=max(0,min(len(kg)-2,ia));im=max(0,min(len(mg)-2,im))
    ka=(cap-kg[ia])/(kg[ia+1]-kg[ia])
    ma=(money-mg[im])/(mg[im+1]-mg[im])
    nm=len(mg)
    mass[ia*nm+im]+=weight*(1-ka)*(1-ma)
    mass[(ia+1)*nm+im]+=weight*ka*(1-ma)
    mass[ia*nm+im+1]+=weight*(1-ka)*ma
    mass[(ia+1)*nm+im+1]+=weight*ka*ma
    return 0

@njit(cache=True)
def forward_dm(f,k,m,kg,mg,y,d,delta,ntypes):
    n=len(f)
    cm=np.zeros(len(kg)*len(mg))
    invalid=0;trades=0.;production=0.
    for i in range(n):
        invalid+=mass_split(kg,mg,m[i],(1-delta)*k[i],f[i],cm)
    for i in range(n):
        for j in range(n):
            if d[i,j]<1e-14:continue
            rate=f[i]*f[j]/ntypes
            if rate==0:continue
            invalid+=mass_split(kg,mg,m[i],(1-delta)*k[i],-rate,cm)
            invalid+=mass_split(kg,mg,m[j],(1-delta)*k[j],-rate,cm)
            invalid+=mass_split(kg,mg,m[i]-d[i,j],(1-delta)*k[i]+y[i,j],rate,cm)
            invalid+=mass_split(kg,mg,m[j]+d[i,j],(1-delta)*k[j],rate,cm)
            trades+=rate;production+=rate*y[i,j]
    return cm,invalid,trades,production

@njit(cache=True)
def central_forward(cm,post_k,post_m,choice_k,choice_m,kg,mg,p,V,beta,b,eta):
    fnext=np.zeros(len(V))
    C=0.;boundary=0.;invalid=0.
    for i in range(len(cm)):
        if cm[i]<=1e-20:continue
        wealth=post_k[i]+post_m[i]/p
        best=-1e100;bj=-1;cons=0.
        for j in range(len(V)):
            c=wealth-choice_k[j]-choice_m[j]/p
            if c>=-1e-14:
                v=u(max(c,0.),b,eta)+beta*V[j]
                if v>best:
                    best=v;bj=j;cons=max(c,0.)
        if bj<0:
            invalid+=cm[i];continue
        fnext[bj]+=cm[i];C+=cm[i]*cons
        if choice_k[bj]>=kg[-1]-1e-10:boundary+=cm[i]
    return fnext,C,boundary,invalid

class MonetarySearch:
    def __init__(self,par=Calibration()):
        self.p=par
        self.kg=np.linspace(0,par.kmax,par.nk)
        self.mg=np.linspace(0,par.mmax,par.nm)
        self.k=np.repeat(self.kg,par.nm)
        self.m=np.tile(self.mg,par.nk)
        self.n=len(self.k)

    def step(self,V,f,price):
        p=self.p
        ww=np.linspace(0,p.kmax+p.mmax/price+p.A*p.kmax**p.alpha+1,501)
        W,_=calc_W(V,self.k,self.m,price,p.beta,p.b,p.eta,ww)
        y,d,gb,gs,labor=bargaining(self.k,self.m,price,W,ww,p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
        base=(1-p.delta)*self.k+self.m/price
        Vnext=np.array([np.interp(base[i],ww,W)+(gb[i]@f+gs[:,i]@f)/p.Ntypes for i in range(self.n)])
        # Enlarged post-DM grid: no artificial clipping of buyer's newly produced good.
        kmax_post=(1-p.delta)*p.kmax+.90*p.A*p.kmax**p.alpha
        kgpost=np.linspace(0,kmax_post,max(2*p.nk,p.nk+8))
        cm,invalid,trades,output=forward_dm(f,self.k,self.m,kgpost,self.mg,y,d,p.delta,p.Ntypes)
        kp=np.repeat(kgpost,p.nm);mp=np.tile(self.mg,len(kgpost))
        fn,C,boundary,invalid_CM=central_forward(cm,kp,mp,self.k,self.m,self.kg,self.mg,price,V,p.beta,p.b,p.eta)
        return Vnext,fn,{"invalid":invalid,"invalid_CM":invalid_CM,"boundary":boundary,
            "trades":trades,"production":output,"consumption":C,"preCM":cm,
            "y":y,"d":d,"buyer_gains":gb,"seller_gains":gs,"labor":labor}

    def solve(self,price=1.,maxit=None,tolerance=None):
        p=self.p
        V=np.zeros(self.n);f=np.ones(self.n)/self.n
        maxit=maxit or p.maxit
        tol=tolerance or p.tol_v
        for it in range(maxit):
            VV,ff,info=self.step(V,f,price)
            value_res=np.max(abs(VV-V))
            dist_res=np.max(abs(ff-f))
            V=.45*VV+.55*V
            f=.25*ff+.75*f
            if value_res<tol and dist_res<p.tol_f:break
        VV,ff,info=self.step(V,f,price)
        value_res=float(np.max(abs(VV-V)));dist_res=float(np.max(abs(ff-f)))
        return {
            "iterations":it+1,"value_residual":value_res,
            "distribution_residual":dist_res,
            "converged":bool(value_res<tol and dist_res<p.tol_f),
            "invalid_transition_count":int(info["invalid"]),
            "unfeasible_choice_mass":float(info["invalid_CM"]),
            "mass":float(f.sum()),"capital":float(f@self.k),"money":float(f@self.m),
            "money_supply_residual":float(f@self.m-1.),
            "capital_grid_top_mass":float(f[self.k==p.kmax].sum()),
            "money_grid_top_mass":float(f[self.m==p.mmax].sum()),
            "consumption":float(info["consumption"]),
            "DM_production":float(info["production"]),
            "trades":float(info["trades"]),
            "price_capital_per_money":price,"real_money_value":1/price,
            "issuer_transfer":0.
        },{"f":f,"V":V,"trade":info}
