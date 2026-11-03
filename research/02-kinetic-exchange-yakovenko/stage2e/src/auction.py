"""Conditional CM money-market clearing for continuous money/capital choice.

A price is accepted only when fiat supply lies in the CM optimal-money
CORRESPONDENCE at the SAME quoted price. We never rescale the money stock.
Neither one-period clearing nor a few fixed-point iterations certifies GE.
"""
from dataclasses import dataclass
import numpy as np
from continuous_core import evaluate_auction

@dataclass
class Auction:
    price:float
    distribution:np.ndarray
    value:np.ndarray
    trade_rate:float
    production:float
    capital:float
    consumption:float
    money:float
    money_min:float
    money_max:float
    mix:float
    goods_residual:float
    mass_residual:float
    regret_bound:float
    demand_evals:int
    price_bracket:tuple
    money_start:float
    capital_start:float
    nash_contracts:int
    status:str="ONE_PERIOD_OPTIMAL_CM_CLEARING_NOT_STATIONARY_GE"

class NoAuction(RuntimeError):
    pass

def clear_price(model,V,f,target=1.,prices=None,price_hint=None,
                opt_tol=3e-9,max_bisect=55,price_tol=1e-12):
    """Compute conditional CM price; near-optimal correspondence bound is explicit."""
    if prices is None:prices=np.geomspace(.10,25.,16)
    if not (np.isfinite(V).all() and np.isfinite(f).all()
            and f.min()>=-1e-13 and abs(f.sum()-1)<1e-10):
        raise ValueError("invalid value function or distribution")
    pgrid=np.unique(np.r_[np.array(prices,dtype=float),
              (np.array(price_hint)*np.array([.85,.9,.95,.98,1.,1.02,1.05,1.1,1.15])
               if price_hint is not None else np.array([]))])
    pgrid=pgrid[pgrid>0]
    cache={}
    def evaluate(price):
        x=float(price)
        if x not in cache:
            cache[x]=evaluate_auction(model,V,f,x,opt_tol=opt_tol)
        return cache[x]
    hits=[];edges=[]
    for price in pgrid:
        r=evaluate(price)
        if r['money_min']-1e-12<=target<=r['money_max']+1e-12:
            hits.append((price,price,r))
    if not hits:
        for lo,hi in zip(pgrid,pgrid[1:]):
            a=evaluate(lo);b=evaluate(hi)
            if a['money_max']<target and b['money_min']>target:
                edges.append((lo,hi))
            if a['money_min']>target and b['money_max']<target:
                edges.append((lo,hi))
        if price_hint is not None:
            edges.sort(key=lambda x:abs(np.log(np.sqrt(x[0]*x[1])/price_hint)))
        for left,right in edges:
            increasing=evaluate(left)['money_max']<target
            a=left;b=right;solution=None
            for _ in range(max_bisect):
                mid=(a+b)/2
                r=evaluate(mid)
                if r['money_min']-1e-12<=target<=r['money_max']+1e-12:
                    solution=(mid,r);break
                if (r['money_max']<target)==increasing:a=mid
                else:b=mid
                if b-a<price_tol*max(1,abs(mid)):break
            if solution is not None:
                hits.append((a,b,solution[1]));break
    if not hits:
        demand=[(k,v['money_min'],v['money_max']) for k,v in sorted(cache.items())]
        raise NoAuction(dict(status='NO_SUPPORTED_CM_CLEARING_PRICE',
                  price_min=float(pgrid.min()),price_max=float(pgrid.max()),
                  evaluations=len(cache),first_10=demand[:10],last_10=demand[-10:],
                  envelope=[float(min(z[1] for z in demand)),
                            float(max(z[2] for z in demand))],
                  candidate_crossings=len(edges)))
    if price_hint is not None:
        hits.sort(key=lambda z:abs(np.log(z[2]['price']/price_hint)))
    lower,upper,r=hits[0]
    denom=r['money_max']-r['money_min']
    if denom<1e-11:
        if abs(r['money_min']-target)>1e-9:
            raise NoAuction('single-valued demand does not clear issuer stock')
        mix=0.
    else:
        mix=(target-r['money_min'])/denom
    if not (-1e-9<=mix<=1+1e-9):
        raise NoAuction('invalid mixed-policy probability')
    mix=np.clip(mix,0,1)
    ff=(1-mix)*r['low']+mix*r['high']
    C=(1-mix)*r['C_min']+mix*r['C_max']
    K=(1-mix)*r['K_min']+mix*r['K_max']
    M=float(ff@model.m)
    residual=(C+K+M/r['price']
             -((1-model.p.delta)*r['capital_start']
              +r['production']+r['money_start']/r['price']))
    if abs(residual)>1e-9 or abs(M-target)>1e-9:
        raise NoAuction('goods or fiat-money budget failed')
    return Auction(r['price'],ff,r['value'],r['trades'],r['production'],
                   K,C,M,r['money_min'],r['money_max'],mix,residual,
                   abs(ff.sum()-1),opt_tol,len(cache),(lower,upper),
                   r['money_start'],r['capital_start'],r['trading_pairs'])

def stationary_iteration(model,V,f,maxit=140,price_guess=3.,
                         v_step=.15,f_step=.12,verbose=False):
    """Diagnostic nonlinear Bellman/price/measure iteration, NOT a GE oracle."""
    if abs(f@model.m-1)>1e-9:
        raise ValueError("initial money supply must equal one")
    history=[];price=price_guess
    for it in range(maxit):
        try:
            a=clear_price(model,V,f,price_hint=price)
        except NoAuction as exc:
            return dict(status='NO_FEASIBLE_CLEARING_PRICE_AT_ITERATION',
                iterations=it,diagnostics=exc.args,history=history),None
        ev=float(np.max(abs(a.value-V)))
        ef=float(np.max(abs(a.distribution-f)))
        history.append(dict(iteration=it+1,price=a.price,
            capital=float(f@model.k),money=float(f@model.m),
            trade_rate=a.trade_rate,consumption=a.consumption,
            bellman_sup=ev,distribution_sup=ef,
            max_portfolio_regret=a.regret_bound,
            clearing_price_evaluations=a.demand_evals,
            cash_bracket=[a.money_min,a.money_max],
            mix=a.mix,budget=a.goods_residual))
        if verbose:print('iteration',it+1,'price',a.price,
                         'Bellman',ev,'distribution',ef,flush=True)
        if ev<1e-7 and ef<1e-8 and a.regret_bound<1e-8:
            return dict(status='CANDIDATE_REQUIRES_FULL_NASH_AND_GRID_CERTIFICATION',
                        iterations=it+1,history=history),a
        V=(1-v_step)*V+v_step*a.value
        f=(1-f_step)*f+f_step*a.distribution
        price=a.price
    return dict(status='STATIONARY_DID_NOT_CONVERGE',
                iterations=maxit,history=history),a
