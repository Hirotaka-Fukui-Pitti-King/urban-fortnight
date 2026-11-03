"""Exact-on-grid centralized-market value and consistent policy for Molico--Zhang.

Stage 2-C interpolated maxima on a fixed wealth grid, yielding severe errors at
kinks. Here the *same* direct discrete maximization is used by value, Nash
bargaining, and the portfolio distribution transition. This is a pilot, NOT
continuous portfolio choice nor a positive stationary monetary GE.
"""
import numpy as np
from numba import njit
from molico_grid import MonetarySearch,Calibration,forward_dm,central_forward,g,u

@njit(cache=True)
def CM_exact(wealth,cost,V,beta,b,eta):
    if wealth<0:return -1e15,-1
    best=-1e100;bestj=-1
    for j in range(len(cost)):
        c=wealth-cost[j]
        if c < -1e-12:continue
        v=u(max(c,0.),b,eta)+beta*V[j]
        if v>best:
            best=v;bestj=j
    return best,bestj

@njit(cache=True)
def bargaining_exact(k,m,p,V,beta,b,eta,alpha,A,theta,ny,nd,delta):
    n=len(k);costs=k+m/p
    yy=np.zeros((n,n));dd=np.zeros((n,n))
    gain_b=np.zeros((n,n));gain_s=np.zeros((n,n));labor=np.zeros((n,n))
    W0=np.empty(n)
    for j in range(n):
        W0[j],_=CM_exact((1-delta)*k[j]+m[j]/p,costs,V,beta,b,eta)
    for buyer in range(n):
        for seller in range(n):
            if m[buyer]<1e-12 or k[seller]<1e-12:continue
            capacity=A*k[seller]**alpha;opt=-1e300
            for idd in range(1,nd+1):
                d=m[buyer]*idd/nd
                for iy in range(1,ny+1):
                    y=capacity*.90*iy/(ny+1)
                    cost_l=g(y,k[seller],alpha,A)
                    buyerW,_=CM_exact((1-delta)*k[buyer]+(m[buyer]-d)/p+y,
                                      costs,V,beta,b,eta)
                    sellerW,_=CM_exact((1-delta)*k[seller]+(m[seller]+d)/p,
                                       costs,V,beta,b,eta)
                    BG=buyerW-W0[buyer];SG=sellerW-W0[seller]-cost_l
                    if BG<=1e-12 or SG<=1e-12:continue
                    obj=theta*np.log(BG)+(1-theta)*np.log(SG)
                    if obj>opt:
                        opt=obj;yy[buyer,seller]=y;dd[buyer,seller]=d
                        gain_b[buyer,seller]=BG;gain_s[buyer,seller]=SG
                        labor[buyer,seller]=(y/(A*k[seller]**alpha))**(1/(1-alpha))
    return yy,dd,gain_b,gain_s,labor,W0

class ExactCMModel(MonetarySearch):
    def __init__(self,par=Calibration()):
        super().__init__(par)
        self.dm_kgrid=np.linspace(0,(1-par.delta)*par.kmax+.90*par.A*par.kmax**par.alpha,
                                  max(2*par.nk,par.nk+8))
        # The seller may RECEIVE money above the next-period CM saving grid.
        # That is an intermediate DM state, not an economically forbidden trade.
        self.dm_mgrid=np.linspace(0,2*par.mmax,max(2*par.nm,par.nm+8))
        self.kpost=np.repeat(self.dm_kgrid,len(self.dm_mgrid))
        self.mpost=np.tile(self.dm_mgrid,len(self.dm_kgrid))
    def step(self,V,f,price):
        p=self.p
        y,d,gb,gs,labor,W0=bargaining_exact(self.k,self.m,price,V,p.beta,p.b,p.eta,
            p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
        VV=W0+(gb@f+gs.T@f)/p.Ntypes
        cm,invalid,trades,output=forward_dm(f,self.k,self.m,self.dm_kgrid,
            self.dm_mgrid,y,d,p.delta,p.Ntypes)
        ff,C,boundary,invalidCM=central_forward(cm,self.kpost,self.mpost,
            self.k,self.m,self.kg,self.mg,price,V,p.beta,p.b,p.eta)
        return VV,ff,dict(invalid=invalid,invalid_CM=invalidCM,boundary=boundary,
            trades=trades,production=output,consumption=C,preCM=cm,y=y,d=d,
            buyer_gains=gb,seller_gains=gs,labor=labor)
