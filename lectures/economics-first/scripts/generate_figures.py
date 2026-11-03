"""Pedagogical reproductions of Aiyagari EGM, finite-N Ising, and token matching.

Usage:
    python lectures/economics-first/scripts/generate_figures.py \
        --output lectures/economics-first/figures

Requires numpy, scipy, matplotlib. Numerical tests are economic-model-specific;
none of the calibrations are original-paper replications.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, root
from scipy.special import gammaln, logsumexp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"svg.fonttype": "path", "mathtext.fontset": "dejavusans", "font.size": 10, "svg.hashsalt": "econ-first-stable-v1"})


def egm(r, a, z, trans, beta=.96, gamma=2., alpha=.36, delta=.08):
    kd = (alpha / (r + delta)) ** (1 / (1 - alpha))
    wage = (1 - alpha) * kd ** alpha
    c = np.maximum(.001, .35 * ((1 + r) * a[:, None] + wage * z[None, :]))
    for _ in range(2500):
        c_next = np.empty_like(c)
        for iz, zi in enumerate(z):
            emu = (c ** (-gamma)) @ trans[iz]
            c_end = (beta * (1 + r) * emu) ** (-1 / gamma)
            a_end = (c_end + a - wage * zi) / (1 + r)
            c_next[:, iz] = np.interp(a, a_end, c_end)
            constraint = a < a_end[0]
            c_next[constraint, iz] = (1 + r) * a[constraint] + wage * zi - a[0]
        error = np.max(np.abs(c_next - c))
        c = .75 * c_next + .25 * c
        if error < 2e-10:
            break
    else:
        raise RuntimeError("EGM failed to converge")
    resources = (1 + r) * a[:, None] + wage * z
    # If the finite savings grid binds at its upper edge, the realized budget
    # must be recomputed. Clipping a' without updating c violates feasibility.
    ap = np.clip(resources - c, a[0], a[-1])
    c = resources - ap
    if np.min(c) <= 0 or np.max(np.abs(c + ap - resources)) > 1e-10:
        raise RuntimeError("EGM budget or consumption feasibility failed")
    return c, ap, kd, wage


def lottery(ap, a):
    lower = np.maximum(0, np.minimum(len(a) - 2,
                                      np.searchsorted(a, ap, side="right") - 1))
    upper = lower + 1
    weight = np.clip((ap - a[lower]) / (a[upper] - a[lower]), 0, 1)
    return lower, upper, weight


def forward(mu, lower, upper, weight, trans):
    out = np.zeros_like(mu)
    for iz in range(len(trans)):
        for jz in range(len(trans)):
            np.add.at(out[:, jz], lower[:, iz],
                      mu[:, iz] * (1 - weight[:, iz]) * trans[iz, jz])
            np.add.at(out[:, jz], upper[:, iz],
                      mu[:, iz] * weight[:, iz] * trans[iz, jz])
    return out


def stationary(ap, a, trans):
    operator = lottery(ap, a)
    mu = np.ones((len(a), len(trans))) / (len(a) * len(trans))
    for _ in range(20000):
        nxt = forward(mu, *operator, trans)
        if np.max(abs(nxt - mu)) < 3e-11:
            return nxt, operator
        mu = nxt
    raise RuntimeError("invariant wealth distribution failed")


def aiyagari_policy_diagnostics(r, a, z, trans, c, ap, beta=.96, gamma=2., alpha=.36, delta=.08):
    """Audit budget, Euler/KKT inequalities, and the artificial upper asset cap.

    EGM Euler checks use interpolation of next-period c at the chosen a'.
    For the lower (upper) active bound, the correct Euler inequality is
    u'(c) >= (<=) beta*(1+r)*E[u'(c')].
    """
    kd = (alpha/(r+delta))**(1/(1-alpha))
    wage = (1-alpha)*kd**alpha
    resources=(1+r)*a[:,None]+wage*z[None,:]
    budget=float(np.max(np.abs(c+ap-resources)))
    rhs=np.zeros_like(c)
    for iz in range(len(z)):
        for jz in range(len(z)):
            c_future=np.interp(ap[:,iz],a,c[:,jz])
            rhs[:,iz]+=trans[iz,jz]*np.maximum(c_future,1e-14)**(-gamma)
    rhs*=beta*(1+r)
    lhs=c**(-gamma)
    residual=(lhs-rhs)/np.maximum(np.maximum(lhs,rhs),1e-14)
    lower=ap<=a[0]+1e-8
    upper=ap>=a[-1]-1e-8
    interior=~(lower|upper)
    violations=np.zeros_like(residual)
    violations[interior]=np.abs(residual[interior])
    violations[lower]=np.maximum(-residual[lower],0)
    violations[upper]=np.maximum(residual[upper],0)
    if budget>1e-9 or np.any(ap<a[0]-1e-10) or np.any(ap>a[-1]+1e-10):
        raise RuntimeError("Aiyagari policy violates budget or asset feasibility")
    return {"budget_sup":budget, "euler_kkt_sup":float(violations.max()),
            "euler_interior_sup":float(np.max(abs(residual[interior]))) if interior.any() else None,
            "euler_lower_violation":float(np.max(np.maximum(-residual[lower],0))) if lower.any() else 0.,
            "euler_upper_violation":float(np.max(np.maximum(residual[upper],0))) if upper.any() else 0.,
            "upper_cap_nodes":int(upper.sum()), "lower_cap_nodes":int(lower.sum()),
            "upper_cap_mask":upper}


def aiyagari_figures(out):
    a = 30 * np.linspace(0, 1, 240) ** 1.7
    z = np.array([.7, 1.3])
    trans = np.array([[.94, .06], [.06, .94]])
    def excess(r):
        _, ap, kd, _ = egm(r, a, z, trans)
        mu, _ = stationary(ap, a, trans)
        return float(np.sum(a[:, None] * mu) - kd)
    r = brentq(excess, .005, 1 / .96 - 1 - .0005, xtol=2e-7)
    _, ap, kd, wage = egm(r, a, z, trans)
    mu, op = stationary(ap, a, trans)
    k = float(np.sum(a[:, None] * mu))
    diagnostics=aiyagari_policy_diagnostics(r,a,z,trans,_,ap)
    upper_mass=float(mu[diagnostics.pop("upper_cap_mask")].sum())
    if abs(k-kd) > .005 or abs(mu.sum()-1)>1e-8 or upper_mass>1e-4:
        raise RuntimeError("Aiyagari market clearing, mass, or upper-grid cap failed")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for iz, zi in enumerate(z):
        ax.plot(a, ap[:, iz], label=rf"$g(a,z={zi:.1f})$")
    ax.plot(a, a, "--", linewidth=1, label=r"$a'=a$")
    ax.set(xlabel=r"Current assets $a$", ylabel=r"Optimal next assets $a'$",
           title="Aiyagari: optimizing savings policies")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "aiyagari-savings.svg", metadata={"Date": None})
    plt.close(fig)
    initial = np.zeros_like(mu)
    initial[0, :] = .5
    history = {0: initial.copy()}
    current = initial
    for t in range(1, 101):
        current = forward(current, *op, trans)
        if t in (5, 25, 100):
            history[t] = current.copy()
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for t in (0, 5, 25, 100):
        ax.plot(a, np.cumsum(history[t].sum(axis=1)), label=rf"$t={t}$")
    ax.plot(a, np.cumsum(mu.sum(axis=1)), "k--", label=r"Stationary $\mu^*$")
    ax.set(xlabel=r"Assets $a$", ylabel=r"Wealth cumulative distribution $F_t(a)$",
           title="Aiyagari: forward distribution at fixed equilibrium prices",
           ylim=(0, 1.02))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "aiyagari-distribution.svg", metadata={"Date": None})
    plt.close(fig)
    return {"r": float(r), "K_supply": k, "K_demand": float(kd),
            "wage": float(wage), "capital_error": float(k - kd),
            "mass_error": float(abs(mu.sum() - 1)),
            "upper_cap_stationary_mass":upper_mass, **diagnostics}


def ising_figure(out):
    n = 100
    k = np.arange(n + 1)
    spin_sum = 2 * k - n
    m = spin_sum / n
    log_comb = gammaln(n+1) - gammaln(k+1) - gammaln(n-k+1)
    modes = {}
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for coupling in (.7, 1.45):
        logp = log_comb + coupling * (spin_sum ** 2 - n) / (2 * (n-1))
        probabilities = np.exp(logp - logsumexp(logp))
        if abs(probabilities.sum() - 1) > 1e-12:
            raise RuntimeError("Ising partition function invalid")
        ax.plot(m, probabilities, label=rf"$J/\tau={coupling:.2f}$")
        modes[str(coupling)] = [float(x) for x in m[np.isclose(
            probabilities, probabilities.max(), rtol=1e-10, atol=0)]]
    ax.set(xlabel=r"Mean choice $m_N$", ylabel=r"Exact finite-$N$ probability",
           title=rf"Asynchronous logit equilibrium: $N={n}$, $h=0$")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "ising-finite-population.svg", metadata={"Date": None})
    plt.close(fig)
    # Direct detailed-balance check on all single-flip edges, N=7.
    n_small = 7
    states = np.array([[1 if i & (1 << j) else -1 for j in range(n_small)]
                       for i in range(1 << n_small)])
    s = states.sum(axis=1)
    phi = .7 * (s*s - n_small) / (2 * (n_small - 1))
    pi = np.exp(phi - logsumexp(phi))
    error = 0.
    for i in range(1 << n_small):
        for j in range(n_small):
            other = (s[i] - states[i,j])/(n_small - 1)
            forward_prob = 1/(1 + np.exp(2 * states[i,j] * .7 * other))
            reverse_prob = 1/(1 + np.exp(-2 * states[i,j] * .7 * other))
            error = max(error, abs(pi[i]*forward_prob/n_small -
                                   pi[i^(1<<j)]*reverse_prob/n_small))
    if error > 1e-11:
        raise RuntimeError("finite Ising detailed balance violation")
    return {"N": 100, "coupling_modes": modes,
            "finite_detailed_balance_max_error": float(error)}


def money_candidate(meeting_rate, assortativity):
    M, money_mean = 5, 2.
    beta, buyer_u, seller_cost = .96, 5., .15
    def generator(f):
        L = np.zeros((M+1, M+1))
        for m in range(M+1):
            upward = meeting_rate/2*sum(
                f[b]*(1 + assortativity*b*m/M**2) for b in range(1, M+1)) if m<M else 0
            downward = meeting_rate/2*sum(
                f[s]*(1 + assortativity*m*s/M**2) for s in range(M)) if m>0 else 0
            if m < M: L[m,m+1] = upward
            if m > 0: L[m,m-1] = downward
            L[m,m] = -upward-downward
        return L
    def residual(x):
        f = np.r_[x, 1-x.sum()]
        return np.r_[(generator(f).T @ f)[:M-1], f @ np.arange(M+1) - money_mean]
    sol = root(residual, np.ones(M)/(M+1), tol=1e-11)
    if not sol.success and np.max(abs(sol.fun)) > 1e-8:
        raise RuntimeError("money root failed")
    f = np.r_[sol.x, 1-sol.x.sum()]
    if f.min() < -1e-9:
        raise RuntimeError("negative money probability")
    f = np.maximum(f, 0)
    f /= f.sum()
    L = generator(f)
    utility = np.zeros(M+1)
    for m in range(M+1):
        if m>0:
            utility[m] += buyer_u*meeting_rate/2*sum(
                f[s]*(1 + assortativity*m*s/M**2) for s in range(M))
        if m<M:
            utility[m] -= seller_cost*meeting_rate/2*sum(
                f[b]*(1 + assortativity*b*m/M**2) for b in range(1,M+1))
    V = np.linalg.solve(np.eye(M+1)-beta*(np.eye(M+1)+L), utility)
    buyers = [buyer_u+beta*(V[b-1]-V[b]) for b in range(1,M+1)]
    sellers = [-seller_cost+beta*(V[s+1]-V[s]) for s in range(M)]
    error = float(np.max(abs(L.T@f)))
    P = np.eye(M+1)+L
    bellman = float(np.max(np.abs(V-utility-beta*P@V)))
    trans_mass = float(abs(np.sum(L.T@f)))
    trans_money = float(abs(np.arange(M+1)@(L.T@f)))
    transition_negative = float(max(0.,-np.min(P)))
    if (min(buyers+sellers)<-1e-8 or error>1e-8 or bellman>1e-9
        or trans_mass>1e-10 or trans_money>1e-10 or transition_negative>1e-12):
        raise RuntimeError("stationarity, Bellman, transition, or voluntary acceptance failed")
    return f, {"stationarity_sup":error, "buyer_min_gain":float(min(buyers)),
               "seller_min_gain":float(min(sellers)),
               "bellman_sup":bellman, "conservation_mass":trans_mass,
               "conservation_money":trans_money, "transition_row_sum_sup":
               float(np.max(abs(P.sum(axis=1)-1))),
               "transition_negative_part":transition_negative}


def monetary_figure(out):
    f0, d0 = money_candidate(.45, 0.)
    f1, d1 = money_candidate(.2, 3.)
    m = np.arange(6)
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.bar(m-.18, f0, width=.36, label="Uniform matching")
    ax.bar(m+.18, f1, width=.36, label="Assortative matching")
    ax.set_xticks(m)
    ax.set(xlabel=r"Token holdings $m$", ylabel=r"Stationary probability $f^*(m)$",
           title="Optimal voluntary service-for-token exchange")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "monetary-matching.svg", metadata={"Date": None})
    plt.close(fig)
    return {"uniform":{**d0,"distribution":f0.tolist()},
            "assortative":{**d1,"distribution":f1.tolist()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="lectures/economics-first/figures")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    results = {"aiyagari": aiyagari_figures(out),
               "ising": ising_figure(out),
               "monetary_matching": monetary_figure(out)}
    (out/"numerical-validation.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
