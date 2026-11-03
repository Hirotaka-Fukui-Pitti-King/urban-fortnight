"""Fixed-price simulation with explicitly failed general-equilibrium conditions."""
from pathlib import Path
import json,sys,time,argparse
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from joint_model import Model,Params
from validation import check_nash,check_kinetic,one_step_particles

parser=argparse.ArgumentParser()
parser.add_argument('--pop',type=int,default=10000)
parser.add_argument('--no-particles',action='store_true')
parser.add_argument('--output',type=Path,default=HERE/'results')
args=parser.parse_args()
p=Params();m=Model(p);start=time.perf_counter()
s=m.solve_inner(4.5,.97,.65)
report={'status':'FIXED_PRICE_JOINT_DP_AND_BARGAINING_ONLY_NOT_GENERAL_EQUILIBRIUM',
        'calibration':vars(p),
        'fixed_price_guess':{'K_guess':4.5,'L_guess':.97,'phi':.65},
        'computed':s['info'],'nash':check_nash(m,s),
        'kinetic':check_kinetic(m,s)}
if not args.no_particles:
    report['particles']=[one_step_particles(m,s,n=args.pop,seed=seed)
                         for seed in (11,22,33,44)]
report['execution_seconds']=time.perf_counter()-start
report['economic_warnings']=[
    'The computed capital, labor and nominal-money excess demands are NOT zero.',
    'Logit portfolios optimize over discrete actions with Gumbel taste shocks, not the deterministic Aiyagari Euler problem.',
    'Portfolio taste shocks themselves create money demand without trading: money essentiality is NOT established.',
    'No full GE, money-price equilibrium, continuous bargaining FOCs, or complete market clearing.',
    'Nash bargaining maximizes a discrete q,d contract menu, not the continuous contract set.']
args.output.mkdir(parents=True,exist_ok=True)
(args.output/'fixed_price_diagnostics.json').write_text(
    json.dumps(report,indent=2,default=float)+'\n')
np.savetxt(args.output/'fixed_price_distribution.csv',s['f'],
           delimiter=',',header='probability',comments='')
print(json.dumps({k:report[k] for k in ('status','computed','nash','kinetic')},
                 indent=2,default=float))
