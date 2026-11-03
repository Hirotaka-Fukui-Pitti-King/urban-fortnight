"""Continuous (k',m') CM optimizer for a triangular piecewise-affine value.

On each affine triangle the maximum of CRRA consumption utility plus
the continuation value occurs on an edge, except when an entire iso-cost
segment is optimal, in which case it is attained on an edge too.
Exact here means exact for this interpolation, NOT the source's spline GE.
"""
import numpy as np
from numba import njit
from molico_grid import Calibration,u,g,forward_dm,mass_split

def triangulation_edges(nk,nm):
    edges=[]
    for a in range(nk):
        for mm in range(nm):
            j=a*nm+mm
            if a+1<nk:edges.append((j,(a+1)*nm+mm))
            if mm+1<nm:edges.append((j,j+1))
            if a+1<nk and mm+1<nm:edges.append((j,(a+1)*nm+mm+1))
    return np.array(edges,dtype=np.int64)

@njit(cache=True)
def cm_opt(wealth,price,k,m,V,edges,beta,b,eta):
    best=-1e200;resk=0.;resm=0.;resc=0.
    if wealth<0:return best,resk,resm,resc
    for e in range(len(edges)):
        i,j=edges[e,0],edges[e,1]
        wi=k[i]+m[i]/price
        dw=k[j]+m[j]/price-wi
        dv=V[j]-V[i]
        lo=0.;hi=1.
        if abs(dw)<1e-14:
            if wi>wealth+1e-12:continue
        elif dw>0:hi=min(1.,(wealth-wi)/dw)
        else:lo=max(0.,(wealth-wi)/dw)
        if lo>hi+1e-12 or hi<0 or lo>1:continue
        lo=max(0.,min(1.,lo));hi=max(0.,min(1.,hi))
        for z in range(3):
            if z==0:t=lo
            elif z==1:t=hi
            else:
                if abs(dw)<1e-14 or dv*dw<=0:continue
                cstar=(dw/(beta*dv))**(1/eta)-b
                t=(wealth-wi-cstar)/dw
                if t<lo or t>hi:continue
            c=wealth-wi-t*dw
            if c < -1e-12:continue
            c=max(0.,c)
            val=u(c,b,eta)+beta*(V[i]+t*dv)
            if val>best:
                best=val
                resk=k[i]+t*(k[j]-k[i])
                resm=m[i]+t*(m[j]-m[i])
                resc=c
    return best,resk,resm,resc

@njit(cache=True)
def cm_extreme_portfolios(wealth,price,k,m,V,edges,beta,b,eta,opt_tol):
    best,km,mm,cc=cm_opt(wealth,price,k,m,V,edges,beta,b,eta)
    minm=mm;maxm=mm;loK=km;loC=cc;hiK=km;hiC=cc
    for e in range(len(edges)):
        i,j=edges[e,0],edges[e,1]
        wi=k[i]+m[i]/price
        dw=k[j]+m[j]/price-wi
        dv=V[j]-V[i]
        lo=0.;hi=1.
        if abs(dw)<1e-14:
            if wi>wealth+1e-12:continue
        elif dw>0:hi=min(1.,(wealth-wi)/dw)
        else:lo=max(0.,(wealth-wi)/dw)
        if lo>hi+1e-12 or hi<0 or lo>1:continue
        lo=max(0.,min(1.,lo));hi=max(0.,min(1.,hi))
        for z in range(3):
            if z==0:t=lo
            elif z==1:t=hi
            else:
                if abs(dw)<1e-14 or dv*dw<=0:continue
                cstar=(dw/(beta*dv))**(1/eta)-b
                t=(wealth-wi-cstar)/dw
                if t<lo or t>hi:continue
            c=wealth-wi-t*dw
            if c < -1e-12:continue
            c=max(0.,c)
            val=u(c,b,eta)+beta*(V[i]+t*dv)
            if best-val<=opt_tol:
                cm=m[i]+t*(m[j]-m[i])
                ck=k[i]+t*(k[j]-k[i])
                if cm<minm:minm=cm;loK=ck;loC=c
                if cm>maxm:maxm=cm;hiK=ck;hiC=c
    return best,loK,minm,loC,hiK,maxm,hiC

@njit(cache=True)
def cm_law(cm,postk,postm,kg,mg,k,m,V,edges,price,beta,b,eta):
    ff=np.zeros(len(V));C=0.;K=0.;M=0.;bad=0.
    for i in range(len(cm)):
        prob=cm[i]
        if prob<=1e-20:continue
        w=postk[i]+postm[i]/price
        val,kp,mp,c=cm_opt(w,price,k,m,V,edges,beta,b,eta)
        if val< -1e100:bad+=prob;continue
        bad+=mass_split(kg,mg,mp,kp,prob,ff)
        C+=prob*c;K+=prob*kp;M+=prob*mp
    return ff,C,K,M,bad

@njit(cache=True)
def cm_auction_extremes(cm,postk,postm,kg,mg,k,m,V,edges,price,beta,b,eta,tol):
    low=np.zeros(len(V));high=np.zeros(len(V))
    lowC=0.;highC=0.;minM=0.;maxM=0.;minK=0.;maxK=0.;bad=0.
    for i in range(len(cm)):
        prob=cm[i]
        if prob<=1e-20:continue
        w=postk[i]+postm[i]/price
        val,lk,lm,lc,hk,hm,hc=cm_extreme_portfolios(w,price,k,m,V,edges,beta,b,eta,tol)
        if val < -1e100:bad+=prob;continue
        bad+=mass_split(kg,mg,lm,lk,prob,low)
        bad+=mass_split(kg,mg,hm,hk,prob,high)
        minM+=prob*lm;maxM+=prob*hm
        minK+=prob*lk;maxK+=prob*hk
        lowC+=prob*lc;highC+=prob*hc
    return low,high,minM,maxM,minK,maxK,lowC,highC,bad

