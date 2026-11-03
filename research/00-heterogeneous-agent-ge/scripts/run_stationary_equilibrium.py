from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from aiyagari import Calibration,equilibrium,save_equilibrium
p=argparse.ArgumentParser()
p.add_argument("--na",type=int,default=360)
p.add_argument("--nz",type=int,default=5)
p.add_argument("--amax",type=float,default=600.)
p.add_argument("--output",type=Path,default=ROOT/"results")
a=p.parse_args()
r=equilibrium(Calibration(na=a.na,nz=a.nz,amax=a.amax),verbose=True)
s=save_equilibrium(r,a.output)
print("RESULT",{k:s[k] for k in ("K_demand","K_supply","r","w","Y","C","gini_assets","goods_resource_error","weighted_p99_kkt_or_log_euler")})
