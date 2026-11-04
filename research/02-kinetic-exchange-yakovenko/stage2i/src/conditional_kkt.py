"""Direct endogenous Nash-contract KKT/Bellman system for the 5x5 private economy.

Rather than differentiating the piecewise fast Nash argmax operator, contract
quantities and nonbinding payments are simultaneous unknowns. Every CM value
is globally reoptimized on the inherited piecewise-affine grid. Local stationarity
does NOT establish global Nash dominance: a separate all-pair check is required.

This is a numerical ATTEMPT, not a globally convergent algorithm.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.special import expit, logit
from scipy.optimize import least_squares

HERE=Path(__file__).resolve().parents[1]
BASE=HERE.parent
for src in (BASE/"stage2h"/"src",BASE/"stage2h"/"scripts",
            BASE/"stage2g"/"src",BASE/"stage2e"/"src",
            BASE/"stage2c"/"src"):
    sys.path.insert(0,str(src))
from continuous_core import cm_opt, ContinuousModel
from molico_grid import Calibration, g
from active_nash import active_operator
from solve_5x5_active import active_complete
from private_nash_bellman import _frozen_operator


def cm(model,v,p,w):
    par=model.p
    return cm_opt(float(w),p,model.k,model.m,v,model.edges,
                  par.beta,par.b,par.eta)


def stable_logit(x):
    return float(logit(np.clip(x,1e-10,1-1e-10)))


class ConditionalKKT:
    def __init__(self,model,price,y,d,*,payment_tol=1e-6):
        self.model=model
        self.price=float(price)
        self.p=model.p
        self.pairs=[]
        self.upper=[]
        for i in range(model.n):
            for j in range(model.n):
                if i!=12 and j!=12:continue
                if y[i,j]<=0:continue
                self.pairs.append((i,j))
                self.upper.append(bool(d[i,j]>=model.m[i]-payment_tol))
        assert len(self.pairs)==39,(len(self.pairs),self.pairs)
        self.upper=np.asarray(self.upper,dtype=bool)
        self.nv=model.n-1
        self.nq=len(self.pairs)
        self.free_indices=np.where(~self.upper)[0]
        self.nfree=len(self.free_indices)
        self.length=self.nv+self.nq+self.nfree
        self.capacity=np.array([self.p.A*model.k[j]**self.p.alpha
                                for i,j in self.pairs],float)
        self.cash=np.array([model.m[i]/price for i,j in self.pairs],float)

    def initialize(self,z,y,d):
        z=np.asarray(z,float)
        ytheta=np.array([stable_logit(float(y[i,j])/self.capacity[n])
                         for n,(i,j) in enumerate(self.pairs)])
        ptheta=np.array([stable_logit(
            (float(d[self.pairs[n][0],self.pairs[n][1]])/self.price)
            /self.cash[n]) for n in self.free_indices])
        return np.r_[z,ytheta,ptheta]

    def unpack(self,u):
        z=u[:self.nv]
        quantities=self.capacity*expit(u[self.nv:self.nv+self.nq])
        x=self.cash.copy()
        x[self.free_indices]=self.cash[self.free_indices]*expit(
            u[self.nv+self.nq:])
        v=np.r_[0.,z]
        return v,quantities,x

    def evaluate(self,u,lm,*,details=False):
        model=self.model
        p=self.p
        price=self.price
        v,q,x=self.unpack(u)
        outside=np.empty(model.n)
        for state in range(model.n):
            wealth=(1-p.delta)*model.k[state]+model.m[state]/price
            outside[state]=cm(model,v,price,wealth)[0]
        T=outside.copy()
        fq=np.zeros(self.nq)
        fx=np.zeros(self.nfree)
        constraint=np.zeros(self.nq)
        observations=[]
        payments=np.zeros((model.n,model.n))
        quantities=np.zeros_like(payments)
        for n,(i,j) in enumerate(self.pairs):
            qty=float(q[n]);xx=float(x[n])
            wbi=(1-p.delta)*model.k[i]+model.m[i]/price
            wsj=(1-p.delta)*model.k[j]+model.m[j]/price
            bw,_,_,bc=cm(model,v,price,wbi+qty-xx)
            sw,_,_,sc=cm(model,v,price,wsj+xx)
            production=g(qty,model.k[j],p.alpha,p.A)
            B=float(bw-outside[i])
            S=float(sw-outside[j]-production)
            # Only matches with a partner drawn from the Dirac
            # distribution affect an individual's Bellman value.
            if j==12:
                T[i]+=lm*B/p.Ntypes
            if i==12:
                T[j]+=lm*S/p.Ntypes
            quantities[i,j]=qty
            payments[i,j]=xx*price
            ell=(qty/self.capacity[n])**(1/(1-p.alpha))
            gp=ell/(qty*(1-p.alpha)*(1-ell)**2)
            bp=(max(0.,bc)+p.b)**(-p.eta)
            sp=(max(0.,sc)+p.b)**(-p.eta)
            # Log marginal-benefit ratios: exactly zero at smooth FOC.
            # These formulas use the CM envelope only with strictly
            # positive consumption. c=0 requires directional KKT.
            positive_B=max(B,1e-8)
            positive_S=max(S,1e-8)
            fq[n]=np.log(max(1e-300,p.theta*bp*positive_S))-np.log(
                max(1e-300,(1-p.theta)*gp*positive_B))
            gx=np.log(max(1e-300,(1-p.theta)*sp*positive_B))-np.log(
                max(1e-300,p.theta*bp*positive_S))
            if not self.upper[n]:
                fx[np.where(self.free_indices==n)[0][0]]=gx
            # Overdetermined feasibility residuals, identically zero
            # at a feasible conditional root.
            constraint[n]=(
                20.*max(0.,xx-qty)+
                2.*max(0.,-B)+2.*max(0.,-S)+
                2.*max(0.,1e-10-float(bc))+
                2.*max(0.,1e-10-float(sc)))
            if details:
                observations.append(dict(buyer=i,seller=j,
                    quantity=qty,nominal_payment=xx*price,
                    buyer_surplus=B,seller_surplus=S,
                    buyer_cm_consumption=float(bc),
                    seller_cm_consumption=float(sc),
                    payment_upper=bool(self.upper[n]),
                    x_less_equal_y=bool(xx<=qty+1e-8),
                    quantity_FOC=float(fq[n]),
                    payment_FOC=float(gx),
                    payment_KKT_violation=float(max(0.,-gx)
                                                if self.upper[n] else abs(gx))))
        relative=T[1:]-T[0]-v[1:]
        res=np.r_[relative,0.5*fq,0.5*fx,constraint]
        if details:
            return res,dict(bellman_sup=float(max(abs(relative))),
                     kkt_quantity_max=float(max(abs(fq))),
                     kkt_free_payment_max=float(max(abs(fx)) if len(fx) else 0.),
                     max_constraint_penalty=float(max(constraint)),
                     max_payment_upper_violation=float(max(
                         (a["payment_KKT_violation"] for a in observations
                          if a["payment_upper"]),default=0.)),
                     min_buyer_surplus=float(min(a["buyer_surplus"] for a in observations)),
                     min_seller_surplus=float(min(a["seller_surplus"] for a in observations)),
                     minimum_CM_consumption=float(min(min(a["buyer_cm_consumption"],
                          a["seller_cm_consumption"]) for a in observations)),
                     observations=observations),quantities,payments,v,T
        return res

    def validate(self,u,lm):
        _,diag,qty,payment,v,T=self.evaluate(u,lm,details=True)
        diag["conditional_solution"]=bool(
            diag["bellman_sup"]<1e-8 and
            diag["kkt_quantity_max"]<1e-5 and
            diag["kkt_free_payment_max"]<1e-5 and
            diag["max_payment_upper_violation"]<1e-5 and
            diag["max_constraint_penalty"]<1e-8 and
            diag["minimum_CM_consumption"]>0 and
            diag["min_buyer_surplus"]>0 and
            diag["min_seller_surplus"]>0)
        return diag,qty,payment,v,T


def fit_step(system,u0,lm,max_nfev=20):
    start=time.monotonic()
    best=(float("inf"),u0.copy())
    calls=0
    def fun(u):
        nonlocal best,calls
        r=system.evaluate(u,lm)
        calls+=1
        score=float(np.max(abs(r)))
        if np.isfinite(score) and score<best[0]:
            best=(score,u.copy())
        return np.nan_to_num(r,nan=1e8,posinf=1e8,neginf=-1e8)
    sol=least_squares(fun,u0,method="trf",jac="2-point",
        diff_step=2e-6,max_nfev=max_nfev,ftol=1e-11,xtol=1e-11,
        gtol=1e-11,x_scale="jac")
    options=[sol.x,best[1]]
    trials=[]
    for cand in options:
        d,_,_,_,_=system.validate(cand,lm)
        trials.append((d["bellman_sup"]+
                       d["kkt_quantity_max"]+
                       d["kkt_free_payment_max"]+
                       d["max_constraint_penalty"],cand,d))
    trials.sort(key=lambda x:x[0])
    _,u,d=trials[0]
    return u,dict(lambda_matching=float(lm),root_success=bool(sol.success),
                  candidate_accepted=bool(d["conditional_solution"]),
                  bellman_sup=d["bellman_sup"],
                  kkt_quantity_max=d["kkt_quantity_max"],
                  kkt_free_payment_max=d["kkt_free_payment_max"],
                  payment_upper_violation=d["max_payment_upper_violation"],
                  constraint_penalty=d["max_constraint_penalty"],
                  min_buyer_surplus=d["min_buyer_surplus"],
                  min_seller_surplus=d["min_seller_surplus"],
                  function_evaluations=calls,
                  elapsed_seconds=time.monotonic()-start,
                  message=str(sol.message)), d


def independent_candidate_check(system,u,lm,*,global_check=False):
    from convex_nash import solve_pair
    diag,q,payment,v,T=system.validate(u,lm)
    model=system.model; p=model.p
    f=np.zeros(model.n);f[12]=1.
    o=np.array([cm(model,v,system.price,(1-p.delta)*model.k[i]+
                   model.m[i]/system.price)[0] for i in range(model.n)])
    fast,fast_q,fast_d,_,_=active_operator(v,f,system.price,model,9,7)
    fast_full=o+lm*(fast-o)
    result=dict(conditional_Bellman_sup=diag["bellman_sup"],
                independent_fast_Bellman_sup=float(max(abs(
                    fast_full[1:]-fast_full[0]-v[1:]))),
                conditional_KKT_pass=bool(diag["conditional_solution"]),
                fast_policy_max_quantity_diff=float(np.max(np.abs(fast_q-q))),
                fast_policy_max_payment_diff=float(np.max(np.abs(fast_d-payment))),
                global_all49_attempted=False,global_Bellman_sup=None,
                verified_source_rate_5x5_private_fixedpoint=False)
    if global_check and diag["conditional_solution"]:
        gy=np.zeros_like(q);gd=np.zeros_like(payment)
        gaps=[]
        unresolved=[]
        for i in range(model.n):
            for j in range(model.n):
                if i!=12 and j!=12:continue
                answer=solve_pair(model,v,system.price,i,j)
                gy[i,j]=answer.y
                gd[i,j]=answer.d
                if answer.unresolved_branches:
                    unresolved.append([i,j,answer.unresolved_branches])
                # Log comparison only when both positive.
                gaps.append(dict(buyer=i,seller=j,
                            unresolved_branches=answer.unresolved_branches,
                            global_log_nash=answer.log_nash))
        TT=_frozen_operator(v,f,system.price,model.k,model.m,model.edges,
                p.beta,p.b,p.eta,p.alpha,p.A,p.delta,p.Ntypes,gy,gd)
        global_T=o+lm*(TT-o)
        global_sup=float(max(abs(global_T[1:]-global_T[0]-v[1:])))
        result.update(global_all49_attempted=True,
            global_Bellman_sup=global_sup,
            unresolved_global_pair_branches=unresolved,
            max_globally_reoptimized_quantity_diff=float(np.max(np.abs(gy-q))),
            max_globally_reoptimized_payment_diff=float(np.max(np.abs(gd-payment))),
            verified_source_rate_5x5_private_fixedpoint=bool(
                abs(lm-1)<1e-12 and global_sup<1e-8 and
                not unresolved and
                diag["conditional_solution"]))
    return result


def run(folder=None,max_nfev=25):
    folder=Path(folder) if folder is not None else HERE/"results"
    folder.mkdir(parents=True,exist_ok=True)
    saved=np.load(BASE/"stage2h"/"results"/"private_5x5_active_last_accepted.npz")
    initial=float(saved["matching_multiplier"])
    assert abs(initial-0.609033203125)<1e-10,initial
    z=np.asarray(saved["relative_value"])
    model=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2))
    f=np.zeros(model.n);f[12]=1.
    v=np.r_[0.,z]
    base=active_complete(v,model,f,2.5,initial)
    value=v+base[0]/(1-model.p.beta)
    _,y,d,_,_=active_operator(value,f,2.5,model,9,7)
    sys=ConditionalKKT(model,2.5,y,d)
    u=sys.initialize(z,y,d)
    initial_diag,_,_,_,_=sys.validate(u,initial)
    print("JOINT_KKT_INITIAL",json.dumps({k:v for k,v in initial_diag.items()
                                        if k!="observations"}),flush=True)
    path=[]
    accepted_lambda=initial
    accepted_u=u.copy()
    # Small steps first to identify when the conditional active set breaks.
    for lam in (0.6091,0.6092,0.6094,0.6096,0.6098,0.61,0.62,1.):
        attempted,summary,details=fit_step(
            sys,accepted_u,lam,max_nfev=max_nfev)
        path.append(summary)
        print("JOINT_KKT_STEP",json.dumps(summary),flush=True)
        if summary["candidate_accepted"]:
            accepted_lambda=lam
            accepted_u=attempted.copy()
            np.savez(folder/"joint_kkt_last_accepted.npz",
                relative_value=accepted_u[:24],
                joint_unknown=accepted_u,matching_multiplier=lam)
        else:
            # The first failure is an active-set event / loss of convergence
            # candidate, NOT a nonexistence proof. Still attempt direct
            # lambda=1 if it was not already attempted.
            if lam!=1.:
                trial,info,_=fit_step(sys,accepted_u,1.,max_nfev=min(12,max_nfev))
                path.append(dict(info,initialization="last_accepted_direct"))
                print("JOINT_KKT_SOURCE_DIRECT",json.dumps(path[-1]),flush=True)
                if info["candidate_accepted"]:
                    accepted_lambda=1.
                    accepted_u=trial.copy()
            break
    check=independent_candidate_check(
        sys,accepted_u,accepted_lambda,
        global_check=abs(accepted_lambda-1)<1e-12)
    report=dict(status=("SOURCE_RATE_CONDITIONAL_CANDIDATE" if
            accepted_lambda>=1.-1e-12 else
            "CONDITIONAL_BRANCH_DID_NOT_REACH_SOURCE_RATE"),
        grid=[5,5],price=2.5,partner_index=12,
        matching_start=initial,matching_last_accepted=accepted_lambda,
        active_pairs=39,nonbinding_payment_pairs=int(sys.nfree),
        base_diagnostics={k:v for k,v in initial_diag.items()
                          if k!="observations"},
        path=path,final_check=check,
        full_source_rate_globally_certified=check[
            "verified_source_rate_5x5_private_fixedpoint"],
        stationary_GE=False)
    (folder/"joint_kkt_source_rate_attempt.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("JOINT_KKT_SUMMARY",json.dumps({k:v for k,v in report.items()
          if k not in ("path","base_diagnostics")}),flush=True)
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-nfev",type=int,default=25)
    args=ap.parse_args()
    run(max_nfev=args.max_nfev)
