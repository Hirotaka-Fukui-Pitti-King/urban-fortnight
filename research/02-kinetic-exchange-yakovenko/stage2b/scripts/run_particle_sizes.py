"""Four seeds for each N at fixed prices: not a finite-population GE."""
from pathlib import Path
import sys,csv
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
from joint_model import Model
from validation import one_step_particles
m=Model();sol=m.solve_inner(4.5,.97,.65)
rows=[one_step_particles(m,sol,n=N,seed=seed)
      for N in [2500,10000,40000] for seed in [11,22,33,44]]
out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
with (out/'one_step_particles.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
for N in [2500,10000,40000]:
    values=[v['total_variation_next_distribution'] for v in rows if v['n']==N]
    print('N',N,'mean TV',sum(values)/len(values))
assert all(x['dm_money_conservation_error']==0 for x in rows)
