"""Price-region feasibility audit, not an equilibrium-existence test.

The agent's inner fixed point may fail or concentrate on the asset-grid ceiling.
Never pass unconverged inner solutions to an outer market-clearing root solver.
"""
from pathlib import Path
import json,sys
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
from joint_model import Model
m=Model()
rows=[]
for K in (1.0,2.0,2.8,3.3,4.0):
    info=m.solve_inner(K,.94,.8)['info']
    keys=("converged","iterations","value_residual","distribution_residual",
          "capital","money","labor","capital_price_consistency",
          "labor_price_consistency","money_supply_excess","max_boundary_asset_mass")
    row={key:info[key] for key in keys}
    row.update(K_price_guess=K,L_price_guess=.94,real_token_value=.8)
    row["equilibrium_accepted"]=bool(info["converged"]
         and abs(info["capital_price_consistency"]/K)<1e-6
         and abs(info["labor_price_consistency"])<1e-6
         and abs(info["money_supply_excess"])<1e-6
         and info["max_boundary_asset_mass"]<.01)
    rows.append(row)
if not any(x["max_boundary_asset_mass"]>.9 for x in rows):
    raise RuntimeError("Expected grid-boundary warning was not reproduced")
if not any(not x["converged"] for x in rows):
    raise RuntimeError("Expected nonconvergence warning was not reproduced")
if any(x["equilibrium_accepted"] for x in rows):
    raise RuntimeError("Exploratory price candidate cannot be misreported as GE")
folder=HERE/"results";folder.mkdir(exist_ok=True,parents=True)
(folder/"ge_admissibility_scan.json").write_text(
    json.dumps(rows,indent=2,default=lambda x:x.item())+"\n")
print("Price region checked; some inner points fail and asset-grid clipping is severe.")
for x in rows:
    print(x["K_price_guess"],"inner=",x["converged"],
          "Ksup=",round(x["capital"],5),
          "top_mass=",round(x["max_boundary_asset_mass"],5))
