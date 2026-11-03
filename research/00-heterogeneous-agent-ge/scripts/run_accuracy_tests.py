"""Sensitivity analysis: asset grid, shock grid, and asset upper bound."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from aiyagari import Calibration,equilibrium
p=argparse.ArgumentParser()
p.add_argument("--quick",action="store_true")
p.add_argument("--output",type=Path,default=ROOT/"results")
a=p.parse_args()
cases=[(200,5,600),(360,5,600)] if a.quick else [(200,5,600),(360,5,600),(520,5,600),(360,7,600),(360,5,900)]
rows=[]
for na,nz,amax in cases:
    try:
        s=equilibrium(Calibration(na=na,nz=nz,amax=amax))["summary"]
        row={k:s[k] for k in ("na","nz","amax","r","K_demand","gini_assets",
             "ge_relative_capital_error","goods_resource_error","weighted_mean_kkt_or_log_euler",
             "weighted_p99_kkt_or_log_euler","asset_top_mass","distribution_invariance_max_error")}
        rows.append(row)
        print(row,flush=True)
    except Exception as e:
        row=dict(na=na,nz=nz,amax=amax,error=str(e))
        rows.append(row)
        print("ERROR",row,flush=True)
a.output.mkdir(exist_ok=True,parents=True)
(a.output/"accuracy_report.json").write_text(json.dumps(rows,indent=2)+"\n")
import pandas as pd
pd.DataFrame(rows).to_csv(a.output/"accuracy_report.csv",index=False)
if any("error" in row for row in rows):
    raise SystemExit("At least one convergence configuration failed")
