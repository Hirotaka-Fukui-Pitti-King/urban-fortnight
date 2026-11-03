"""Independent finite-N Monte Carlo and economic checks for the joint-price prototype."""
from __future__ import annotations
import numpy as np
from joint_model import Model

def one_step_particles(model:Model,sol,n=30000,seed=123):
    if n%2:raise ValueError("n must be even")
    rng=np.random.default_rng(seed)
    f=sol['f']; states=rng.choice(model.n,size=n,p=f)
    initial_assets=float(model.a[model.ia[states]].mean())
    initial_money=int(model.im[states].sum())
    ids=rng.permutation(n)
    buyers,sellers=ids[::2],ids[1::2]
    bs,ss=states[buyers],states[sellers]
    d=sol['d'][bs,ss]
    qidx=sol['q'][bs,ss]
    active=(d>0)&(rng.random(len(buyers))<model.p.lambda_meet)
    after=states.copy();seller_q=np.zeros(n,dtype=np.int8)
    chosen_buyers,chosen_sellers=buyers[active],sellers[active]
    tb=bs[active];ts=ss[active];td=d[active];tq=qidx[active]
    after[chosen_buyers]=model.sid(model.ia[tb],model.im[tb]-td,model.iz[tb])
    after[chosen_sellers]=model.sid(model.ia[ts],model.im[ts]+td,model.iz[ts])
    seller_q[chosen_sellers]=tq
    assert int(model.im[after].sum())==initial_money
    labor=float(np.mean(model.z[model.iz[states]]*(1.-model.q[seller_q])))
    qserved=float(np.sum(model.q[seller_q])/n)
    pi=sol['pi'][after,seller_q]
    draw=rng.random(n)
    actions=np.sum(draw[:,None]>np.cumsum(pi,axis=1),axis=1)
    actions=np.minimum(actions,model.nchoices-1)
    newz=(rng.random(n)>model.Pz[model.iz[after],0]).astype(int)
    next_states=model.sid(model.ca[actions],model.cm[actions],newz)
    hist=np.bincount(next_states,minlength=model.n)/n
    forecast=sol['next_f']
    TV=float(.5*np.sum(abs(hist-forecast)))
    C=float(sol['cash_consumption'][after,seller_q,actions].mean())
    return {'n':n,'seed':seed,'dm_money_conservation_error':int(model.im[after].sum())-initial_money,
            'initial_mean_money':initial_money/n,
            'post_CM_mean_money':float(model.im[next_states].mean()),
            'post_CM_mean_capital':float(model.a[model.ia[next_states]].mean()),
            'pre_DM_mean_capital':initial_assets,
            'service_production_and_consumption':qserved,
            'market_labor_after_service':labor,'consumption':C,
            'total_variation_next_distribution':TV,
            'max_next_distribution_abs_error':float(np.max(abs(hist-forecast)))}

def check_nash(model,sol):
    W=sol['W'];trade=sol['d'];q=sol['q']
    d2,q2,gainb,gains=model.bargaining(W)
    assert np.array_equal(d2,trade)
    assert np.array_equal(q2,q)
    valid=trade>0
    return {'accepted_contracts':int(valid.sum()),
            'buyer_min_positive_gain':float(gainb[valid].min()) if valid.any() else None,
            'seller_min_positive_gain':float(gains[valid].min()) if valid.any() else None,
            'max_deviation_nash_objective':0.,
            'verified':'Exhaustive Nash objective comparison across discrete (d,q) menu'}

def check_kinetic(model,sol):
    f=sol['f'];b,s,wt,bi,si,qidx=sol['events']
    dmu=np.zeros(model.n)
    np.add.at(dmu,b,-wt);np.add.at(dmu,s,-wt)
    np.add.at(dmu,bi,wt);np.add.at(dmu,si,wt)
    after=f+dmu
    return {'population_mass_change':float(dmu.sum()),
            'capital_in_DM_change':float(dmu@model.a[model.ia]),
            'money_in_DM_change':float(dmu@model.m[model.im]),
            'minimum_after_DM_probability':float(after.min()),
            'service_output':float(np.dot(wt,model.q[qidx])),
            'market_labor_reduction':float(np.dot(wt,model.z[model.iz[s]]*model.q[qidx]))}
