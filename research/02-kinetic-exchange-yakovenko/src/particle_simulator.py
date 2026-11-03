"""Finite-N random bilateral meetings matching the optimal discrete kinetic operator."""
from __future__ import annotations
import numpy as np
from numba import njit
from scipy.stats import wasserstein_distance

@njit(cache=True)
def _paths(initial, meet_prob, trade, burnin, measure_every, measure_count, seed):
    np.random.seed(seed)
    n = len(initial); M = trade.shape[0] - 1
    money = initial.copy()
    inds = np.arange(n)
    hist = np.zeros(M + 1)
    service = 0
    observed = 0
    for t in range(burnin + measure_every * measure_count):
        np.random.shuffle(inds)
        for q in range(0, n - 1, 2):
            b, s = inds[q], inds[q + 1]
            mb, ms = money[b], money[s]
            if trade[mb, ms] and np.random.random() < meet_prob[mb, ms]:
                money[b] -= 1
                money[s] += 1
                if t >= burnin:
                    service += 1
        if t >= burnin and (t - burnin) % measure_every == 0:
            for i in range(n):
                hist[money[i]] += 1
            observed += 1
    return money, hist / (n * observed), service / (n * measure_every * measure_count)

def simulate(prm, sol, n_agents, seed, burnin=1200, measure_count=20, measure_every=20):
    if n_agents % 2:
        raise ValueError("N must be even")
    if abs(prm.average_tokens - round(prm.average_tokens)) > 1e-12:
        raise ValueError("Simulation harness requires integer per-capita token supply")
    rng = np.random.default_rng(seed + 100000)
    f = sol["f"]
    money = rng.choice(len(f), size=n_agents, p=f).astype(np.int64)
    discrepancy = int(round(prm.average_tokens * n_agents) - money.sum())
    for _ in range(abs(discrepancy)):
        if discrepancy > 0:
            choices = np.flatnonzero(money < prm.max_tokens)
            money[rng.choice(choices)] += 1
        else:
            choices = np.flatnonzero(money > 0)
            money[rng.choice(choices)] -= 1
    assert money.sum() == round(prm.average_tokens * n_agents)
    probs = np.zeros_like(sol["flows"])
    for b in range(len(f)):
        for s in range(len(f)):
            probs[b,s] = prm.meeting_rate * (
                1 + prm.assortativity * (b/prm.max_tokens)*(s/prm.max_tokens))
    if probs.max() > 1 + 1e-13:
        raise ValueError("Meeting probability exceeds one")
    terminal, hist, trade_rate = _paths(
        money, probs, sol["trade"], burnin, measure_every, measure_count, seed)
    return {"n_agents": int(n_agents), "seed": int(seed),
            "burnin": int(burnin), "measure_count": int(measure_count),
            "measure_every": int(measure_every), "money_mean": float(terminal.mean()),
            "money_supply_error": float(terminal.sum()-prm.average_tokens*n_agents),
            "terminal_mass": (np.bincount(terminal,minlength=len(f))/n_agents).tolist(),
            "average_mass": hist.tolist(),
            "average_mass_L1": float(sum(abs(hist-f))),
            "average_mass_W1": float(wasserstein_distance(
                np.arange(len(f)),np.arange(len(f)),u_weights=hist,v_weights=f)),
            "service_trade_rate": float(trade_rate),
            "theoretical_service_trade_rate": float(sol["flows"].sum()),
            "service_trade_error": float(trade_rate-sol["flows"].sum())}
