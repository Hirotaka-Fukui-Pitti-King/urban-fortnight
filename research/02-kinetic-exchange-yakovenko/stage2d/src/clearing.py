"""One-period Walrasian CM money clearing with truly indifferent portfolio lotteries.

Under a discrete portfolio approximation, demand jumps at optimal-policy
switches; interpolating the EXCESS DEMAND or rescaling money holdings is NOT
a valid equilibrium. At a *verified tie* an optimizing household can randomize
between its tied portfolios. A CM-clearing auction is NOT stationary GE:
continuation values and the full distribution must ALSO be self-consistent.
"""
from dataclasses import dataclass
import numpy as np
from molico_grid import u

@dataclass
class ClearingResult:
    status:str
    price:float
    price_lower:float
    price_upper:float
    money_lower:float
    money_upper:float
    mixing_probability:float
    inner_optimality_gap:float
    incoming_money:float
    next_money:float
    next_capital:float
    next_distribution:np.ndarray
    next_value:np.ndarray
    consumption:float
    production:float
    trades:float
    mass_residual:float
    budget_residual:float
    changed_bargaining_contracts:int
    active_mixed_mass:float

class ClearingError(RuntimeError):
    pass

def _candidate(model,V,f,price):
    newV,newF,details=model.step(V,f,float(price))
    if details["invalid"] or details["invalid_CM"]>1e-10:
        raise ClearingError("invalid DM or CM asset-grid transition")
    if abs(newF.sum()-1)>1e-10:
        raise ClearingError("probability mass lost")
    return newV,newF,details

def _choices(model,V,cm,price):
    pk=model.kpost
    pm=model.mpost
    resources=pk[:,None]+pm[:,None]/price-model.k[None,:]-model.m[None,:]/price
    values=np.full(resources.shape,-np.inf)
    feasible=resources>=-1e-12
    row,col=np.nonzero(feasible)
    values[row,col]=u(np.maximum(resources[row,col],0),model.p.b,model.p.eta)+model.p.beta*V[col]
    return np.argmax(values,axis=1),values

def clear_cm_price(model,V,f,target=1.,bracket=(2.45,3.0),
                   tolerance=1e-10,max_bisect=65):
    if not (np.isfinite(V).all() and f.min()>=0 and abs(f.sum()-1)<1e-9):
        raise ValueError("invalid initial value function or distribution")
    low,high=map(float,bracket)
    VL,FL,DL=_candidate(model,V,f,low)
    VH,FH,DH=_candidate(model,V,f,high)
    mlow=float(FL@model.m);mhigh=float(FH@model.m)
    if not (mlow<=target<=mhigh):
        raise ClearingError(f"no upward demand bracket: {mlow=}, {mhigh=}, {low=}, {high=}")
    for _ in range(max_bisect):
        p=.5*(low+high)
        VM,FM,DM=_candidate(model,V,f,p)
        if float(FM@model.m)<target:
            low=p;VL,FL,DL=VM,FM,DM;mlow=float(FM@model.m)
        else:
            high=p;VH,FH,DH=VM,FM,DM;mhigh=float(FM@model.m)
        if high-low<=tolerance*max(1,abs(p)):break
    # A discontinuous Nash bargaining decision is NOT a CM portfolio tie.
    if np.any(abs(DL["d"]-DH["d"])>1e-11) or np.any(abs(DL["y"]-DH["y"])>1e-11):
        raise ClearingError("Nash contract jumps; CM policy mixing is inapplicable")
    cm=DL["preCM"]
    if np.max(abs(cm-DH["preCM"]))>1e-11:
        raise ClearingError("post-DM wealth distribution changes across switch")
    pstar=.5*(low+high)
    _,value=_choices(model,V,cm,pstar)
    jl,_=_choices(model,V,cm,low)
    jh,_=_choices(model,V,cm,high)
    changes=(jl!=jh)&(cm>1e-12)
    if not np.any(changes):
        raise ClearingError("no supported CM policy indifference at the switch")
    maxv=value.max(axis=1)
    regret=np.maximum(maxv-value[np.arange(len(cm)),jl],
                      maxv-value[np.arange(len(cm)),jh])
    gap=float(regret[cm>1e-11].max())
    if gap>1e-6:
        raise ClearingError(f"suboptimal portfolio mixing would be required: {gap}")
    denom=mhigh-mlow
    if denom<=1e-12:raise ClearingError("no discrete money-demand jump")
    mix=(target-mlow)/denom
    if mix<-1e-12 or mix>1+1e-12:raise ClearingError("probability outside [0,1]")
    nf=(1-mix)*FL+mix*FH
    nv=(1-mix)*VL+mix*VH
    C=(1-mix)*DL["consumption"]+mix*DH["consumption"]
    Y=(1-mix)*DL["production"]+mix*DH["production"]
    Mnext=float(nf@model.m);Knext=float(nf@model.k)
    Min=float(f@model.m);Kin=float(f@model.k)
    uses=C+Knext+Mnext/pstar
    sources=(1-model.p.delta)*Kin+Y+Min/pstar
    return ClearingResult(
        "CM_MONEY_CLEARED_ON_TIED_DISCRETE_POLICY_ONLY_NOT_STATIONARY_GE",
        pstar,low,high,mlow,mhigh,float(mix),gap,Min,Mnext,Knext,
        nf,nv,float(C),float(Y),float(DL["trades"]),
        float(abs(nf.sum()-1)),float(uses-sources),0,
        float(cm[changes].sum())
    )

