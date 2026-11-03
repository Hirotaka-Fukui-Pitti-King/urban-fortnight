"""Monte Carlo dynamics using the *same* optimal Stage 0 savings policy.

Continuous asset updates: never replace optimal choices with lottery rounding.
Prices are fixed at the infinite-population stationary general equilibrium.
"""
from pathlib import Path
import json,sys
import numpy as np
from numba import njit

@njit(cache=True)
def particle_path(a,policy,consumption,z,P,n_agents,burnin,sample_periods,seed):
    np.random.seed(seed)
    nz=len(z)
    agents_a=np.full(n_agents,a[0],dtype=np.float64)
    agents_z=np.zeros(n_agents,dtype=np.int64)
    P_cum=np.zeros_like(P)
    for k in range(nz):
        run=0.
        for j in range(nz):
            run+=P[k,j]
            P_cum[k,j]=run
    sum_k=0.;sum_c=0.;samples=0
    for i in range(n_agents):
        agents_z[i]=int(np.random.random()*nz)
    for t in range(burnin+sample_periods):
        period_c=0.
        for i in range(n_agents):
            k=agents_z[i];x=agents_a[i]
            if x>a[-1]: raise ValueError("particle escaped asset grid")
            idx=np.searchsorted(a,x)
            if idx==0: idx=1
            if idx>=len(a): idx=len(a)-1
            wt=(x-a[idx-1])/(a[idx]-a[idx-1])
            gn=policy[k,idx-1]*(1-wt)+policy[k,idx]*wt
            cn=consumption[k,idx-1]*(1-wt)+consumption[k,idx]*wt
            period_c+=cn
            if gn<a[0]-1e-10 or gn>a[-1]+1e-10:
                raise ValueError("policy beyond grid")
            agents_a[i]=gn
            u=np.random.random()
            s=0
            while s<nz-1 and u>P_cum[k,s]: s+=1
            agents_z[i]=s
        if t>=burnin:
            sum_k+=np.sum(agents_a)/n_agents
            sum_c+=period_c/n_agents
            samples+=1
    return agents_a,agents_z,sum_k/samples,sum_c/samples

def compare_stationary(reference,n_agents,seed,burnin=1200,sample_periods=100):
    a,z,P=reference["a"],reference["z"],reference["P"]
    assets,state,Kmean,Cmean=particle_path(a,reference["g"],reference["c"],z,P,n_agents,burnin,sample_periods,seed)
    from scipy.stats import wasserstein_distance
    src=str(Path(__file__).resolve().parents[2]/"00-heterogeneous-agent-ge"/"src")
    if src not in sys.path:sys.path.insert(0,src)
    from aiyagari import gini
    mu=reference["mu"];weights=mu.sum(axis=0)
    return {"n_agents":int(n_agents),"seed":int(seed),"burnin":int(burnin),
            "sample_periods":int(sample_periods),"K_mean":float(Kmean),"C_mean":float(Cmean),
            "K_error":float(Kmean-reference["summary"]["K_demand"]),
            "C_error":float(Cmean-reference["summary"]["C"]),
            "K_relative_error":float(abs(Kmean/reference["summary"]["K_demand"]-1)),
            "terminal_gini":float(gini(assets,np.ones(n_agents)/n_agents)),
            "terminal_income_shares":(np.bincount(state,minlength=len(z))/n_agents).tolist(),
            "terminal_asset_wasserstein":float(wasserstein_distance(assets,a,v_weights=weights)),
            "terminal_K":float(np.mean(assets))}

def save_agent_results(rows,folder):
    import pandas as pd
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/"agent_comparison.json").write_text(json.dumps(rows,indent=2)+"\n")
    pd.DataFrame(rows).drop(columns="terminal_income_shares").to_csv(folder/"agent_comparison.csv",index=False)
