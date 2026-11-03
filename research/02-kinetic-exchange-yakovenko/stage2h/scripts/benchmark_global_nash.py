"""Execute small-grid source-aligned convex Nash experiments.

Requires CVXPY and Clarabel. This script reports the convex-branch
optimal candidate, independently evaluated within the source Bellman W,
and a comparison to the existing Stage 2-G global rectangle certificate.
"""
from pathlib import Path
import sys,json,time
import numpy as np

HERE=Path(__file__).resolve().parents[1]
RESEARCH=HERE.parent
for path in (HERE/"src",RESEARCH/"stage2g"/"src",
             RESEARCH/"stage2c"/"src",RESEARCH/"stage2e"/"src",
             RESEARCH/"stage2g"/"scripts"):
    sys.path.insert(0,str(path))
from convex_nash import solve_pair,enumerate_triangles
from private_nash_bellman import fixture_3x3,solve_private
from solve_private import WARM_RELATIVE_VALUE
from nash_global_bounds import bound_nash
from continuous_core import cm_opt
from molico_grid import g


def run():
    output=HERE/"results"
    output.mkdir(parents=True,exist_ok=True)
    model,f=fixture_3x3()
    base=solve_private(model,f,2.5,np.asarray(WARM_RELATIVE_VALUE),
                       nq=17,nx=15)
    V=base["value"]
    print("BASE_PRIVATE",base["bellman_sup"],flush=True)
    report={"grid":[3,3],"num_triangles":len(enumerate_triangles(3,3)),
            "baseline_bellman":base["bellman_sup"]}
    tic=time.monotonic()
    solution=solve_pair(model,V,2.5,4,4)
    print("CONVEX_RESULT",solution,flush=True)
    p=model.p
    wb=(1-p.delta)*model.k[4]+model.m[4]/2.5
    ws=wb
    W=lambda w:float(cm_opt(w,2.5,model.k,model.m,V,model.edges,p.beta,p.b,p.eta)[0])
    cost=lambda y:float(g(y,model.k[4],p.alpha,p.A))
    upper=bound_nash(W,cost,wb,ws,model.m[4]/2.5,
                     p.A*model.k[4]**p.alpha,p.theta,
                     initial=((solution.y,solution.d/2.5)
                               if solution.y>0 else None),
                     log_gap_tolerance=1e-4,max_boxes=100000)
    report.update(buyer=4,seller=4,
        convex_quantity=solution.y,convex_payment=solution.d,
        convex_log_nash=solution.log_nash,
        convex_triangles_considered=solution.triangles_considered,
        convex_triangles_pruned=solution.triangles_pruned,
        convex_triangles_solved=solution.triangles_solved,
        convex_successful_subproblems=solution.successes,
        monotone_lower_log_nash=upper.lower_log_nash,
        monotone_upper_log_nash=upper.upper_log_nash,
        monotone_log_gap=upper.gap_log_nash,
        convex_improvement_vs_branch_lower=solution.log_nash-upper.lower_log_nash,
        global_nash_optimality_with_interval_rounding=False,
        wall_seconds=time.monotonic()-tic,stationary_GE=False)
    (output/"convex_nash_pilot.json").write_text(json.dumps(report,indent=2)+"\n")
    print("CONVEX_PILOT",json.dumps(report),flush=True)
    assert solution.y>0, report
    assert solution.triangles_solved>0, report
    assert abs(solution.log_nash-upper.lower_log_nash)<1e-5, report
    assert upper.gap_log_nash<1.01e-4, report
    return report


if __name__=="__main__":
    run()