def stationary_attempt(model,V,f,init_price=2.7,max_iter=180,
                       damping_value=.45,damping_distribution=.25):
    """Feasibility-preserving but exploratory nonlinear stationary iteration.

    Every accepted interim step exactly clears CM money and satisfies true
    discrete-choice indifference. Failure to find such a step is reported, not
    patched using fake transfers, artificial tastes or post hoc normalization.
    """
    if abs(f@model.m-1)>1e-9:
        raise ValueError("initial nominal fiat money must equal issuer supply 1")
    history=[];price=init_price
    for iteration in range(max_iter):
        prices=np.unique(np.r_[np.geomspace(.2,12.,31),
            price*np.array([.85,.9,.95,.98,1.,1.02,1.05,1.1,1.15])])
        prices=prices[prices>0]
        valid=[]
        for trial in prices:
            try:
                _,fn,_=_candidate(model,V,f,trial)
                valid.append((float(trial),float(fn@model.m)-1.))
            except ClearingError:continue
        possible=[]
        for (pl,ml),(ph,mh) in zip(valid,valid[1:]):
            if ml<=0<=mh:possible.append((pl,ph))
        possible.sort(key=lambda x:abs(np.log(np.sqrt(x[0]*x[1])/price)))
        clearing=None
        for br in possible:
            try:
                clearing=clear_cm_price(model,V,f,bracket=br)
                break
            except ClearingError:continue
        if clearing is None:
            return dict(
                status="NO_FEASIBLE_MARKET_CLEARING_TIE_AT_CURRENT_ITERATION",
                iterations=iteration,history=history,last_price=price,
                candidate_price_count=len(valid),upcrossing_count=len(possible),
                money_excess_range=(
                    [min(z[1] for z in valid),max(z[1] for z in valid)]
                    if valid else None)),None
        dv=float(np.max(abs(clearing.next_value-V)))
        df=float(np.max(abs(clearing.next_distribution-f)))
        V=(1-damping_value)*V+damping_value*clearing.next_value
        f=(1-damping_distribution)*f+damping_distribution*clearing.next_distribution
        price=clearing.price
        history.append(dict(iteration=iteration+1,price=price,
            value_sup=dv,distribution_sup=df,
            capital=float(f@model.k),money=float(f@model.m),
            trade_rate=clearing.trades,mix=clearing.mixing_probability,
            max_portfolio_regret=clearing.inner_optimality_gap))
        if dv<1e-7 and df<1e-8 and clearing.inner_optimality_gap<1e-8:
            return dict(status="CANDIDATE_REQUIRES_SEPARATE_HIGH_GRID_GE_CERTIFICATION",
                iterations=iteration+1,history=history),clearing
    return dict(status="NOT_CONVERGED_JOINT_PRICE_BELLMAN_DISTRIBUTION",
                iterations=max_iter,history=history),clearing
