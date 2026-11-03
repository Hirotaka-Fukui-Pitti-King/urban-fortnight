"""Execute the original positive-matching 3x3 private-problem benchmark.

The saved initial relative value is a numerical warm start, not a solved root.
The solve reoptimizes ALL relevant continuous Nash contracts at every
nonlinear root trial and performs an independent denser final evaluation.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from private_nash_bellman import fixture_3x3, solve_private, endogenous_operator

WARM_RELATIVE_VALUE = [
    0., 2946.7179991, 3152.75508697, 3278.52358795, 3406.10697095,
    3457.64688968, 3489.92849979, 3526.98090514, 3546.06220954,
]

def run(out: Path, nq: int = 17, nx: int = 15):
    model, f = fixture_3x3()
    ans = solve_private(model, f, 2.5, np.asarray(WARM_RELATIVE_VALUE),
                        nq=nq, nx=nx, tolerance=1e-8)
    out.mkdir(parents=True, exist_ok=True)
    (out / "private_summary.json").write_text(json.dumps({
        k: v for k, v in ans.items() if not isinstance(v, np.ndarray)
    }, indent=2), encoding="utf-8")
    np.savez(out / "private_arrays.npz", value=ans["value"], y=ans["y"],
             d=ans["d"], f=f, k=model.k, m=model.m)
    with (out / "contracts.csv").open("w", newline="", encoding="utf-8") as fh:
        writer=csv.writer(fh)
        writer.writerow(["buyer","seller","quantity","nominal_payment",
                         "buyer_money","seller_capital"])
        for i in range(model.n):
            for j in range(model.n):
                if f[i] == 0 and f[j] == 0: continue
                writer.writerow([i,j,float(ans["y"][i,j]),float(ans["d"][i,j]),
                                 float(model.m[i]),float(model.k[j])])
    print(json.dumps({k:v for k,v in ans.items()
                      if k not in {"value","y","d","history"}}, indent=2))
    if not ans["converged"]:
        raise SystemExit("PRIVATE_NASH_BELLMAN_NOT_CERTIFIED")
    return ans

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"results")
    parser.add_argument("--nq",type=int,default=17)
    parser.add_argument("--nx",type=int,default=15)
    a=parser.parse_args()
    run(a.out,a.nq,a.nx)
