"""Finite convex decomposition of the interpolated Molico–Zhang Nash problem.

For a FIXED pair of CM interpolation triangles the Nash log product is a
concave objective on a convex set. Maximizing over every triangle pair
recovers the continuous Nash optimum for this finite-grid interpolation.

This solver does not claim numerical interval-proof unless an independent
upper bound is provided. It never interpolates contractual policies.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import numpy as np

def enumerate_triangles(nk:int,nm:int)->list[tuple[int,int,int]]:
    triangles=[]
    for i in range(nk-1):
        for j in range(nm-1):
            a=i*nm+j
            b=(i+1)*nm+j
            c=(i+1)*nm+j+1
            d=i*nm+j+1
            triangles.extend([(a,b,c),(a,d,c)])
    return triangles


def restricted_cm_value(w, tri, model, V,price):
    from continuous_core import cm_opt
    p=model.p
    a,b,c=tri
    edges=np.array([[a,b],[a,c],[b,c]],dtype=np.int64)
    return float(cm_opt(w,price,model.k,model.m,V,edges,p.beta,p.b,p.eta)[0])


@dataclass
class NashResult:
    y:float
    d:float
    buyer_surplus:float
    seller_surplus:float
    log_nash:float
    triangles_considered:int
    triangles_pruned:int
    triangles_solved:int
    successes:int
    optimal_branch:tuple[int,int]|None
    dcp_pass:bool
    global_proof:bool=False


def solve_pair(model,V,price,buyer,seller,*,solver="CLARABEL",
               cap_branches=None,verbose=False)->NashResult:
    import cvxpy as cp
    p=model.p
    V=np.asarray(V,dtype=float)-float(np.max(V))
    empty=NashResult(0.,0.,0.,0.,float("-inf"),0,0,0,0,None,True)
    if model.m[buyer]<=0 or model.k[seller]<=0:
        return empty
    wb=(1-p.delta)*model.k[buyer]+model.m[buyer]/price
    ws=(1-p.delta)*model.k[seller]+model.m[seller]/price
    Wb=restricted_cm_value(wb,enumerate_triangles(p.nk,p.nm)[0],model,V,price)
    # Outside option must be globally optimized, not restricted to a triangle.
    from continuous_core import cm_opt
    Wb=float(cm_opt(wb,price,model.k,model.m,V,model.edges,
                   p.beta,p.b,p.eta)[0])
    Ws=float(cm_opt(ws,price,model.k,model.m,V,model.edges,
                   p.beta,p.b,p.eta)[0])
    capacity=p.A*model.k[seller]**p.alpha
    cash=model.m[buyer]/price
    triangles=enumerate_triangles(p.nk,p.nm)
    buyer_bounds=[restricted_cm_value(wb+capacity,tr,model,V,price)-Wb
                  for tr in triangles]
    seller_bounds=[restricted_cm_value(ws+cash,tr,model,V,price)-Ws
                   for tr in triangles]
    buyer_ids=[i for i,bound in enumerate(buyer_bounds) if bound>1e-11]
    seller_ids=[i for i,bound in enumerate(seller_bounds) if bound>1e-11]
    pairs=[(i,j) for i in buyer_ids for j in seller_ids]
    # Obtain a feasible incumbent only for branch pruning, NEVER for
    # certifying optimality. Bounds below dominate every feasible contract
    # in each individual triangle pair.
    from private_nash_bellman import nash_candidate
    q0,d0,score0=nash_candidate(buyer,seller,price,model.k,model.m,
                   V,model.edges,p.beta,p.b,p.eta,p.alpha,p.A,p.theta,
                   p.delta,13,11)
    if q0>0 and np.isfinite(score0) and score0>-1e200:
        incumbent=NashResult(float(q0),float(d0),0.,0.,float(score0),
                        len(triangles)**2,0,0,0,None,True)
    else:
        incumbent=empty
    candidate_pairs=[]
    for ib,is_ in pairs:
        bu=buyer_bounds[ib]
        su=seller_bounds[is_]
        ub=p.theta*np.log(bu)+(1-p.theta)*np.log(su)
        if ub>incumbent.log_nash:
            candidate_pairs.append((ib,is_))
    pairs=candidate_pairs
    if cap_branches is not None:
        pairs=pairs[:cap_branches] # Explicitly *not* a global search
    considered=len(triangles)**2
    pruned=considered-len(pairs)
    result=incumbent
    result.triangles_considered=considered
    result.triangles_pruned=pruned
    successes=solved=0
    failed_branches=0
    r=1/(1-p.alpha)
    for ib,is_ in pairs:
        tri_b=np.asarray(triangles[ib],dtype=int)
        tri_s=np.asarray(triangles[is_],dtype=int)
        weights_b=cp.Variable(3,nonneg=True)
        weights_s=cp.Variable(3,nonneg=True)
        yy=cp.Variable(nonneg=True)
        xx=cp.Variable(nonneg=True)
        cost_b=model.k[tri_b]+model.m[tri_b]/price
        cost_s=model.k[tri_s]+model.m[tri_s]/price
        cb=wb+yy-xx-cost_b@weights_b
        cs=ws+xx-cost_s@weights_s
        # CRRA u(c)=[b^(1-eta)-(c+b)^(1-eta)]/(eta-1)
        ub=(p.b**(1-p.eta)-cp.power(cb+p.b,1-p.eta))/(p.eta-1)
        us=(p.b**(1-p.eta)-cp.power(cs+p.b,1-p.eta))/(p.eta-1)
        effort=cp.inv_pos(1-cp.power(yy/capacity,r))-1
        B=ub+p.beta*(V[tri_b]@weights_b)-Wb
        S=us+p.beta*(V[tri_s]@weights_s)-Ws-effort
        obj=cp.Maximize(p.theta*cp.log(B)+(1-p.theta)*cp.log(S))
        cons=[cp.sum(weights_b)==1,cp.sum(weights_s)==1,
              cb>=0,cs>=0,B>=1e-10,S>=1e-10,
              xx<=cash,xx<=yy,yy<=capacity]
        problem=cp.Problem(obj,cons)
        if not problem.is_dcp():
            raise AssertionError(f"Non-DCP branch ({ib},{is_})")
        solved+=1
        try:
            problem.solve(solver=solver,verbose=verbose,
                          **({"tol_gap_abs":1e-9,"tol_feas":1e-9,
                              "tol_gap_rel":1e-9} if solver=="CLARABEL" else {}))
        except cp.SolverError:
            failed_branches+=1
            continue
        # An economically infeasible triangle pair is not a numerical
        # solver failure. Such cells are allowed by coarse surplus upper
        # bounds but ruled out by joint participation/budget constraints.
        if problem.status in ("infeasible","infeasible_inaccurate"):
            continue
        if problem.status not in ("optimal","optimal_inaccurate"):
            failed_branches+=1
            continue
        successes+=1
        q=float(yy.value)
        pay=float(xx.value)*price
        if q<=0 or pay<=0 or q>=capacity or pay>model.m[buyer]+1e-6:
            continue
        # Independent objective re-evaluation via *globally* optimal CM policy.
        from molico_grid import g
        buyerW=float(cm_opt(wb+q-pay/price,price,model.k,model.m,V,
                           model.edges,p.beta,p.b,p.eta)[0])
        sellerW=float(cm_opt(ws+pay/price,price,model.k,model.m,V,
                           model.edges,p.beta,p.b,p.eta)[0])
        BS=buyerW-Wb
        SS=sellerW-Ws-float(g(q,model.k[seller],p.alpha,p.A))
        if BS<=0 or SS<=0:
            continue
        score=float(p.theta*np.log(BS)+(1-p.theta)*np.log(SS))
        if score>result.log_nash:
            result=NashResult(q,pay,BS,SS,score,considered,pruned,
                              solved,successes,(ib,is_),True)
    result.triangles_solved=solved
    result.successes=successes
    # Polish the globally selected convex-branch incumbent in the original
    # continuous (quantity,payment) contract space. This is a NUMERICAL
    # accuracy step following (not replacing) the global branch enumeration.
    # It matters because 1e-7 quantity/payment errors can produce a
    # Bellman residual over 1e-6 when the continuation value is steep.
    if result.y>0:
        from private_nash_bellman import nash_polish,nash_score
        from continuous_core import cm_opt
        from molico_grid import g
        newy,newd,kkt=nash_polish(buyer,seller,result.y,result.d,
                                  model,V,price)
        if newy>0 and newd>0:
            adjusted=nash_score(newy,newd,buyer,seller,model,V,price)
            if np.isfinite(adjusted) and adjusted>=result.log_nash-1e-10:
                nb=float(cm_opt(wb+newy-newd/price,price,model.k,
                      model.m,V,model.edges,p.beta,p.b,p.eta)[0])
                ns=float(cm_opt(ws+newd/price,price,model.k,model.m,
                      V,model.edges,p.beta,p.b,p.eta)[0])
                B=nb-Wb
                S=ns-Ws-float(g(newy,model.k[seller],p.alpha,p.A))
                if B>0 and S>0:
                    result.y=float(newy)
                    result.d=float(newd)
                    result.buyer_surplus=float(B)
                    result.seller_surplus=float(S)
                    result.log_nash=float(adjusted)
    # Failed convex branches cannot be silently certified.
    if failed_branches:
        result.dcp_pass=False
    # Not even successful convex solver status is an exact numerical proof.
    return result
