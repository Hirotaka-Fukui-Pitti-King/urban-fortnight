from pathlib import Path
import sys,argparse
ROOT=Path(__file__).resolve().parents[1]
MODELPATH=ROOT.parent/"00-heterogeneous-agent-ge"/"src"
sys.path[:0]=[str(MODELPATH),str(ROOT/"src")]
from aiyagari import Calibration,equilibrium
from particles import compare_stationary,save_agent_results
p=argparse.ArgumentParser()
p.add_argument("--quick",action="store_true")
p.add_argument("--output",type=Path,default=ROOT/"results")
a=p.parse_args()
cal=Calibration(na=200 if a.quick else 360,amax=600.)
ref=equilibrium(cal)
Ns=[1000,4000] if a.quick else [2500,10000,40000]
seeds=[101,202] if a.quick else [101,202,303]
rows=[]
for N in Ns:
    for seed in seeds:
        r=compare_stationary(ref,N,seed,burnin=550 if a.quick else 1400,
                             sample_periods=40 if a.quick else 150)
        print(N,seed,"Kerror",r["K_error"],"W1",r["terminal_asset_wasserstein"],flush=True)
        rows.append(r)
save_agent_results(rows,a.output)
print("EXPECTED_K",ref["summary"]["K_demand"],"EMPIRICAL",
      [(n,round(sum(x["K_mean"] for x in rows if x["n_agents"]==n)/len(seeds),6)) for n in Ns])
