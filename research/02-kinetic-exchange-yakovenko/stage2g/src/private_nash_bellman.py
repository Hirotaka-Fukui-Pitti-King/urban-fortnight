"""Continuous Nash--Bellman fixed-price solver (Molico--Zhang eqs. 1--8).

Exact-on-piecewise-affine-grid CM portfolio optimization is imported from
Stage 2-E. The original continuous contract domain is 0 <= d <= m_b and
0 <= y < A*k_s**alpha (labor l < 1, disutility divergent at l=1).
The joint private fixed point is solved independently of money clearing.
No claim of continuous-space global optimality or stationary GE is made.

The grid search is an initialization/independent lower bound. Binding-payment
contracts are polished using the quantity FOC; interior contracts use both
FOCs. Every trial evaluation solves Nash anew, including the final residual.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numba import njit
from scipy.optimize import root, brentq

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "stage2c" / "src"))
sys.path.insert(0, str(BASE / "stage2e" / "src"))
from molico_grid import Calibration, g
from continuous_core import ContinuousModel, cm_opt


@njit(cache=True)
def _W(w, price, k, m, v, edges, beta, b, eta):
    return cm_opt(w, price, k, m, v, edges, beta, b, eta)[0]


@njit(cache=True)
def _nash_log(q, x, wb, ws, base_b, base_s, ks, price, k, m,
              v, edges, beta, b, eta, alpha, A, theta):
    if q <= 0 or x <= 0 or x >= q:
        return -1e250
    cap = A * ks ** alpha
    if q >= cap:
        return -1e250
    bg = _W(wb + q - x, price, k, m, v, edges, beta, b, eta) - base_b
    sg = (_W(ws + x, price, k, m, v, edges, beta, b, eta) -
          base_s - g(q, ks, alpha, A))
    if bg <= 1e-12 or sg <= 1e-12:
        return -1e250
    return theta * np.log(bg) + (1 - theta) * np.log(sg)


@njit(cache=True)
def _payment_profile(q, mb_real, wb, ws, B0, S0, ks, price, k, m,
                     v, edges, beta, b, eta, alpha, A, theta, nx):
    xmax = min(mb_real, q)
    if xmax <= 0:
        return -1e250, 0.
    values = np.empty(nx)
    best = -1e250
    best_x = 0.
    for j in range(nx):
        x = xmax * j / (nx - 1)
        val = _nash_log(q, x, wb, ws, B0, S0, ks, price, k, m,
                        v, edges, beta, b, eta, alpha, A, theta)
        values[j] = val
        if val > best:
            best, best_x = val, x
    gr = .6180339887498949
    for j in range(1, nx - 1):
        if values[j] <= -1e200 or values[j] < values[j - 1] or values[j] < values[j + 1]:
            continue
        lo = xmax * (j - 1) / (nx - 1)
        hi = xmax * (j + 1) / (nx - 1)
        a = hi - gr * (hi - lo)
        c = lo + gr * (hi - lo)
        va = _nash_log(q, a, wb, ws, B0, S0, ks, price, k, m,
                       v, edges, beta, b, eta, alpha, A, theta)
        vc = _nash_log(q, c, wb, ws, B0, S0, ks, price, k, m,
                       v, edges, beta, b, eta, alpha, A, theta)
        for _ in range(35):
            if va > vc:
                hi, c, vc = c, a, va
                a = hi - gr * (hi - lo)
                va = _nash_log(q, a, wb, ws, B0, S0, ks, price, k, m,
                               v, edges, beta, b, eta, alpha, A, theta)
            else:
                lo, a, va = a, c, vc
                c = lo + gr * (hi - lo)
                vc = _nash_log(q, c, wb, ws, B0, S0, ks, price, k, m,
                               v, edges, beta, b, eta, alpha, A, theta)
        if va > best:
            best, best_x = va, a
        if vc > best:
            best, best_x = vc, c
    return best, best_x


@njit(cache=True)
def nash_candidate(i, j, price, k, m, v, edges, beta, b, eta,
                   alpha, A, theta, delta, nq=17, nx=13):
    if m[i] <= 1e-14 or k[j] <= 1e-14:
        return 0., 0., -1e250
    cap = A * k[j] ** alpha
    wb = (1 - delta) * k[i] + m[i] / price
    ws = (1 - delta) * k[j] + m[j] / price
    B0 = _W(wb, price, k, m, v, edges, beta, b, eta)
    S0 = _W(ws, price, k, m, v, edges, beta, b, eta)
    mb_real = m[i] / price
    qvals = np.empty(nq)
    prof = np.empty(nq)
    best, bq, bx = -1e250, 0., 0.
    for z in range(nq):
        qvals[z] = cap * ((z + 1.) / (nq + 1.)) ** 2
        val, x = _payment_profile(qvals[z], mb_real, wb, ws, B0, S0, k[j],
                                  price, k, m, v, edges, beta, b, eta,
                                  alpha, A, theta, nx)
        prof[z] = val
        if val > best:
            best, bq, bx = val, qvals[z], x
    if best <= -1e200:
        return 0., 0., -1e250
    gr = .6180339887498949
    for z in range(nq):
        if prof[z] <= -1e200:
            continue
        if z and prof[z] < prof[z - 1]:
            continue
        if z + 1 < nq and prof[z] < prof[z + 1]:
            continue
        lo = 0. if z == 0 else qvals[z - 1]
        hi = cap * (1. - 1e-12) if z == nq - 1 else qvals[z + 1]
        a = hi - gr * (hi - lo)
        c = lo + gr * (hi - lo)
        va, xa = _payment_profile(a, mb_real, wb, ws, B0, S0, k[j],
                                  price, k, m, v, edges, beta, b, eta,
                                  alpha, A, theta, nx)
        vc, xc = _payment_profile(c, mb_real, wb, ws, B0, S0, k[j],
                                  price, k, m, v, edges, beta, b, eta,
                                  alpha, A, theta, nx)
        for _ in range(31):
            if va > vc:
                hi, c, vc, xc = c, a, va, xa
                a = hi - gr * (hi - lo)
                va, xa = _payment_profile(a, mb_real, wb, ws, B0, S0, k[j],
                                           price, k, m, v, edges, beta, b, eta,
                                           alpha, A, theta, nx)
            else:
                lo, a, va, xa = a, c, vc, xc
                c = lo + gr * (hi - lo)
                vc, xc = _payment_profile(c, mb_real, wb, ws, B0, S0, k[j],
                                           price, k, m, v, edges, beta, b, eta,
                                           alpha, A, theta, nx)
        if va > best:
            best, bq, bx = va, a, xa
        if vc > best:
            best, bq, bx = vc, c, xc
    return bq, bx * price, best


@njit(cache=True)
def nash_grad(q, d, i, j, price, k, m, v, edges, beta, b, eta,
              alpha, A, theta, delta):
    cap = A * k[j] ** alpha
    if q <= 0 or q >= cap:
        return np.nan, np.nan
    wb = (1 - delta) * k[i] + m[i] / price
    ws = (1 - delta) * k[j] + m[j] / price
    x = d / price
    B0 = cm_opt(wb, price, k, m, v, edges, beta, b, eta)[0]
    S0 = cm_opt(ws, price, k, m, v, edges, beta, b, eta)[0]
    bv, _, _, cb = cm_opt(wb + q - x, price, k, m, v, edges, beta, b, eta)
    sv, _, _, cs = cm_opt(ws + x, price, k, m, v, edges, beta, b, eta)
    ell = (q / cap) ** (1 / (1 - alpha))
    gy = ell / (q * (1 - alpha) * (1 - ell) ** 2)
    BG = bv - B0
    SG = sv - S0 - ell / (1 - ell)
    if BG <= 0 or SG <= 0:
        return np.nan, np.nan
    wb_prime = (cb + b) ** (-eta)
    ws_prime = (cs + b) ** (-eta)
    return (theta * wb_prime / BG - (1 - theta) * gy / SG,
            -theta * wb_prime / BG + (1 - theta) * ws_prime / SG)


def nash_score(q, d, i, j, model, v, price):
    p = model.p
    if not (q > 0 and 0 < d <= model.m[i] and q < p.A * model.k[j] ** p.alpha):
        return -np.inf
    wb = (1 - p.delta) * model.k[i] + model.m[i] / price
    ws = (1 - p.delta) * model.k[j] + model.m[j] / price
    return float(_nash_log(q, d / price, wb, ws,
                          _W(wb, price, model.k, model.m, v, model.edges, p.beta, p.b, p.eta),
                          _W(ws, price, model.k, model.m, v, model.edges, p.beta, p.b, p.eta),
                          model.k[j], price, model.k, model.m, v, model.edges, p.beta,
                          p.b, p.eta, p.alpha, p.A, p.theta))


def nash_polish(i, j, q, d, model, v, price):
    p = model.p
    if q <= 0:
        return 0., 0., 0.
    cap = p.A * model.k[j] ** p.alpha
    def grad(qq, dd):
        return nash_grad(qq, dd, i, j, price, model.k, model.m, v,
                         model.edges, p.beta, p.b, p.eta, p.alpha,
                         p.A, p.theta, p.delta)
    old = nash_score(q, d, i, j, model, v, price)
    newq, newd = q, d
    if d >= model.m[i] * (1 - 1e-7):
        # Active payment constraint. Search a *local feasible* FOC bracket.
        for width in (1e-4, 1e-5, 1e-6, 1e-7):
            low = max(1e-10, q - width * cap)
            high = min((1 - 1e-10) * cap, q + width * cap)
            a, bder = grad(low, d)[0], grad(high, d)[0]
            if np.isfinite(a) and np.isfinite(bder) and a * bder < 0:
                newq = brentq(lambda qq: grad(qq, d)[0], low, high,
                              xtol=1e-14, rtol=1e-14)
                break
    else:
        def conditions(z):
            if not (0 < z[0] < cap and 0 < z[1] < model.m[i]):
                return np.array([1e6, 1e6])
            a, bder = grad(*z)
            if not np.isfinite(a + bder):
                return np.array([1e6, 1e6])
            return np.array([a, bder])
        fit = root(conditions, [q, d], method="hybr",
                   options={"xtol": 1e-12, "eps": 1e-8, "maxfev": 100})
        if np.isfinite(fit.x).all() and max(abs(conditions(fit.x))) < 1e-6:
            newq, newd = map(float, fit.x)
    if nash_score(newq, newd, i, j, model, v, price) + 1e-10 < old:
        newq, newd = q, d
    gy, gx = grad(newq, newd)
    kkt = abs(gy) if np.isfinite(gy) else np.inf
    if newd < model.m[i] - 1e-7:
        kkt = max(kkt, abs(gx))
    else:
        kkt = max(kkt, max(0., -gx))
    return float(newq), float(newd), float(kkt)


@njit(cache=True)
def _frozen_operator(v, f, price, k, m, edges, beta, b, eta,
                     alpha, A, delta, ntypes, y, d):
    n = len(v)
    outside = np.empty(n)
    for i in range(n):
        outside[i] = _W((1 - delta) * k[i] + m[i] / price,
                        price, k, m, v, edges, beta, b, eta)
    result = outside.copy()
    for i in range(n):
        for j in range(n):
            if f[j] > 0 and y[i, j] > 0:
                wb = (1 - delta) * k[i] + m[i] / price
                gain = _W(wb + y[i, j] - d[i, j] / price, price,
                          k, m, v, edges, beta, b, eta) - outside[i]
                result[i] += f[j] * gain / ntypes
            if f[j] > 0 and y[j, i] > 0:
                ws = (1 - delta) * k[i] + m[i] / price
                gain = (_W(ws + d[j, i] / price, price,
                           k, m, v, edges, beta, b, eta) -
                        outside[i] - g(y[j, i], k[i], alpha, A))
                result[i] += f[j] * gain / ntypes
    return result


def endogenous_operator(V, f, price, model, nq=17, nx=15):
    p = model.p
    n = model.n
    if abs(f.sum() - 1) > 1e-12 or np.min(f) < 0:
        raise ValueError("invalid partner distribution")
    # Avoid cancellation in W(new) - W(old). Translation affects only level.
    offset = float(max(V))
    v = np.asarray(V) - offset
    y = np.zeros((n, n))
    d = np.zeros((n, n))
    max_kkt = 0.
    for i in range(n):
        for j in range(n):
            if f[i] <= 1e-15 and f[j] <= 1e-15:
                continue
            q, pay, _ = nash_candidate(i, j, price, model.k, model.m,
                                       v, model.edges, p.beta, p.b, p.eta,
                                       p.alpha, p.A, p.theta, p.delta, nq, nx)
            if q <= 0:
                continue
            q, pay, kkt = nash_polish(i, j, q, pay, model, v, price)
            y[i, j], d[i, j] = q, pay
            max_kkt = max(max_kkt, kkt)
    val = (_frozen_operator(v, f, price, model.k, model.m, model.edges,
                            p.beta, p.b, p.eta, p.alpha, p.A,
                            p.delta, p.Ntypes, y, d) + p.beta * offset)
    return val, y, d, max_kkt


def solve_private(model, f, price, initial_V, nq=17, nx=15, tolerance=1e-8,
                  maxfev=300):
    v0 = np.asarray(initial_V, dtype=float).copy()
    v0 -= v0[0]
    history = []
    def residual(z):
        v = np.r_[0., z]
        val, _, _, _ = endogenous_operator(v, f, price, model, nq, nx)
        r = val - val[0] - v
        history.append(float(np.max(np.abs(r))))
        return r[1:]
    outcome = root(residual, v0[1:], method="hybr",
                   options={"xtol": 1e-12, "eps": 1e-8, "maxfev": maxfev})
    relative = np.r_[0., outcome.x]
    raw, y, d, max_kkt = endogenous_operator(relative, f, price, model, nq, nx)
    # General translation covariance T(v+C)=T(v)+beta*C.
    level = raw[0] / (1 - model.p.beta)
    value = relative + level
    check, yy, dd, independent_kkt = endogenous_operator(value, f, price, model,
                                                          nq=max(nq, 23), nx=max(nx, 19))
    full_res = float(np.max(np.abs(check - value)))
    return {"converged": bool(full_res < tolerance and independent_kkt < 1e-6),
            "root_success": bool(outcome.success), "message": str(outcome.message),
            "bellman_sup": full_res, "nash_kkt_max": float(independent_kkt),
            "function_evaluations": len(history), "history": history,
            "value": value, "y": yy, "d": dd,
            "positive_contracts": int(np.count_nonzero(yy)),
            "grid": [model.p.nk, model.p.nm], "price": float(price),
            "partner_states": int(np.count_nonzero(f))}


def fixture_3x3():
    model = ContinuousModel(Calibration(nk=3, nm=3, kmax=3., mmax=2.))
    f = np.zeros(model.n)
    f[model.n // 2] = 1.
    return model, f
