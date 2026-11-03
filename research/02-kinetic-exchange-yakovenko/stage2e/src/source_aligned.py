"""Molico--Zhang Section 4 ordering: clear CM with FIXED CM entrants.

A conditional price is computed for given entrant wealth and previous V.
Only AFTER the CM clears do we update the DM bargaining, value and next
entrant wealth distribution. The original bicubic/10,000-agent protocol is
NOT reproduced, and a stationary GE is not assumed.
"""
import numpy as np
from continuous_core import cm_auction_extremes,bargaining_discrete_continuousW
from molico_grid import forward_dm,mass_split

class CMPriceFailure(RuntimeError):
    pass

def make_CM_entrants(model,k0,m0):
    entrants=np.zeros(len(model.postk))
    bad=mass_split(model.postkg,model.postmg,m0,k0,1.,entrants)
    if bad or abs(entrants.sum()-1)>1e-12:
        raise ValueError('initial entrant state is not feasible')
    return entrants

def optimal_CM_entrants(model,V,entrants,price,tol=3e-9):
    p=model.p
    lo,hi,minM,maxM,minK,maxK,minC,maxC,bad=cm_auction_extremes(
        entrants,model.postk,model.postm,model.kg,model.mg,
        model.k,model.m,V,model.edges,price,p.beta,p.b,p.eta,tol)
    if bad>1e-10:raise CMPriceFailure('infeasible CM household choice')
    return dict(price=price,lo=lo,hi=hi,minM=minM,maxM=maxM,
                minK=minK,maxK=maxK,minC=minC,maxC=maxC,regret_tol=tol)

def clear_CM_entrants(model,V,entrants,price_hint=3.,M=1.,tol=3e-9):
    """Price clearing CONDITIONAL on fixed current CM entrants and prior V.

    Matching contracts are NOT recomputed inside this root's price trials:
    they enter the NEXT population iteration after CM price determination.
    This is the original manuscript's Section 4 step ordering.
    """
    prices=np.unique(np.r_[np.geomspace(.12,40,27),
              price_hint*np.array([.7,.8,.9,.95,.98,1.,1.02,1.05,1.1,1.2,1.3])])
    cache={}
    def trial(p):
        p=float(p)
        if p not in cache:
            cache[p]=optimal_CM_entrants(model,V,entrants,p,tol)
        return cache[p]
    solutions=[];scan=[]
    for price in prices:
        r=trial(price)
        if r['minM']-1e-11<=M<=r['maxM']+1e-11:
            solutions.append(r)
        scan.append((price,r['minM'],r['maxM']))
    if not solutions:
        brackets=[]
        for l,r in zip(scan,scan[1:]):
            if l[2]<M and r[1]>M:brackets.append((l[0],r[0],True))
            elif l[1]>M and r[2]<M:brackets.append((l[0],r[0],False))
        brackets.sort(key=lambda a:abs(np.log(np.sqrt(a[0]*a[1])/price_hint)))
        for left,right,increasing in brackets:
            for _ in range(60):
                mid=(left+right)*.5
                r=trial(mid)
                if r['minM']-1e-11<=M<=r['maxM']+1e-11:
                    solutions.append(r);break
                if (r['maxM']<M)==increasing:left=mid
                else:right=mid
                if right-left<1e-13*max(1.,mid):break
            if solutions:break
    if not solutions:
        lo=min(r[1] for r in scan)
        hi=max(r[2] for r in scan)
        raise CMPriceFailure(f'no CM-clearing price at pricehint={price_hint}; money range [{lo},{hi}]')
    solutions.sort(key=lambda x:abs(np.log(x['price']/price_hint)))
    r=solutions[0]
    spread=r['maxM']-r['minM']
    mix=0. if abs(spread)<1e-12 else np.clip((M-r['minM'])/spread,0,1)
    f=(1-mix)*r['lo']+mix*r['hi']
    C=(1-mix)*r['minC']+mix*r['maxC']
    K=(1-mix)*r['minK']+mix*r['maxK']
    money=float(f@model.m)
    rhs=float(entrants@(model.postk+model.postm/r['price']))
    lhs=C+K+money/r['price']
    if abs(money-M)>1e-8 or abs(lhs-rhs)>1e-8:
        raise CMPriceFailure('CM money or real resource accounting failed')
    return dict(price=r['price'],f=f,money=money,
       capital=K,consumption=C,budget_error=lhs-rhs,
       mass_error=float(f.sum()-1),minM=r['minM'],
       maxM=r['maxM'],mix=float(mix),
       prices_evaluated=len(cache),policy_regret_max=tol)

def next_DM(model,V,f,price):
    p=model.p
    y,d,bg,sg,labor,W0=bargaining_discrete_continuousW(
        model.k,model.m,price,V,model.edges,p.beta,p.b,p.eta,
        p.alpha,p.A,p.theta,p.y_choices,p.d_choices,p.delta)
    nextV=W0+(bg@f+sg.T@f)/p.Ntypes
    entrants,bad,trades,output=forward_dm(
        f,model.k,model.m,model.postkg,model.postmg,
        y,d,p.delta,p.Ntypes)
    if bad or abs(entrants.sum()-1)>1e-10:
        raise RuntimeError('invalid DM state transition/mass')
    if abs(entrants@model.postm-f@model.m)>1e-10:
        raise RuntimeError('DM fiat conservation violated')
    if abs(entrants@model.postk-(1-p.delta)*(f@model.k)-output)>1e-10:
        raise RuntimeError('DM production/capital accounting failed')
    return nextV,entrants,dict(trades=trades,output=output,
        max_seller_labor=float(labor.max()),
        active_contracts=int(np.count_nonzero(d)))

def source_iteration(model,V,entrants,price_hint=3.,maxit=60,
                     alpha_V=.06,alpha_g=.06,trace=False):
    """Return diagnostics without promoting false stationary equilibrium.

    Mixing entrant measures preserves the population and money stock because
    both current and proposed measures carry the same nominal issuer stock.
    """
    if abs(entrants@model.postm-1)>1e-9:
        raise ValueError('initial entrant fiat stock !=1')
    history=[];price=price_hint
    for it in range(maxit):
        try:
            current=clear_CM_entrants(model,V,entrants,price_hint=price)
        except CMPriceFailure as exc:
            return dict(status='NO_CM_CLEARING_PRICE',
                iterations=it,error=str(exc),history=history),None
        newV,newEnt,dm=next_DM(model,V,current['f'],current['price'])
        ev=float(abs(newV-V).max())
        eg=float(abs(newEnt-entrants).max())
        history.append(dict(iteration=it+1,price=current['price'],
            capital=current['capital'],money=current['money'],
            trades=dm['trades'],production=dm['output'],
            Bellman_sup=ev,entrant_distribution_sup=eg,
            money_error=current['money']-1.,
            CM_budget=current['budget_error'],
            mass_error=current['mass_error'],mix=current['mix']))
        if trace:
            print('iter',it+1,'price',current['price'],
                  'Bellman sup',ev,'distribution sup',eg,flush=True)
        if ev<1e-7 and eg<1e-8 and abs(current['budget_error'])<1e-9:
            return dict(status='CANDIDATE_DISCRETE_NASH_REQUIRES_FURTHER_CHECKS',
               iterations=it+1,history=history),current
        V=(1-alpha_V)*V+alpha_V*newV
        entrants=(1-alpha_g)*entrants+alpha_g*newEnt
        price=current['price']
    return dict(status='NO_STATIONARY_GE_AFTER_MAXIT',
                iterations=maxit,history=history),current
