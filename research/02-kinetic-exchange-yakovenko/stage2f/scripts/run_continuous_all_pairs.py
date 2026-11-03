"""Run all relevant buyer/seller continuous Nash optimizations in a one-period CM-DM pilot."""
from pathlib import Path
import sys,json
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"src"))
sys.path.insert(0,str(HERE.parent/"stage2e"/"src"))
sys.path.insert(0,str(HERE.parent/"stage2c"/"src"))
from molico_grid import Calibration
from continuous_core import ContinuousModel
from source_aligned import make_CM_entrants,clear_CM_entrants
from all_pair_continuous_nash import one_step_all_relevant_continuous_nash
m=ContinuousModel(Calibration(nk=5,nm=5,kmax=3,mmax=2,y_choices=4,d_choices=5))
V=5*(m.k+m.m/3.)+.02*np.sin(m.k)+.003*np.sin(2*m.m)
entrants=make_CM_entrants(m,1.5,1.)
cm=clear_CM_entrants(m,V,entrants,price_hint=3.)
nv,next_ent,diag=one_step_all_relevant_continuous_nash(
    m,V,cm["f"],cm["price"],maxiter=100)
result=dict(status="ONE_PERIOD_CONTINUOUS_NASH_CANDIDATES_NOT_STATIONARY_GE",
             price=cm["price"],CM_money=cm["money"],
             CM_budget=cm["budget_error"],**diag)
print(json.dumps(result,indent=2))
assert abs(result["CM_money"]-1)<1e-9
assert abs(result["money_after"]-1)<1e-9
assert not result["stationary_GE"]
assert result["continuous_contracts_applied_to_actual_DM_operator"]
out=HERE/"results";out.mkdir(exist_ok=True)
(out/"continuous_all_pair_pilot.json").write_text(json.dumps(result,indent=2)+"\n")
