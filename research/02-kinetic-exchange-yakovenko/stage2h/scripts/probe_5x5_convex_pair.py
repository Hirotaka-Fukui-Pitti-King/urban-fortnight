"""Verify one 5x5 convex Nash pair separately from the unsolved private root.

The value vector is an interpolated 3x3 private root *INITIAL GUESS*, not
a 5x5 Bellman solution. A numerical global bound for its Nash subproblem
does not establish any 5x5 private or monetary equilibrium.
"""
from pathlib import Path
import json
import sys
import time
import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent
for path in (ROOT/"src",PARENT/"stage2g"/"src",PARENT/"stage2g"/"scripts",
             PARENT/"stage2e"/"src",PARENT/"stage2c"/"src"):
    sys.path.insert(0,str(path))
from convex_nash import solve_pair, enumerate_triangles
from private_nash_bellman import fixture_3x3, solve_private
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import cm_opt, ContinuousModel
from molico_grid import Calibration, g
from nash_global_bounds import bound_nash


def run(folder=ROOT/"results"):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    small,fs=fixture_3x3()
    baseline=solve_private(small,fs,2.5,
                           np.asarray(WARM_RELATIVE_VALUE,dtype=float),
                           nq=17,nx=15,maxfev=200)
    big=ContinuousModel(Calibration(nk=5,nm=5,kmax=3.,mmax=2.))
    interpolator=RegularGridInterpolator(
         (small.kg,small.mg), baseline["value"].reshape(3,3),bounds_error=True)
    V=interpolator(np.column_stack((big.k,big.m)))
    pair=12
    t0=time.monotonic()
    candidate=solve_pair(big,V,2.5,pair,pair)
    tconv=time.monotonic()-t0
    p=big.p
    wb=(1-p.delta)*big.k[pair]+big.m[pair]/2.5
    W=lambda wealth:float(cm_opt(
       wealth,2.5,big.k,big.m,V,big.edges,p.beta,p.b,p.eta)[0])
    cost=lambda y:float(g(y,big.k[pair],p.alpha,p.A))
    t1=time.monotonic()
    independent=bound_nash(
        W,cost,wb,wb,big.m[pair]/2.5,p.A*big.k[pair]**p.alpha,
        p.theta,initial=((candidate.y,candidate.d/2.5)
                         if candidate.y>0 else None),
        log_gap_tolerance=1e-3,max_boxes=100000)
    report=dict(
        status="5x5_NASH_ONLY_WITH_INTERPOLATED_VALUE_GUESS",
        grid=[5,5],buyer=pair,seller=pair,price=2.5,
        baseline_3x3_Bellman_sup=baseline["bellman_sup"],
        value_5x5_source="3x3 linear interpolation, not re-solved",
        triangles=len(enumerate_triangles(5,5)),
        triangle_pairs_considered=candidate.triangles_considered,
        triangle_pairs_pruned=candidate.triangles_pruned,
        convex_subproblems_solved=candidate.triangles_solved,
        convex_successes=candidate.successes,
        convex_dcp_no_reported_solver_error=bool(candidate.dcp_pass),
        quantity=candidate.y,nominal_payment=candidate.d,
        convex_log_nash=candidate.log_nash,
        independent_lower_log_nash=independent.lower_log_nash,
        independent_upper_log_nash=independent.upper_log_nash,
        independent_global_gap=independent.gap_log_nash,
        independent_bound_reached=bool(independent.bounded_to_tolerance),
        runtime_convex_s=tconv,runtime_bound_s=time.monotonic()-t1,
        runtime_total_s=time.monotonic()-start,
        certified_5x5_private_root=False,
        stationary_GE=False)
    (folder/"5x5_convex_pair_probe.json").write_text(
         json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("FIVE_PAIR",json.dumps(report),flush=True)
    assert candidate.y>0 and candidate.d>0
    assert candidate.triangles_solved>0 and candidate.dcp_pass
    assert independent.bounded_to_tolerance
    assert candidate.log_nash<=independent.upper_log_nash+1e-8
    assert independent.upper_log_nash-candidate.log_nash<.00101
    return report


if __name__=="__main__":
    run()