@njit(cache=True)
def bargaining_discrete_continuousW(k,m,price,V,edges,beta,b,eta,alpha,A,theta,ny,nd,delta):
    n=len(k);y=np.zeros((n,n));d=np.zeros((n,n))
    bg=np.zeros((n,n));sg=np.zeros((n,n));labor=np.zeros((n,n));W0=np.empty(n)
    for j in range(n):
        W0[j]=cm_opt((1-delta)*k[j]+m[j]/price,price,k,m,V,edges,beta,b,eta)[0]
    for buyer in range(n):
        if m[buyer]<=1e-12:continue
        for seller in range(n):
            if k[seller]<=1e-12:continue
            cap=A*k[seller]**alpha
            best=-1e200
            for iy in range(1,ny+1):
                yy=.95*cap*iy/(ny+1)
                cost=g(yy,k[seller],alpha,A)
                if cost>1e20:continue
                for idd in range(1,nd+1):
                    pay=m[buyer]*idd/nd
                    wb=(1-delta)*k[buyer]+yy+(m[buyer]-pay)/price
                    ws=(1-delta)*k[seller]+(m[seller]+pay)/price
                    buyerV=cm_opt(wb,price,k,m,V,edges,beta,b,eta)[0]-W0[buyer]
                    sellerV=cm_opt(ws,price,k,m,V,edges,beta,b,eta)[0]-W0[seller]-cost
                    if buyerV<=1e-12 or sellerV<=1e-12:continue
                    obj=theta*np.log(buyerV)+(1-theta)*np.log(sellerV)
                    if obj>best:
                        best=obj;y[buyer,seller]=yy;d[buyer,seller]=pay
                        bg[buyer,seller]=buyerV;sg[buyer,seller]=sellerV
                        labor[buyer,seller]=(yy/(A*k[seller]**alpha))**(1/(1-alpha))
    return y,d,bg,sg,labor,W0

class ContinuousModel:
    def __init__(self,p=None):
        self.p=p or Calibration()
        self.kg=np.linspace(0,self.p.kmax,self.p.nk)
        self.mg=np.linspace(0,self.p.mmax,self.p.nm)
        self.k=np.repeat(self.kg,self.p.nm)
        self.m=np.tile(self.mg,self.p.nk)
        self.edges=triangulation_edges(self.p.nk,self.p.nm)
        self.n=len(self.k)
        self.postkg=np.linspace(0,(1-self.p.delta)*self.p.kmax+.95*self.p.A*self.p.kmax**self.p.alpha,
                                max(self.p.nk*2,self.p.nk+8))
        self.postmg=np.linspace(0,2*self.p.mmax,max(self.p.nm*2,self.p.nm+8))
        self.postk=np.repeat(self.postkg,len(self.postmg))
        self.postm=np.tile(self.postmg,len(self.postkg))
    def cm_value(self,wealth,price,V):
        return cm_opt(wealth,price,self.k,self.m,V,self.edges,self.p.beta,self.p.b,self.p.eta)
    def step(self,V,f,price):
        p=self.p
        y,d,gb,gs,labor,W0=bargaining_discrete_continuousW(
            self.k,self.m,price,V,self.edges,p.beta,p.b,p.eta,
            p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
        VV=W0+(gb@f+gs.T@f)/p.Ntypes
        cm,invalid,trades,output=forward_dm(
            f,self.k,self.m,self.postkg,self.postmg,y,d,p.delta,p.Ntypes)
        ff,C,K,M,bad=cm_law(cm,self.postk,self.postm,self.kg,self.mg,
                            self.k,self.m,V,self.edges,price,p.beta,p.b,p.eta)
        return VV,ff,dict(invalid=invalid,invalid_CM=bad,
            consumption=C,capital=K,money=M,trades=trades,production=output,
            preCM=cm,y=y,d=d,buyer_gains=gb,seller_gains=gs,labor=labor)

def evaluate_auction(model,V,f,price,opt_tol=1e-10):
    p=model.p
    y,d,gb,gs,labor,W0=bargaining_discrete_continuousW(
        model.k,model.m,price,V,model.edges,p.beta,p.b,p.eta,
        p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
    vv=W0+(gb@f+gs.T@f)/p.Ntypes
    cm,invalid,trades,output=forward_dm(
        f,model.k,model.m,model.postkg,model.postmg,y,d,p.delta,p.Ntypes)
    lo,hi,minM,maxM,minK,maxK,minC,maxC,bad=cm_auction_extremes(
        cm,model.postk,model.postm,model.kg,model.mg,model.k,model.m,V,
        model.edges,price,p.beta,p.b,p.eta,opt_tol)
    if invalid or bad>1e-12:
        raise ValueError('infeasible DM/CM transition or escaping post-DM grid')
    return dict(price=price,money_min=minM,money_max=maxM,
                low=lo,high=hi,K_min=minK,K_max=maxK,
                C_min=minC,C_max=maxC,value=vv,trades=trades,
                production=output,dm=cm,y=y,d=d,
                money_start=float(f@model.m),capital_start=float(f@model.k),
                trading_pairs=int(np.count_nonzero(d)))
