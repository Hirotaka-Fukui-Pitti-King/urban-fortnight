"""Joint assets/fiat-money DP and discrete Nash bargaining (research prototype).

Portfolio logit decisions optimize expected utility with explicit Type-I
extreme-value taste shocks. No full general equilibrium is claimed.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.special import logsumexp, softmax
from scipy.optimize import least_squares

@dataclass(frozen=True)
class Params:
    beta:float=0.93
    alpha:float=0.36
    delta:float=0.08
    productivity:float=1.0
    buyer_strength:float=6.0
    eta:float=0.5
    lambda_meet:float=0.50
    mean_money:float=1.20
    taste_scale:float=0.15
    assets:tuple=(0.0,0.8,2.0,4.0,6.5,10.0)
    money_max:int=3
    z_values:tuple=(0.8,1.2)
    z_persistence:float=0.75
    q_values:tuple=(0.25,0.5,0.75)
    v_tol:float=1e-8
    f_tol:float=1e-9
    max_inner:int=1000

class Model:
    def __init__(self,prm=Params()):
        self.p=prm
        self.a=np.asarray(prm.assets,dtype=float)
        self.z=np.asarray(prm.z_values,dtype=float)
        self.m=np.arange(prm.money_max+1)
        self.q=np.r_[0.,np.asarray(prm.q_values,dtype=float)]
        assert len(self.a)>1 and np.all(np.diff(self.a)>0)
        assert self.q.max()<=1 and prm.lambda_meet<=1
        assert prm.taste_scale>0
        self.na=len(self.a);self.nm=len(self.m);self.nz=len(self.z)
        self.n=self.na*self.nm*self.nz;self.nchoices=self.na*self.nm
        self.aa,self.mm,self.zz=np.indices((self.na,self.nm,self.nz))
        self.ia=self.aa.flatten();self.im=self.mm.flatten();self.iz=self.zz.flatten()
        self.sid=lambda ia,im,iz: (ia*self.nm+im)*self.nz+iz
        self.ca=np.repeat(np.arange(self.na),self.nm)
        self.cm=np.tile(np.arange(self.nm),self.na)
        r=prm.z_persistence
        self.Pz=np.array([[(1+r)/2,(1-r)/2],[(1-r)/2,(1+r)/2]]) if self.nz==2 else None
        if self.Pz is None:raise ValueError("prototype uses two productivity states")

    def firms(self,K,L):
        p=self.p
        r=p.alpha*p.productivity*(K/L)**(p.alpha-1)-p.delta
        w=(1-p.alpha)*p.productivity*(K/L)**p.alpha
        Y=p.productivity*K**p.alpha*L**(1-p.alpha)
        return r,w,Y

    def central(self,V,r,w,phi):
        """CM joint (a',m') decision within ONE budget; q reduces CM wage hours."""
        pp=self.p
        EV=np.einsum('kj,jiz->kiz',self.Pz,V.reshape(self.na,self.nm,self.nz).transpose(2,0,1))
        discounted=pp.beta*EV[self.iz,:].reshape(self.n,self.nchoices)
        current=(1+r)*self.a[self.ia]+w*self.z[self.iz]+phi*self.m[self.im]
        costs=self.a[self.ca]+phi*self.m[self.cm]
        W=np.zeros((self.n,len(self.q)))
        pi=np.zeros((self.n,len(self.q),self.nchoices))
        consume=np.zeros((self.n,len(self.q),self.nchoices))
        for iq,q in enumerate(self.q):
            cash=current[:,None]-w*self.z[self.iz,None]*q-costs[None,:]
            good=cash>1e-10
            u=np.full(cash.shape,-1e9)
            u[good]=np.log(cash[good])
            value=u+discounted
            W[:,iq]=pp.taste_scale*logsumexp(value/pp.taste_scale,axis=1)
            pi[:,iq,:]=softmax(value/pp.taste_scale,axis=1)
            consume[:,iq,:]=np.where(good,cash,0.)
        return W,pi,consume

    def bargaining(self,W):
        """Exhaustive two-sided Nash bargaining on announced discrete (d,q) menu."""
        n=self.n;p=self.p
        base=W[:,0]
        U=np.full((n,n),-np.inf,dtype=float)
        B=np.zeros((n,n),dtype=float)
        S=np.zeros((n,n),dtype=float)
        dstar=np.zeros((n,n),dtype=np.int8)
        qstar=np.zeros((n,n),dtype=np.int8)
        for d in range(1,self.nm):
            valid_b=self.im>=d
            valid_s=self.im+d<self.nm
            bi=self.sid(self.ia,np.maximum(0,self.im-d),self.iz)
            si=self.sid(self.ia,np.minimum(self.nm-1,self.im+d),self.iz)
            for iq in range(1,len(self.q)):
                q=self.q[iq]
                bg=p.buyer_strength*np.log1p(q)+W[bi,0]-base
                sg=W[si,iq]-base
                gain_b=bg[:,None];gain_s=sg[None,:]
                feasible=valid_b[:,None] & valid_s[None,:] & (gain_b>0) & (gain_s>0)
                obj=np.where(feasible,p.eta*np.log(np.maximum(gain_b,1e-300))
                    +(1-p.eta)*np.log(np.maximum(gain_s,1e-300)),-np.inf)
                updated=obj>U
                U[updated]=obj[updated]
                B[updated]=np.broadcast_to(gain_b,(n,n))[updated]
                S[updated]=np.broadcast_to(gain_s,(n,n))[updated]
                dstar[updated]=d;qstar[updated]=iq
        return dstar,qstar,B,S

    def meeting_events(self,f,dstar,qstar):
        b,s=np.nonzero(dstar)
        wt=.5*self.p.lambda_meet*f[b]*f[s]
        mb=self.im[b]-dstar[b,s]
        ms=self.im[s]+dstar[b,s]
        buyer_after=self.sid(self.ia[b],mb,self.iz[b])
        seller_after=self.sid(self.ia[s],ms,self.iz[s])
        return b,s,wt,buyer_after,seller_after,qstar[b,s]

    def dm_value(self,f,W,d,q,B,S):
        expected=W[:,0].copy()
        expected+=.5*self.p.lambda_meet*(B@f+S.T@f)
        return expected

    def forward(self,f,pi,consume,events):
        b,s,wt,b_after,s_after,qidx=events
        mass=np.zeros((self.n,len(self.q)))
        mass[:,0]=f
        np.add.at(mass[:,0],b,-wt)
        np.add.at(mass[:,0],s,-wt)
        np.add.at(mass[:,0],b_after,wt)
        np.add.at(mass,(s_after,qidx),wt)
        assert mass.min()>-1e-10, mass.min()
        action=np.einsum('sq,sqj->sj',mass,pi)
        fresh=np.zeros((self.na,self.nm,self.nz))
        for iz in range(self.nz):
            newaction=action[self.iz==iz,:].sum(axis=0).reshape(self.na,self.nm)
            for iz2 in range(self.nz):
                fresh[:,:,iz2]+=newaction*self.Pz[iz,iz2]
        fnext=fresh.ravel()
        C=float(np.einsum('sq,sqj,sqj->',mass,pi,consume))
        L=float(f@self.z[self.iz]-np.dot(wt,self.z[self.iz[s]]*self.q[qidx]))
        Q=float(np.dot(wt,self.q[qidx]))
        return fnext,C,L,Q,action,mass

    def solve_inner(self,K,L,phi,initial=None,verbose=False):
        r,w,Y=self.firms(K,L)
        if 1+r<=0 or phi<=0:
            raise ValueError("Infeasible prices")
        if initial is None:
            f=np.ones(self.n)/self.n
            V=np.zeros(self.n)
        else:
            f=initial['f'].copy();V=initial['V'].copy()
        for it in range(self.p.max_inner):
            W,pi,c=self.central(V,r,w,phi)
            d,q,B,S=self.bargaining(W)
            nextV=self.dm_value(f,W,d,q,B,S)
            events=self.meeting_events(f,d,q)
            fnew,C,Lreal,Q,act,mass=self.forward(f,pi,c,events)
            errv=np.max(abs(nextV-V))
            errf=np.max(abs(fnew-f))
            if verbose and it%100==0:
                print("inner",it,errv,errf,flush=True)
            V=.6*V+.4*nextV
            f=.70*f+.30*fnew
            if errv<self.p.v_tol and errf<self.p.f_tol:
                break
        W,pi,c=self.central(V,r,w,phi)
        d,q,B,S=self.bargaining(W)
        nextV=self.dm_value(f,W,d,q,B,S)
        events=self.meeting_events(f,d,q)
        fnew,C,Lreal,Q,act,mass=self.forward(f,pi,c,events)
        Kreal=float(f@self.a[self.ia]);Mreal=float(f@self.m[self.im])
        info=dict(iterations=it+1,converged=bool(errv<self.p.v_tol and errf<self.p.f_tol),
            value_residual=float(max(abs(nextV-V))),
            distribution_residual=float(max(abs(fnew-f))),
            capital=Kreal,money=Mreal,labor=Lreal,consumption=C,
            service=Q,output=Y,interest=r,wage=w,phi=phi,
            goods_residual=Y-C-self.p.delta*Kreal,
            capital_price_consistency=Kreal-K,
            labor_price_consistency=Lreal-L,
            money_supply_excess=Mreal-self.p.mean_money,
            trades_per_person=float(sum(events[2])),
            capital_money_cov=float(f@(self.a[self.ia]*self.m[self.im])-Kreal*Mreal),
            max_boundary_asset_mass=float(f[self.ia==self.na-1].sum()),
            max_boundary_money_mass=float(f[self.im==self.nm-1].sum()))
        info['goods_accounting_identity_error'] = (
            info['goods_residual']
            - ((r+self.p.delta)*(K-Kreal)+w*(L-Lreal)))
        return {'f':f,'V':V,'pi':pi,'W':W,'cash_consumption':c,'d':d,
                'q':q,'events':events,'mass':mass,'next_f':fnew,'info':info}

    def solve_prices(self,start=(4.5,.97,.6),verbose=False):
        """Exploratory nonlinear price solve; check result before any equilibrium claim."""
        cache={};last=None
        def obj(x):
            nonlocal last
            K,L,phi=x
            key=tuple(np.round(x,9))
            if key not in cache:
                sol=self.solve_inner(K,L,phi,initial=last)
                if not sol['info']['converged']:
                    raise RuntimeError(
                        "Cannot evaluate GE excess demand: household/distribution "
                        + "fixed point not converged at K,L,phi="
                        + str((K,L,phi))
                        + "; value residual="
                        + str(sol['info']['value_residual']))
                if sol['info']['max_boundary_asset_mass'] > .01:
                    raise RuntimeError(
                        "More than 1% probability at asset grid maximum; GE price candidate unreliable")
                cache[key]=sol
                last=sol
            else:
                sol=cache[key]
            d=sol['info']
            errors=np.array([d['capital_price_consistency']/K,
                d['labor_price_consistency'],d['money_supply_excess']])
            if verbose:
                print('prices',x,'errors',errors,'inner_converged',d['converged'],flush=True)
            return errors
        fit=least_squares(obj,np.array(start),bounds=([.4,.35,.03],[25.,1.05,5.]),
            max_nfev=80,xtol=1e-9,ftol=1e-9,gtol=1e-9,diff_step=1e-3)
        sol=self.solve_inner(*fit.x,initial=last)
        if (not sol['info']['converged']
                or sol['info']['max_boundary_asset_mass'] > .01):
            raise RuntimeError("Final candidate violates inner convergence/asset grid GE gate")
        sol['info']['prices_solver']={
            'success':bool(fit.success),'message':str(fit.message),
            'iterations':int(fit.nfev),'outer_residuals':obj(fit.x).tolist(),
            'prices':fit.x.tolist()}
        # SciPy success alone is never evidence of an economic equilibrium.
        sol['info']['verified_GE']=bool(
            sol['info']['converged']
            and max(abs(np.asarray(sol['info']['prices_solver']['outer_residuals'])))<1e-6
            and abs(sol['info']['goods_residual'])<1e-6)
        return sol
