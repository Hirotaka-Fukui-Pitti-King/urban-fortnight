"""Execute optimal exchange candidates and compare to stochastic agents."""
from pathlib import Path
import sys, json, argparse
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from monetary_matching import (Params,solve_candidate,diagnostics,
    foley_style_transaction_benchmark)
from particle_simulator import simulate

parser=argparse.ArgumentParser()
parser.add_argument("--quick",action="store_true")
parser.add_argument("--out",type=Path,default=ROOT/"results")
args=parser.parse_args()
args.out.mkdir(parents=True,exist_ok=True)
cases={"C_uniform":Params(),
       "C_state_dependent":Params(meeting_rate=.2,assortativity=3)}
rows=[];particle_rows=[]
for label,p in cases.items():
    s=solve_candidate(p)
    d=diagnostics(s,p)
    d.update(foley_style_transaction_benchmark(s,p))
    d["model"]=label
    if (d["participation_failures"] or d["money_mass_error"]>1e-10 or
        d["stationarity_sup_error"]>1e-9 or d["bellman_sup_error"]>1e-9):
        raise RuntimeError("Not an equilibrium candidate: "+str(d))
    rows.append(d)
    Ns=[1000,4000] if args.quick else [1500,6000,20000]
    seeds=[11,22] if args.quick else [11,22,33,44]
    for N in Ns:
        for seed in seeds:
            x=simulate(p,s,N,seed,burnin=600 if args.quick else 1800,
                measure_count=20 if args.quick else 70,measure_every=10)
            x["model"]=label
            particle_rows.append(x)
            print(label,N,seed,"W1",x["average_mass_W1"],
                  "trade error",x["service_trade_error"],flush=True)
    pd.DataFrame({"money":range(p.max_tokens+1),"equilibrium_mass":s["f"],
        "maxent_mass":d["maxent_distribution"]}).to_csv(
            args.out/(label+"_stationary_money.csv"),index=False)
(args.out/"economic_diagnostics.json").write_text(json.dumps(rows,indent=2)+"\n")
(args.out/"particle_comparison.json").write_text(json.dumps(particle_rows,indent=2)+"\n")
pd.DataFrame([{k:v for k,v in x.items() if not isinstance(v,list)}
    for x in particle_rows]).to_csv(args.out/"particle_comparison.csv",index=False)
(args.out/"model_comparison.json").write_text(json.dumps({
    "A":{"name":"Stationary Aiyagari economy with capital production",
         "status":"previously solved and verified"},
    "B":{"name":"Exogenous pure token transfer without reciprocal service",
         "status":"heuristic, violates strict bilateral monotone participation"},
    "C":{"name":"Optimizing posted-price service-for-token monetary search",
         "status":"verified stationary subeconomy and kinetic operator; no nonseparable joint HANK-money equilibrium"},
    "caveats":["No Nash bargaining; the one-token service price is fixed by the trading protocol.",
        "The no-trade equilibrium coexists with the active monetary equilibrium.",
        "The Foley-style entropy calculation changes opportunity-set restrictions."]
},indent=2)+"\n")
print("RESULTS",[(r["model"],r["trade_rate"],
    r["kl_divergence_from_money_maxent"],
    r["transaction_kl_realized_to_maxent"]) for r in rows])
