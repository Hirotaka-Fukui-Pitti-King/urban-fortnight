"""Pseudo-arclength continuation of the 5x5 conditional Nash--Bellman root.

Continues the *same* private problem with endogenous Nash reoptimization in
every residual. The Nash oracle is a fast candidate oracle, not certified
globally; even a full-rate root requires a separate convex Nash recheck.
No monetary clearing or stationary GE claim.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.optimize import root
from scipy.interpolate import RegularGridInterpolator

HERE = Path(__file__).resolve().parents[1]
RESEARCH = HERE.parent
for source in (HERE / "scripts", RESEARCH / "stage2g" / "src",
               RESEARCH / "stage2g" / "scripts", RESEARCH / "stage2e" / "src",
               RESEARCH / "stage2c" / "src"):
    sys.path.insert(0, str(source))
from solve_private_5x5 import root_at_match, complete_operator
from private_nash_bellman import fixture_3x3, solve_private, endogenous_operator
from solve_private import WARM_RELATIVE_VALUE
from continuous_core import ContinuousModel
from molico_grid import Calibration


def relative_residual(z, matching, model, partners, price, nq, nx):
    value = complete_operator(np.r_[0.0, z], model, partners, price,
                              float(matching), nq, nx)
    return value[1:] - value[0] - z


def correct_arc(zprevious, lprevious, zcurrent, lcurrent,
                scale, ds, model, f, price, nq, nx, maxfev):
    direction = np.r_[(zcurrent - zprevious) / scale, lcurrent - lprevious]
    direction /= np.linalg.norm(direction)
    predictor = np.r_[zcurrent + ds * direction[:-1] * scale,
                      lcurrent + ds * direction[-1]]
    calls = 0
    best = (float("inf"), predictor.copy())

    def residual(x):
        nonlocal calls, best
        z, lm = x[:-1], float(x[-1])
        if lm < -0.025 or lm > 1.3:
            return np.r_[np.ones(len(z)) * (1e4 + 1e3 * abs(lm)),
                         lm - predictor[-1]]
        rr = relative_residual(z, lm, model, f, price, nq, nx)
        arc = np.dot(direction[:-1], (z - predictor[:-1]) / scale)
        arc += direction[-1] * (lm - predictor[-1])
        calls += 1
        err = max(float(np.max(np.abs(rr))), abs(float(arc)))
        if err < best[0]:
            best = (err, x.copy())
        return np.r_[rr / 100., arc]

    sol = root(residual, predictor, method="hybr",
               options={"xtol": 1e-10, "eps": 1e-7, "maxfev": maxfev})
    checks = []
    for x in [sol.x, best[1]]:
        z, lm = x[:-1], float(x[-1])
        if not 0 <= lm <= 1.2:
            continue
        rr = relative_residual(z, lm, model, f, price, nq, nx)
        arc = np.dot(direction[:-1], (z - predictor[:-1]) / scale)
        arc += direction[-1] * (lm - predictor[-1])
        checks.append((max(float(np.max(abs(rr))), abs(float(arc))), x))
    checks.sort(key=lambda a: a[0])
    if checks:
        err, chosen = checks[0]
    else:
        err, chosen = float("inf"), predictor
    return chosen[:-1], float(chosen[-1]), dict(
        residual=err, root_success=bool(sol.success), calls=calls,
        ds=float(ds), predictor_matching=float(predictor[-1]),
        corrected_matching=float(chosen[-1]),
        tangent_matching=float(direction[-1]),
        solver_message=str(sol.message))


def run(out=HERE / "results", max_points=36, maxfev=500,
        nq=9, nx=7, ds0=.025):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    small, fs = fixture_3x3()
    base = solve_private(small, fs, 2.5, np.asarray(WARM_RELATIVE_VALUE),
                         nq=17, nx=15, maxfev=200)
    big = ContinuousModel(Calibration(nk=5, nm=5, kmax=3., mmax=2.))
    f = np.zeros(big.n)
    assert big.k[12] == 1.5 and big.m[12] == 1.
    f[12] = 1.
    interp = RegularGridInterpolator((small.kg, small.mg),
            base["value"].reshape(3, 3), bounds_error=True)
    v0 = interp(np.column_stack((big.k, big.m)))
    z = v0[1:] - v0[0]
    seeds, zs, ls = [], [], []
    for lm in [0., .05, .15, .30, .55]:
        candidate, diag = root_at_match(big, f, 2.5, z, lm, nq, nx, maxfev)
        ok = diag["relative_residual"] < 1e-7
        seeds.append(dict(diag, accepted=bool(ok)))
        print("ARC_SEED", json.dumps(seeds[-1]), flush=True)
        if not ok:
            break
        z = candidate
        zs.append(z.copy())
        ls.append(float(lm))
    trace, independent = [], {}
    source = None
    best_source = float("inf")
    if len(zs) >= 5:
        scale = np.maximum(30., np.maximum(abs(zs[-1]), abs(zs[-2])))
        ds = float(ds0)
        target_attempts = 0
        for idx in range(max_points):
            if ds < 1e-4:
                break
            zz, lm, info = correct_arc(
                zs[-2], ls[-2], zs[-1], ls[-1], scale, ds, big, f,
                2.5, nq, nx, maxfev)
            ok = info["residual"] < 1e-7
            trace.append(dict(step=idx+1, accepted=bool(ok), **info))
            print("ARC_POINT", json.dumps(trace[-1]), flush=True)
            if ok:
                zs.append(zz.copy())
                ls.append(lm)
                np.savez(out/"pseudo_arclength_last_accepted.npz",
                         relative_value=zz, matching_multiplier=lm)
                ds = min(.08, ds*1.3)
                if lm >= .90 and target_attempts < 4:
                    target_attempts += 1
                    trial, di = root_at_match(big, f, 2.5, zz, 1.,
                                              nq, nx, maxfev)
                    print("ARC_TARGET", json.dumps(di), flush=True)
                    best_source = min(best_source, di["relative_residual"])
                    if di["relative_residual"] < 1e-7:
                        source = trial
                        break
            else:
                ds *= .5
    if source is not None:
        relative = np.r_[0., source]
        raw = endogenous_operator(relative, f, 2.5, big,
                                  nq=max(17,nq), nx=max(15,nx))[0]
        value = relative + raw[0]/(1-big.p.beta)
        checked, y, d, kkt = endogenous_operator(
            value, f, 2.5, big, nq=max(23,nq), nx=max(19,nx))
        independent = dict(Bellman_sup=float(np.max(abs(checked-value))),
                           local_Nash_KKT=float(kkt),
                           positive_contracts=int(np.count_nonzero(y)))
        np.savez(out/"pseudo_arclength_candidate_5x5.npz",
                 V=value, y=y, d=d, f=f)
    result = dict(
        status=("SOURCE_RATE_CANDIDATE_UNCERTIFIED" if source is not None else
                "NO_SOURCE_RATE_ROOT_FROM_THIS_BRANCH"),
        source_rate_root_found=source is not None,
        source_rate_best_coarse_sup=(best_source if np.isfinite(best_source) else None),
        max_matching_on_traced_branch=(max(ls) if ls else None),
        turning_point_observed=any(i["tangent_matching"]<0 for i in trace
                                   if i["accepted"]), seed=seeds, arclength=trace,
        independent=independent, global_Nash_verified=False,
        fixed_price_5x5_certified=False, stationary_GE=False,
        seconds=time.monotonic()-start)
    (out/"pseudo_arclength_5x5.json").write_text(
        json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print("ARC_SUMMARY", json.dumps({k:v for k,v in result.items()
                                     if k not in ("seed","arclength")}),flush=True)
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--max-points",type=int,default=36)
    parser.add_argument("--maxfev",type=int,default=500)
    parser.add_argument("--nq",type=int,default=9)
    parser.add_argument("--nx",type=int,default=7)
    parser.add_argument("--ds",type=float,default=.025)
    opts=parser.parse_args()
    run(max_points=opts.max_points, maxfev=opts.maxfev,
        nq=opts.nq, nx=opts.nx, ds0=opts.ds)
