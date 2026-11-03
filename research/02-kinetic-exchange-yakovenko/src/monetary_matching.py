"""Discrete-time voluntary monetary exchange with endogenous kinetic distribution.

This is a constrained posted-price service/money search model. It is not a
fully nonseparable integration of monetary trading into Aiyagari saving.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.optimize import root, brentq

@dataclass(frozen=True)
class Params:
    max_tokens: int = 5
    average_tokens: float = 2.0
    beta: float = 0.96
    meeting_rate: float = 0.45
    buyer_value: float = 5.0
    seller_cost: float = 0.15
    assortativity: float = 0.0

def matching_weight(buyer, seller, prm):
    return 1 + prm.assortativity * (buyer / (prm.max_tokens or 1)) * (seller / (prm.max_tokens or 1))

def buyer_gain(V, buyer, prm):
    return prm.buyer_value + prm.beta * (V[buyer - 1] - V[buyer]) if buyer > 0 else -np.inf

def seller_gain(V, seller, prm):
    return -prm.seller_cost + prm.beta * (V[seller + 1] - V[seller]) if seller < prm.max_tokens else -np.inf

def optimal_trade(V, buyer, seller, prm):
    return buyer_gain(V, buyer, prm) >= -1e-12 and seller_gain(V, seller, prm) >= -1e-12

def flows(f, trade, prm):
    """Ordered buyer/seller meeting mass, once per period, with Poisson-like mean field."""
    n = prm.max_tokens + 1
    q = np.zeros((n, n))
    for b in range(1, n):
        for s in range(n - 1):
            if trade[b, s]:
                q[b, s] = 0.5 * prm.meeting_rate * f[b] * f[s] * matching_weight(b, s, prm)
    return q

def generator(f, trade, prm):
    """One-period transition is I+L, rows summing to one."""
    n = prm.max_tokens + 1
    L = np.zeros((n, n))
    for m in range(n):
        sell_rate = (0.5 * prm.meeting_rate *
            sum(f[b] * matching_weight(b, m, prm) * trade[b, m] for b in range(1, n))
            if m < n - 1 else 0)
        buy_rate = (0.5 * prm.meeting_rate *
            sum(f[s] * matching_weight(m, s, prm) * trade[m, s] for s in range(n - 1))
            if m > 0 else 0)
        if m < n - 1:
            L[m, m + 1] += sell_rate
        if m > 0:
            L[m, m - 1] += buy_rate
        L[m, m] -= buy_rate + sell_rate
    return L

def payoff(f, trade, prm):
    n = prm.max_tokens + 1
    u = np.zeros(n)
    for m in range(n):
        if m > 0:
            u[m] += (0.5 * prm.meeting_rate * prm.buyer_value *
                sum(f[s] * trade[m, s] * matching_weight(m, s, prm) for s in range(n - 1)))
        if m < n - 1:
            u[m] -= (0.5 * prm.meeting_rate * prm.seller_cost *
                sum(f[b] * trade[b, m] * matching_weight(b, m, prm) for b in range(1, n)))
    return u

def solve_candidate(prm, trade=None):
    """Compute the all-feasible-trades candidate and *then* verify both ICs.

    Failure of IC means this candidate is not an equilibrium; this routine
    does not silently replace it with a policy or claim general existence.
    """
    n = prm.max_tokens + 1
    if prm.meeting_rate * (1 + max(0., prm.assortativity)) > 1 + 1e-12:
        raise ValueError("A matched person cannot have meeting probability above one")
    if trade is None:
        trade = np.zeros((n, n), dtype=bool)
        trade[1:, :-1] = True
    def eq(fprefix):
        f = np.r_[fprefix, 1 - np.sum(fprefix)]
        e = generator(f, trade, prm).T @ f
        # Aggregate money and total probability are conserved exactly, so
        # n-2 independent stationarity equations plus money supply suffice.
        return np.r_[e[:n-2], np.dot(f, np.arange(n)) - prm.average_tokens]
    best = None
    for start in (np.ones(n) / n, np.linspace(1.3, .7, n) / n,
                  np.linspace(.7, 1.3, n) / n):
        r = root(eq, start[:-1], tol=1e-12)
        f = np.r_[r.x, 1 - sum(r.x)]
        if r.success and f.min() > -1e-11 and abs(f @ np.arange(n) - prm.average_tokens) < 1e-8:
            err = np.max(abs(generator(f, trade, prm).T @ f))
            if best is None or err < best[0]:
                f = np.maximum(f, 0)
                best = (err, f / f.sum())
    if best is None:
        raise RuntimeError("No valid stationary distribution in this candidate regime")
    f = best[1]
    L = generator(f, trade, prm)
    Ptrans = np.eye(n) + L
    if Ptrans.min() < -1e-13:
        raise RuntimeError("Meeting hazard violates one-meeting-per-period constraint")
    V = np.linalg.solve(np.eye(n) - prm.beta * Ptrans, payoff(f, trade, prm))
    violations = []
    for b in range(1, n):
        for s in range(n - 1):
            bg, sg = buyer_gain(V, b, prm), seller_gain(V, s, prm)
            if (trade[b, s] and min(bg, sg) < -1e-10) or (
                not trade[b, s] and bg > 1e-10 and sg > 1e-10):
                violations.append((b, s, bg, sg))
    return {"f": f, "V": V, "L": L, "trade": trade,
            "flows": flows(f, trade, prm),
            "participation_violations": violations,
            "max_stationarity_error": float(np.max(abs(L.T @ f))),
            "bellman_error": float(np.max(abs(
                V - payoff(f, trade, prm) - prm.beta * (np.eye(n) + L) @ V)))}

def diagnostics(sol, prm):
    f, V, q = sol["f"], sol["V"], sol["flows"]
    total = float(q.sum())
    change = np.zeros(len(f))
    for b in range(1, len(f)):
        for s in range(len(f)-1):
            change[b] -= q[b, s]
            change[b-1] += q[b, s]
            change[s] -= q[b, s]
            change[s+1] += q[b, s]
    entropy = -float(sum(x * np.log(x) for x in f if x > 0))
    levels = np.arange(len(f))
    def maxent(lam):
        ex = np.exp(-lam * levels)
        return ex / ex.sum()
    lam = brentq(lambda x: maxent(x) @ levels - prm.average_tokens, -30, 30)
    fme = maxent(lam)
    kl = float(sum(f[i] * np.log(f[i] / fme[i])
                   for i in range(len(f)) if f[i] > 0))
    return {**asdict(prm), "money_mass_error": float(abs(sum(f) - 1)),
            "money_conservation_error": float(abs(change @ levels)),
            "flow_balance_error": float(np.max(abs(change))),
            "stationarity_sup_error": sol["max_stationarity_error"],
            "bellman_sup_error": sol["bellman_error"],
            "participation_failures": len(sol["participation_violations"]),
            "mean_money": float(f @ levels), "money_distribution": f.tolist(),
            "money_shadow_values": V.tolist(), "trade_rate": total,
            "service_output": total, "service_consumption": total,
            "service_market_error": 0.,
            "mean_entropy": entropy, "maxent_lagrange": float(lam),
            "maxent_distribution": fme.tolist(),
            "kl_divergence_from_money_maxent": kl}

def foley_style_transaction_benchmark(sol, prm):
    """Illustrative entropy program, NOT Foley's original admissible offer sets.

    Money-level types have choices x in {-1,0,+1}, where feasible, with only
    aggregate token-market clearing. Role and matching opportunity constraints
    are purposely omitted from this comparison program.
    """
    f, n = sol["f"], len(sol["f"])
    P = np.eye(n) + sol["L"]
    x = np.array([-1, 0, 1])
    eligible = np.array([[(0 <= m + dx < n) for dx in x] for m in range(n)])
    actual = np.zeros((n, 3))
    for m in range(n):
        for j, dx in enumerate(x):
            if eligible[m, j]:
                actual[m, j] = P[m, m + dx]
    assert np.max(abs(actual.sum(axis=1) - 1)) < 1e-10
    def gibbs(pi):
        weights = np.where(eligible, np.exp(-pi * x[None, :]), 0.)
        return weights / weights.sum(axis=1, keepdims=True)
    pi = brentq(lambda v: float(np.sum(f[:,None]*gibbs(v)*x[None,:])), -30, 30)
    h = gibbs(pi)
    divergence = float(sum(f[m] * actual[m, j] *
        np.log(actual[m, j] / h[m, j]) for m in range(n)
        for j in range(3) if actual[m, j] > 0))
    return {"transaction_entropy_price": float(pi),
            "transaction_kl_realized_to_maxent": divergence,
            "transaction_market_balance": float(np.sum(f[:,None]*actual*x[None,:])),
            "transaction_entropy_distribution": h.tolist(),
            "realized_transition_transaction_distribution": actual.tolist()}


def collision_operator(f, trade, prm):
    """Exact Boltzmann gain-loss operator for feasible optimal bilateral trades."""
    q = flows(f, trade, prm)
    result = np.zeros_like(f)
    for b in range(1, len(f)):
        for s in range(len(f)-1):
            w = q[b, s]
            result[b] -= w
            result[b-1] += w
            result[s] -= w
            result[s+1] += w
    return result
